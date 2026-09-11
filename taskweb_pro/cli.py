"""Command-line entry point for the TaskWeb PRO product.

Exposes the pure decision logic in this package to the Claude Code
skills that orchestrate it (`.claude/skills/taskweb-pro-azure-integration/`
and `.claude/skills/taskweb-pro-text-interpretation/`), which invoke it
via Bash and perform the actual Azure DevOps / Taskweb MCP tool calls
themselves — see tasks/prd-integracao-azure-taskweb/techspec.md ->
System Architecture for why this module never calls MCP directly.

Every subcommand prints a single JSON object to stdout and exits 0 on
success. On a business-rule violation (e.g. an ambiguous child task,
or Taskweb being unavailable) it prints
`{"error": "<message>", "error_type": "<ClassName>"}` and exits 1 —
never a Python traceback, so the invoking skill can always parse the
result.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime

from taskweb_pro.azure_task_resolver import (
    AmbiguousChildTaskError,
    InvalidParentTaskError,
    UnknownActivityError,
    activity_to_work_type,
    build_activity_update,
    build_assignment_update,
    build_child_task_item,
    build_children_wiql,
    find_compatible_child,
    needs_assignment,
    should_create_child,
    validate_parent_type,
    work_type_to_activity,
)
from taskweb_pro.activity_classification import classify_work_type
from taskweb_pro.models import ActionStatus, ChildTask
from taskweb_pro.taskweb_adapter import TaskwebUnavailableError, UnavailableTaskwebAdapter
from taskweb_pro.time_parsing import parse_time_range


def _child_from_dict(data: dict) -> ChildTask:
    return ChildTask(**data)


def _print_ok(payload: dict) -> None:
    print(json.dumps(payload))


def _print_error(exc: Exception) -> None:
    print(json.dumps({"error": str(exc), "error_type": type(exc).__name__}))


def cmd_validate_parent_type(args: argparse.Namespace) -> int:
    try:
        validate_parent_type(args.work_item_type)
    except InvalidParentTaskError as exc:
        _print_error(exc)
        return 1
    _print_ok({"valid": True})
    return 0


def cmd_build_children_wiql(args: argparse.Namespace) -> int:
    wiql = build_children_wiql(args.parent_id)
    _print_ok({"wiql": wiql})
    return 0


def cmd_find_compatible_child(args: argparse.Namespace) -> int:
    children = [_child_from_dict(c) for c in json.loads(args.children_json)]
    try:
        match = find_compatible_child(children, args.work_type, args.user)
    except (AmbiguousChildTaskError, ValueError) as exc:
        _print_error(exc)
        return 1
    _print_ok({"match": asdict(match) if match else None})
    return 0


def cmd_should_create_child(args: argparse.Namespace) -> int:
    if args.existing_json is None:
        parsed = None
    else:
        parsed = json.loads(args.existing_json)
    existing = _child_from_dict(parsed) if parsed is not None else None
    _print_ok({"should_create": should_create_child(existing)})
    return 0


def cmd_build_child_task_item(args: argparse.Namespace) -> int:
    try:
        item = build_child_task_item(args.parent_title, args.description or "")
    except ValueError as exc:
        _print_error(exc)
        return 1
    _print_ok(item)
    return 0


def cmd_needs_assignment(args: argparse.Namespace) -> int:
    child = _child_from_dict(json.loads(args.child_json))
    _print_ok({"needs_assignment": needs_assignment(child, args.user)})
    return 0


def cmd_build_assignment_update(args: argparse.Namespace) -> int:
    _print_ok(build_assignment_update(args.user))
    return 0


def cmd_build_activity_update(args: argparse.Namespace) -> int:
    try:
        update = build_activity_update(args.work_type)
    except ValueError as exc:
        _print_error(exc)
        return 1
    _print_ok(update)
    return 0


def cmd_activity_to_work_type(args: argparse.Namespace) -> int:
    try:
        work_type = activity_to_work_type(args.activity)
    except UnknownActivityError as exc:
        _print_error(exc)
        return 1
    _print_ok({"work_type": work_type})
    return 0


def cmd_work_type_to_activity(args: argparse.Namespace) -> int:
    try:
        activity = work_type_to_activity(args.work_type)
    except ValueError as exc:
        _print_error(exc)
        return 1
    _print_ok({"activity": activity})
    return 0


def _handle_action_status(status: ActionStatus) -> int:
    """Apply the CLI's success/error contract to a `TaskwebAdapter` result.

    An adapter is free to signal failure either by raising (as
    `UnavailableTaskwebAdapter` does) or by returning
    `ActionStatus(success=False, ...)` (as `FakeTaskwebAdapter.log_hours`
    does for an invalid interval) — both must exit 1 with the
    documented error shape, never exit 0 with a false-success payload.
    """
    if not status.success:
        print(json.dumps({"error": status.message, "error_type": "ActionFailure"}))
        return 1
    payload = asdict(status)
    payload["timestamp"] = status.timestamp.isoformat()
    _print_ok(payload)
    return 0


def cmd_parse_time_range(args: argparse.Namespace) -> int:
    try:
        start_dt, end_dt = parse_time_range(
            args.start, args.end, args.duration_minutes, datetime.now()
        )
    except (ValueError, TypeError) as exc:
        _print_error(exc)
        return 1
    _print_ok({"start": start_dt.isoformat(), "end": end_dt.isoformat()})
    return 0


def cmd_classify_work_type(args: argparse.Namespace) -> int:
    try:
        work_type = classify_work_type(args.hint)
    except ValueError as exc:
        _print_error(exc)
        return 1
    _print_ok({"work_type": work_type})
    return 0


def cmd_taskweb_start_timer(args: argparse.Namespace) -> int:
    try:
        status = UnavailableTaskwebAdapter().start_timer(args.child_task_id)
    except TaskwebUnavailableError as exc:
        _print_error(exc)
        return 1
    return _handle_action_status(status)  # pragma: no cover — unreachable until taskweb-mcp connects


def cmd_taskweb_stop_timer(args: argparse.Namespace) -> int:
    try:
        status = UnavailableTaskwebAdapter().stop_timer(args.child_task_id)
    except TaskwebUnavailableError as exc:
        _print_error(exc)
        return 1
    return _handle_action_status(status)  # pragma: no cover — unreachable until taskweb-mcp connects


def cmd_taskweb_log_hours(args: argparse.Namespace) -> int:
    try:
        status = UnavailableTaskwebAdapter().log_hours(
            args.child_task_id,
            datetime.fromisoformat(args.start),
            datetime.fromisoformat(args.end),
        )
    except TaskwebUnavailableError as exc:
        _print_error(exc)
        return 1
    return _handle_action_status(status)  # pragma: no cover — unreachable until taskweb-mcp connects


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m taskweb_pro.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate-parent-type")
    p.add_argument("--work-item-type", required=True)
    p.set_defaults(func=cmd_validate_parent_type)

    p = sub.add_parser("build-children-wiql")
    p.add_argument("--parent-id", required=True, type=int)
    p.set_defaults(func=cmd_build_children_wiql)

    p = sub.add_parser("find-compatible-child")
    p.add_argument("--children-json", required=True)
    p.add_argument("--work-type", required=True)
    p.add_argument("--user", required=True)
    p.set_defaults(func=cmd_find_compatible_child)

    p = sub.add_parser("should-create-child")
    p.add_argument("--existing-json", default=None)
    p.set_defaults(func=cmd_should_create_child)

    p = sub.add_parser("build-child-task-item")
    p.add_argument("--parent-title", required=True)
    p.add_argument("--description", default=None)
    p.set_defaults(func=cmd_build_child_task_item)

    p = sub.add_parser("needs-assignment")
    p.add_argument("--child-json", required=True)
    p.add_argument("--user", required=True)
    p.set_defaults(func=cmd_needs_assignment)

    p = sub.add_parser("build-assignment-update")
    p.add_argument("--user", required=True)
    p.set_defaults(func=cmd_build_assignment_update)

    p = sub.add_parser("build-activity-update")
    p.add_argument("--work-type", required=True)
    p.set_defaults(func=cmd_build_activity_update)

    p = sub.add_parser("activity-to-work-type")
    p.add_argument("--activity", required=True)
    p.set_defaults(func=cmd_activity_to_work_type)

    p = sub.add_parser("work-type-to-activity")
    p.add_argument("--work-type", required=True)
    p.set_defaults(func=cmd_work_type_to_activity)

    p = sub.add_parser("parse-time-range")
    p.add_argument("--start", default=None, help="HH:MM, 24h")
    p.add_argument("--end", default=None, help="HH:MM, 24h")
    p.add_argument("--duration-minutes", default=None, type=int)
    p.set_defaults(func=cmd_parse_time_range)

    p = sub.add_parser("classify-work-type")
    p.add_argument("--hint", default=None)
    p.set_defaults(func=cmd_classify_work_type)

    p = sub.add_parser("taskweb-start-timer")
    p.add_argument("--child-task-id", required=True, type=int)
    p.set_defaults(func=cmd_taskweb_start_timer)

    p = sub.add_parser("taskweb-stop-timer")
    p.add_argument("--child-task-id", required=True, type=int)
    p.set_defaults(func=cmd_taskweb_stop_timer)

    p = sub.add_parser("taskweb-log-hours")
    p.add_argument("--child-task-id", required=True, type=int)
    p.add_argument("--start", required=True, help="ISO 8601 datetime")
    p.add_argument("--end", required=True, help="ISO 8601 datetime")
    p.set_defaults(func=cmd_taskweb_log_hours)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        # Last-resort safety net: the module contract (see docstring
        # above) guarantees every subcommand prints the JSON error
        # shape and exits 1, never a raw traceback — this also covers
        # malformed --*-json input (json.JSONDecodeError, or a
        # TypeError from ChildTask(**data) with a missing/unexpected
        # key) that individual cmd_* handlers do not catch themselves.
        _print_error(exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
