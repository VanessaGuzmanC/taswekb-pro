"""Azure DevOps child-task query, compatibility and write logic.

Feature 1 (query & compatibility) is implemented here — see
tasks/prd-integracao-azure-taskweb/2_task.md. Creation (Task 3.0) and
assignment (Task 4.0) extend this module without duplicating this
logic.

This module is pure: it never calls Azure DevOps itself. The
orchestrating skill (Task 6.0) executes the MCP tool calls
(`wit_query`, `wit_work_item`) and passes their results in.
"""

from __future__ import annotations

import logging
import re

from taskweb_pro.models import ChildTask, WorkType

logger = logging.getLogger(__name__)

# Azure DevOps identity-reference fields (e.g. `System.AssignedTo`) are
# commonly rendered as "Display Name <email>" rather than the bare
# email/uniqueName. Comparing that raw string against a plain `user`
# value (e.g. "alice@db1.com.br") with `==` would never match, causing
# every existing assignment to look unassigned — silently duplicating
# child tasks (PRD 2.4) and forcing redundant assignment writes on
# every run. This regex extracts the bracketed identity when present.
#
# ASSUMPTION, not yet verified against this project's real Azure
# DevOps API responses (no sandbox provisioned yet — see Known Risks
# in techspec.md): covers the common "Display Name <email>" string
# shape. Does NOT cover an identity returned as a structured object
# (e.g. {"displayName":..., "uniqueName":...}) — if the MCP tools
# return that shape instead, the caller must extract the
# email/uniqueName field itself before building ChildTask.assigned_to,
# since this function only operates on strings.
_IDENTITY_EMAIL_RE = re.compile(r"<([^<>]+)>\s*$")


def _normalize_identity(raw: str | None) -> str | None:
    """Best-effort normalization of an Azure DevOps identity string for comparison.

    Extracts the bracketed email from "Display Name <email>" when
    present, otherwise returns the value unchanged; case-folds either
    way so comparison is not sensitive to email casing.
    """
    if raw is None:
        return None
    match = _IDENTITY_EMAIL_RE.search(raw)
    normalized = match.group(1) if match else raw
    return normalized.strip().casefold()


def _identities_match(a: str | None, b: str | None) -> bool:
    """Compare two identity strings after `_normalize_identity`, not by raw equality."""
    return _normalize_identity(a) == _normalize_identity(b)

# Scrum process template's hierarchy-1 types (confirmed via web search
# during techspec drafting). "Bug hom" / "Bug client" from
# overview/glossary_context.md.md are business sub-classifications of
# "Bug", not distinct Azure DevOps work item types, so they are not
# listed separately here. Override if this project's process template
# differs.
DEFAULT_VALID_PARENT_TYPES: frozenset[str] = frozenset({"Product Backlog Item", "Bug"})

# Maps our internal work-type classification to the Azure DevOps Task
# work item's `Microsoft.VSTS.Common.Activity` field — a standard
# (suggested-value, not enforced) field in the Scrum process template,
# confirmed via web search during implementation. This is how a child
# task's work_type is actually persisted in Azure: `add_child` cannot
# set it at creation time (its `items` schema only accepts
# title/description/areaPath/iterationPath/format), so it must be set
# via a follow-up `update` call — see build_activity_update below and
# references/orchestrate.md.
WORK_TYPE_TO_ACTIVITY: dict[WorkType, str] = {
    "development": "Development",
    "test": "Testing",
    "business_analysis": "Requirements",
}
ACTIVITY_TO_WORK_TYPE: dict[str, WorkType] = {v: k for k, v in WORK_TYPE_TO_ACTIVITY.items()}


class InvalidParentTaskError(ValueError):
    """Raised when a work item is not a valid parent type for this flow (PRD 1.4)."""


class AmbiguousChildTaskError(RuntimeError):
    """Raised when more than one compatible child task exists for the same user + work type.

    Per overview/glossary_context.md.md, at most one compatible child
    task should exist at a time; more than one is a data anomaly that
    must be surfaced, never silently resolved by picking one.
    """


class UnknownActivityError(ValueError):
    """Raised when an Azure DevOps Activity value doesn't map to a known work_type.

    The Activity field is a suggested-value field, not an enforced
    one — a work item could carry a value this flow never wrote (e.g.
    "Design", "Deployment"). Such a child task cannot be evaluated for
    compatibility and must be surfaced, not silently skipped or
    mis-typed.
    """


def work_type_to_activity(work_type: WorkType) -> str:
    """Map a work_type to the Azure DevOps `Microsoft.VSTS.Common.Activity` value to write."""
    try:
        return WORK_TYPE_TO_ACTIVITY[work_type]
    except KeyError as exc:
        raise ValueError(f"Unknown work_type {work_type!r}") from exc


def activity_to_work_type(activity: str) -> WorkType:
    """Inverse of `work_type_to_activity`, for interpreting a fetched child task."""
    try:
        return ACTIVITY_TO_WORK_TYPE[activity]
    except KeyError as exc:
        raise UnknownActivityError(
            f"Activity {activity!r} does not map to a known work_type; "
            f"expected one of {sorted(ACTIVITY_TO_WORK_TYPE)}"
        ) from exc


