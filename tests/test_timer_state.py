"""Unit tests for Tasks 1.0/2.0 — active-timer decision logic and persistence."""

import logging
from datetime import datetime

import pytest

from taskweb_pro.models import ActiveTimer
from taskweb_pro.timer_state import (
    NoActiveTimerError,
    clear_active_timer,
    has_conflicting_timer,
    load_active_timer,
    resolve_stop_target,
    save_active_timer,
)

STARTED_AT = datetime(2026, 9, 10, 15, 30)


def _timer(child_task_id: int = 1) -> ActiveTimer:
    return ActiveTimer(
        child_task_id=child_task_id,
        parent_id=100,
        work_type="development",
        user="alice",
        started_at=STARTED_AT,
    )


# -- has_conflicting_timer ----------------------------------------------------


def test_no_active_timer_is_not_a_conflict():
    assert has_conflicting_timer(None, requested_child_task_id=1) is False


def test_active_timer_for_same_child_is_not_a_conflict():
    assert has_conflicting_timer(_timer(child_task_id=1), requested_child_task_id=1) is False


def test_active_timer_for_different_child_is_a_conflict():
    assert has_conflicting_timer(_timer(child_task_id=1), requested_child_task_id=2) is True


# -- resolve_stop_target -------------------------------------------------------


def test_stop_target_falls_back_to_active_when_no_reference_given():
    assert resolve_stop_target(_timer(child_task_id=1), requested_child_task_id=None) == 1


def test_stop_target_uses_matching_explicit_reference():
    assert resolve_stop_target(_timer(child_task_id=1), requested_child_task_id=1) == 1


def test_explicit_reference_wins_over_a_different_active_timer():
    assert resolve_stop_target(_timer(child_task_id=1), requested_child_task_id=2) == 2


def test_explicit_reference_used_when_no_active_timer():
    assert resolve_stop_target(None, requested_child_task_id=2) == 2


def test_no_active_and_no_reference_raises():
    with pytest.raises(NoActiveTimerError):
        resolve_stop_target(None, requested_child_task_id=None)


# -- persistence ---------------------------------------------------------------


def test_save_then_load_round_trip(tmp_path):
    path = tmp_path / "active_timer.json"
    save_active_timer(_timer(child_task_id=42), path=path)
    loaded = load_active_timer(path=path)
    assert loaded == _timer(child_task_id=42)


def test_load_missing_file_returns_none(tmp_path):
    path = tmp_path / "does_not_exist.json"
    assert load_active_timer(path=path) is None


def test_load_corrupted_file_returns_none_and_logs_warning(tmp_path, caplog):
    path = tmp_path / "active_timer.json"
    path.write_text("not valid json")
    with caplog.at_level(logging.WARNING, logger="taskweb_pro.timer_state"):
        assert load_active_timer(path=path) is None
    assert any("corrupted" in record.message for record in caplog.records)


def test_clear_removes_existing_file(tmp_path):
    path = tmp_path / "active_timer.json"
    save_active_timer(_timer(), path=path)
    clear_active_timer(path=path)
    assert not path.exists()


def test_clear_is_a_noop_when_already_absent(tmp_path):
    path = tmp_path / "does_not_exist.json"
    clear_active_timer(path=path)  # must not raise
    assert not path.exists()


def test_save_leaves_no_stray_temp_file(tmp_path):
    path = tmp_path / "active_timer.json"
    save_active_timer(_timer(), path=path)
    assert list(tmp_path.iterdir()) == [path]


def test_save_creates_parent_directory(tmp_path):
    path = tmp_path / "nested" / "dir" / "active_timer.json"
    save_active_timer(_timer(), path=path)
    assert path.exists()
