"""Unit tests for Task 7.0 — local observability.

Asserts a log line is emitted at each major decision point, and that
no log message contains anything resembling a secret/token.
"""

import logging

from taskweb_pro.azure_task_resolver import (
    build_child_task_item,
    find_compatible_child,
    needs_assignment,
    should_create_child,
    validate_parent_type,
)
from taskweb_pro.models import ChildTask
from taskweb_pro.taskweb_adapter import FakeTaskwebAdapter, TaskwebUnavailableError, UnavailableTaskwebAdapter

FORBIDDEN_SUBSTRINGS = ("token", "password", "secret", "AZURE_DEVOPS_PAT")


def _assert_no_secrets(records: list[logging.LogRecord]) -> None:
    for record in records:
        message = record.getMessage().lower()
        for forbidden in FORBIDDEN_SUBSTRINGS:
            assert forbidden.lower() not in message


def test_validate_parent_type_logs_decision(caplog):
    with caplog.at_level(logging.INFO, logger="taskweb_pro.azure_task_resolver"):
        validate_parent_type("Bug")
    assert any("accepted parent work item type" in r.message for r in caplog.records)
    _assert_no_secrets(caplog.records)


def test_find_compatible_child_logs_decision(caplog):
    child = ChildTask(id=1, parent_id=99, work_type="development", assigned_to="alice", taskweb_visible=True)
    with caplog.at_level(logging.INFO, logger="taskweb_pro.azure_task_resolver"):
        find_compatible_child([child], "development", "alice")
    assert any("compatibility check" in r.message for r in caplog.records)
    _assert_no_secrets(caplog.records)


def test_should_create_child_logs_decision(caplog):
    with caplog.at_level(logging.INFO, logger="taskweb_pro.azure_task_resolver"):
        should_create_child(None)
    assert any("create decision" in r.message for r in caplog.records)


def test_build_child_task_item_logs(caplog):
    with caplog.at_level(logging.INFO, logger="taskweb_pro.azure_task_resolver"):
        build_child_task_item("Some Title")
    assert any("built child task item" in r.message for r in caplog.records)


def test_needs_assignment_logs_decision(caplog):
    child = ChildTask(id=1, parent_id=99, work_type="development", assigned_to=None, taskweb_visible=False)
    with caplog.at_level(logging.INFO, logger="taskweb_pro.azure_task_resolver"):
        needs_assignment(child, "alice")
    assert any("assignment check" in r.message for r in caplog.records)


def test_taskweb_unavailable_logs_warning(caplog):
    with caplog.at_level(logging.WARNING, logger="taskweb_pro.taskweb_adapter"):
        try:
            UnavailableTaskwebAdapter().start_timer(1)
        except TaskwebUnavailableError:
            pass
    assert any("backend unavailable" in r.message for r in caplog.records)
    _assert_no_secrets(caplog.records)


def test_fake_adapter_logs_success(caplog):
    with caplog.at_level(logging.INFO, logger="taskweb_pro.taskweb_adapter"):
        FakeTaskwebAdapter().start_timer(1)
    assert any("success" in r.message for r in caplog.records)
