"""Integration tests for Task 3.0 — timer-control CLI subcommands.

Exercises `taskweb_pro.cli.main` directly, the seam the orchestrating
skill invokes via Bash, with the active-timer state file redirected to
a temp path per test (no shared state across tests, no touching the
real `~/.taskweb_pro/active_timer.json`).
"""

import json

import pytest

import taskweb_pro.timer_state as timer_state
from taskweb_pro.cli import main


@pytest.fixture(autouse=True)
def isolated_state_path(tmp_path, monkeypatch):
    monkeypatch.setattr(timer_state, "DEFAULT_STATE_PATH", tmp_path / "active_timer.json")


def run_cli(capsys, argv: list[str]) -> tuple[int, dict]:
    exit_code = main(argv)
    output = json.loads(capsys.readouterr().out)
    return exit_code, output


def test_get_active_when_none_tracked(capsys):
    code, out = run_cli(capsys, ["timer-get-active"])
    assert code == 0
    assert out == {"active": None}


def test_save_then_get_active(capsys):
    code, _ = run_cli(
        capsys,
        [
            "timer-save-active",
            "--child-task-id", "42",
            "--parent-id", "100",
            "--work-type", "development",
            "--user", "alice",
        ],
    )
    assert code == 0

    code, out = run_cli(capsys, ["timer-get-active"])
    assert code == 0
    assert out["active"]["child_task_id"] == 42
    assert out["active"]["parent_id"] == 100
    assert out["active"]["work_type"] == "development"
    assert out["active"]["user"] == "alice"
    assert "started_at" in out["active"]


def test_check_conflict_no_active_timer(capsys):
    code, out = run_cli(capsys, ["timer-check-conflict", "--requested-child-task-id", "42"])
    assert code == 0
    assert out == {"conflict": False, "active": None}


def test_check_conflict_same_child_task(capsys):
    run_cli(
        capsys,
        [
            "timer-save-active",
            "--child-task-id", "42",
            "--parent-id", "100",
            "--work-type", "development",
            "--user", "alice",
        ],
    )
    code, out = run_cli(capsys, ["timer-check-conflict", "--requested-child-task-id", "42"])
    assert code == 0
    assert out["conflict"] is False


def test_check_conflict_different_child_task(capsys):
    run_cli(
        capsys,
        [
            "timer-save-active",
            "--child-task-id", "42",
            "--parent-id", "100",
            "--work-type", "development",
            "--user", "alice",
        ],
    )
    code, out = run_cli(capsys, ["timer-check-conflict", "--requested-child-task-id", "99"])
    assert code == 0
    assert out["conflict"] is True
    assert out["active"]["child_task_id"] == 42


def test_resolve_stop_target_falls_back_to_active(capsys):
    run_cli(
        capsys,
        [
            "timer-save-active",
            "--child-task-id", "42",
            "--parent-id", "100",
            "--work-type", "development",
            "--user", "alice",
        ],
    )
    code, out = run_cli(capsys, ["timer-resolve-stop-target"])
    assert code == 0
    assert out == {"child_task_id": 42}


def test_resolve_stop_target_uses_explicit_reference(capsys):
    run_cli(
        capsys,
        [
            "timer-save-active",
            "--child-task-id", "42",
            "--parent-id", "100",
            "--work-type", "development",
            "--user", "alice",
        ],
    )
    code, out = run_cli(
        capsys, ["timer-resolve-stop-target", "--requested-child-task-id", "99"]
    )
    assert code == 0
    assert out == {"child_task_id": 99}


def test_resolve_stop_target_no_active_no_reference_errors(capsys):
    code, out = run_cli(capsys, ["timer-resolve-stop-target"])
    assert code == 1
    assert out["error_type"] == "NoActiveTimerError"


def test_clear_active_removes_tracking(capsys):
    run_cli(
        capsys,
        [
            "timer-save-active",
            "--child-task-id", "42",
            "--parent-id", "100",
            "--work-type", "development",
            "--user", "alice",
        ],
    )
    code, out = run_cli(capsys, ["timer-clear-active"])
    assert code == 0
    assert out == {"cleared": True}

    code, out = run_cli(capsys, ["timer-get-active"])
    assert out == {"active": None}


def test_clear_active_when_nothing_tracked(capsys):
    code, out = run_cli(capsys, ["timer-clear-active"])
    assert code == 0
    assert out == {"cleared": True}
