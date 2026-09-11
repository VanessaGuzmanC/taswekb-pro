"""Unit tests for Task 2.0 — Azure query & child-task compatibility resolver."""

import pytest

from taskweb_pro.azure_task_resolver import (
    AmbiguousChildTaskError,
    InvalidParentTaskError,
    _identities_match,
    _normalize_identity,
    build_children_wiql,
    find_compatible_child,
    validate_parent_type,
)
from taskweb_pro.models import ChildTask

PARENT_ID = 12345


def make_child(id: int, work_type: str, assigned_to: str | None) -> ChildTask:
    return ChildTask(
        id=id,
        parent_id=PARENT_ID,
        work_type=work_type,
        assigned_to=assigned_to,
        taskweb_visible=True,
    )


# -- validate_parent_type ----------------------------------------------------


@pytest.mark.parametrize("work_item_type", ["Product Backlog Item", "Bug"])
def test_validate_parent_type_accepts_default_valid_types(work_item_type):
    validate_parent_type(work_item_type)  # must not raise


def test_validate_parent_type_rejects_invalid_type():
    with pytest.raises(InvalidParentTaskError):
        validate_parent_type("Task")


def test_validate_parent_type_respects_custom_valid_set():
    validate_parent_type("Epic", valid_parent_types=frozenset({"Epic"}))


# -- build_children_wiql ------------------------------------------------------


def test_build_children_wiql_contains_parent_id():
    wiql = build_children_wiql(PARENT_ID)
    assert str(PARENT_ID) in wiql
    assert "System.Parent" in wiql


def test_build_children_wiql_rejects_non_int_parent_id():
    with pytest.raises(TypeError):
        build_children_wiql("12345; DROP TABLE WorkItems")


def test_build_children_wiql_rejects_bool_parent_id():
    with pytest.raises(TypeError):
        build_children_wiql(True)


# -- find_compatible_child ----------------------------------------------------


def test_find_compatible_child_returns_match():
    children = [
        make_child(1, "development", "alice"),
        make_child(2, "test", "alice"),
    ]
    result = find_compatible_child(children, "development", "alice")
    assert result is not None
    assert result.id == 1


def test_find_compatible_child_returns_none_when_no_match():
    children = [make_child(1, "development", "bob")]
    result = find_compatible_child(children, "development", "alice")
    assert result is None


def test_find_compatible_child_returns_none_for_empty_list():
    assert find_compatible_child([], "development", "alice") is None


def test_find_compatible_child_raises_on_multiple_matches():
    children = [
        make_child(1, "development", "alice"),
        make_child(2, "development", "alice"),
    ]
    with pytest.raises(AmbiguousChildTaskError):
        find_compatible_child(children, "development", "alice")


def test_find_compatible_child_requires_exact_assignee_and_type_match():
    children = [
        make_child(1, "test", "alice"),
        make_child(2, "development", "bob"),
    ]
    assert find_compatible_child(children, "development", "alice") is None


# -- identity normalization (code-review finding: "Display Name <email>" shape) --


def test_normalize_identity_extracts_bracketed_email():
    assert _normalize_identity("Alice Wonderland <alice@db1.com.br>") == "alice@db1.com.br"


def test_normalize_identity_passes_through_plain_value():
    assert _normalize_identity("alice@db1.com.br") == "alice@db1.com.br"


def test_normalize_identity_is_case_insensitive():
    assert _normalize_identity("Alice@DB1.com.br") == "alice@db1.com.br"


def test_normalize_identity_none_stays_none():
    assert _normalize_identity(None) is None


def test_identities_match_display_name_vs_plain_email():
    assert _identities_match("Alice Wonderland <alice@db1.com.br>", "alice@db1.com.br")


def test_identities_match_rejects_different_identities():
    assert not _identities_match("Bob Builder <bob@db1.com.br>", "alice@db1.com.br")


def test_find_compatible_child_matches_display_name_format():
    """Regression test for the code-review finding: Azure's System.AssignedTo
    is commonly "Display Name <email>", not the bare email `user` is given
    as — without normalization this always looked unassigned, causing
    ensure-child-task to duplicate the child task on every run."""
    children = [make_child(1, "development", "Alice Wonderland <alice@db1.com.br>")]
    result = find_compatible_child(children, "development", "alice@db1.com.br")
    assert result is not None
    assert result.id == 1
