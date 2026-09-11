"""Unit tests for Task 4.0 — automatic child task assignment (Feature 3)."""

from taskweb_pro.azure_task_resolver import build_assignment_update, needs_assignment
from taskweb_pro.models import ChildTask


def make_child(assigned_to: str | None) -> ChildTask:
    return ChildTask(
        id=1, parent_id=99, work_type="development", assigned_to=assigned_to, taskweb_visible=True
    )


def test_needs_assignment_true_when_unassigned():
    assert needs_assignment(make_child(None), "alice") is True


def test_needs_assignment_true_when_assigned_to_someone_else():
    assert needs_assignment(make_child("bob"), "alice") is True


def test_needs_assignment_false_when_already_correct():
    assert needs_assignment(make_child("alice"), "alice") is False


def test_needs_assignment_false_when_already_correct_display_name_format():
    """Regression test for the code-review finding: without normalizing
    Azure's "Display Name <email>" identity format, this always returned
    True, causing a redundant assignment write on every run."""
    child = make_child("Alice Wonderland <alice@db1.com.br>")
    assert needs_assignment(child, "alice@db1.com.br") is False


def test_build_assignment_update_shape():
    update = build_assignment_update("alice")
    assert update == {"op": "add", "path": "/fields/System.AssignedTo", "value": "alice"}