def validate_parent_type(
    work_item_type: str,
    valid_parent_types: frozenset[str] = DEFAULT_VALID_PARENT_TYPES,
) -> None:
    """Validate that a fetched work item is an allowed parent type (PRD 1.4).

    `valid_parent_types` defaults to `DEFAULT_VALID_PARENT_TYPES`;
    override if the project uses a different process template.
    """
    if work_item_type not in valid_parent_types:
        logger.warning("rejected parent work item type=%r", work_item_type)
        raise InvalidParentTaskError(
            f"Work item type {work_item_type!r} is not a valid parent task; "
            f"expected one of {sorted(valid_parent_types)}"
        )
    logger.info("accepted parent work item type=%r", work_item_type)


def build_children_wiql(parent_id: int) -> str:
    """Build the WIQL query to fetch all child work items of `parent_id`.

    Intended to be run via `mcp__azure-devops__wit_query` (action
    `wiql`); see techspec.md -> Integration Points.
    """
    if not isinstance(parent_id, int) or isinstance(parent_id, bool):
        raise TypeError(f"parent_id must be an int, got {parent_id!r}")
    return f"SELECT [System.Id] FROM WorkItems WHERE [System.Parent] = {parent_id}"


def find_compatible_child(
    children: list[ChildTask], work_type: WorkType, user: str
) -> ChildTask | None:
    """Return the single child task compatible with `work_type` and `user`, or None.

    Compatibility requires both an exact work-type match and an exact
    assignee match (PRD 1.3). Raises `AmbiguousChildTaskError` if more
    than one candidate matches, per the uniqueness rule in
    overview/glossary_context.md.md.
    """
    if work_type not in WORK_TYPE_TO_ACTIVITY:
        raise ValueError(f"Unknown work_type {work_type!r}")
    matches = [
        child
        for child in children
        if child.work_type == work_type and _identities_match(child.assigned_to, user)
    ]
    if len(matches) > 1:
        logger.error(
            "ambiguous child tasks for user=%r work_type=%r: ids=%s",
            user,
            work_type,
            [m.id for m in matches],
        )
        raise AmbiguousChildTaskError(
            f"Found {len(matches)} compatible child tasks for user={user!r}, "
            f"work_type={work_type!r}: {[m.id for m in matches]}"
        )
    result = matches[0] if matches else None
    logger.info(
        "compatibility check for user=%r work_type=%r -> %s",
        user,
        work_type,
        result.id if result else "no match",
    )
    return result


# -- Task 3.0: child task creation (Feature 2) -------------------------------


def should_create_child(existing_match: ChildTask | None) -> bool:
    """Return True only when no compatible child task already exists (PRD 2.1, 2.4).

    The caller (orchestrating skill) must call this a second time
    immediately before creating, against a freshly re-queried
    `existing_match`, to guard against a duplicate created between the
    first check and the write (PRD 2.4).
    """
    decision = existing_match is None
    logger.info(
        "create decision: %s (existing_match=%s)",
        decision,
        existing_match.id if existing_match else None,
    )
    return decision


def build_child_task_item(parent_title: str, description: str = "") -> dict[str, str]:
    """Build one `items` entry for `wit_work_item_write` action `add_child`.

    The child task title matches the parent's title verbatim (PRD
    2.2). Linking to the parent is handled by the `add_child` action
    itself, so no separate `wit_work_item_link_write` call is needed
    (see techspec.md -> Technical Considerations -> Main Decisions).
    """
    if not parent_title:
        raise ValueError("parent_title must not be empty")
    logger.info("built child task item for title=%r", parent_title)
    return {"title": parent_title, "description": description}


# -- Task 4.0: automatic child task assignment (Feature 3) -------------------


def needs_assignment(child: ChildTask, user: str) -> bool:
    """Return True when `child` is not yet assigned to `user` (PRD 3.1)."""
    result = not _identities_match(child.assigned_to, user)
    logger.info("assignment check for child_task_id=%s -> needs_assignment=%s", child.id, result)
    return result


def build_assignment_update(user: str) -> dict[str, str]:
    """Build one `updates` entry for `wit_work_item_write` action `update`.

    Sets `System.AssignedTo`; PRD 3.2 makes this a precondition for the
    child task to become usable in Taskweb.
    """
    return {"op": "add", "path": "/fields/System.AssignedTo", "value": user}


def build_activity_update(work_type: WorkType) -> dict[str, str]:
    """Build one `updates` entry for `wit_work_item_write` action `update`.

    Sets `Microsoft.VSTS.Common.Activity` on a newly created child
    task so its work_type classification is actually persisted in
    Azure (PRD 2.2/2.3's "the child task has a type compatible with
    the work"). Must run as a follow-up `update` after `add_child`,
    since that action's `items` schema cannot set this field —
    see references/orchestrate.md.
    """
    return {
        "op": "add",
        "path": "/fields/Microsoft.VSTS.Common.Activity",
        "value": work_type_to_activity(work_type),
    }
