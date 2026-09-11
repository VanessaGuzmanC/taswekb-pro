"""Unit tests for Task 5.0 — Taskweb adapter interface (Feature 4 contract)."""

from datetime import datetime, timedelta

import pytest

from taskweb_pro.taskweb_adapter import (
    FakeTaskwebAdapter,
    TaskwebUnavailableError,
    UnavailableTaskwebAdapter,
)

CHILD_TASK_ID = 42


def test_unavailable_adapter_start_timer_fails_fast():
    adapter = UnavailableTaskwebAdapter()
    with pytest.raises(TaskwebUnavailableError):
        adapter.start_timer(CHILD_TASK_ID)


def test_unavailable_adapter_stop_timer_fails_fast():
    adapter = UnavailableTaskwebAdapter()
    with pytest.raises(TaskwebUnavailableError):
        adapter.stop_timer(CHILD_TASK_ID)


def test_unavailable_adapter_log_hours_fails_fast():
    adapter = UnavailableTaskwebAdapter()
    now = datetime.now()
    with pytest.raises(TaskwebUnavailableError):
        adapter.log_hours(CHILD_TASK_ID, now, now + timedelta(hours=1))


def test_fake_adapter_start_and_stop_timer_record_calls():
    adapter = FakeTaskwebAdapter()
    start_status = adapter.start_timer(CHILD_TASK_ID)
    stop_status = adapter.stop_timer(CHILD_TASK_ID)
    assert start_status.success is True
    assert stop_status.success is True
    assert adapter.calls == [
        ("start_timer", (CHILD_TASK_ID,)),
        ("stop_timer", (CHILD_TASK_ID,)),
    ]


def test_fake_adapter_log_hours_success():
    adapter = FakeTaskwebAdapter()
    start = datetime(2026, 9, 10, 10, 0)
    end = datetime(2026, 9, 10, 10, 15)
    status = adapter.log_hours(CHILD_TASK_ID, start, end)
    assert status.success is True
    assert adapter.calls == [("log_hours", (CHILD_TASK_ID, start, end))]


def test_fake_adapter_log_hours_rejects_end_before_start():
    adapter = FakeTaskwebAdapter()
    start = datetime(2026, 9, 10, 10, 15)
    end = datetime(2026, 9, 10, 10, 0)
    status = adapter.log_hours(CHILD_TASK_ID, start, end)
    assert status.success is False
    assert adapter.calls == []
