"""Unit/integration tests for Task 6.0 — skill orchestration end-to-end.

Exercises `taskweb_pro.cli.main`, the seam the orchestrating skill
invokes via Bash, with the underlying Azure/Taskweb calls mocked out
(no live credentials required), per techspec.md -> Testing Approach.
"""

import json
from datetime import datetime

import pytest

from taskweb_pro.cli import _handle_action_status, main
from taskweb_pro.models import ActionStatus

PARENT_TITLE = "PBI 1234112: Registrar horas"


def run_cli(capsys, argv: list[str]) -> tuple[int, dict]:
    exit_code = main(argv)
    output = json.loads(capsys.readouterr().out)
    return exit_code, output


def test_validate_parent_type_valid(capsys):
    code, out = run_cli(capsys, ["validate-parent-type", "--work-item-type", "Bug"])
    assert code == 0
    assert out == {"valid": True}


def test_validate_parent_type_invalid(capsys):
    code, out = run_cli(capsys, ["validate-parent-type", "--work-item-type", "Task"])
    assert code == 1
    assert out["error_type"] == "InvalidParentTaskError"


def test_build_children_wiql(capsys):
    code, out = run_cli(capsys, ["build-children-wiql", "--parent-id", "12345"])
    assert code == 0
    assert "12345" in out["wiql"]


def test_find_compatible_child_match(capsys):
    children = [
        {
            "id": 1,
            "parent_id": 12345,
            "work_type": "development",
            "assigned_to": "alice",
            "taskweb_visible": True,
        }
    ]
    code, out = run_cli(
        capsys,
        [
            "find-compatible-child",
            "--children-json",
            json.dumps(children),
            "--work-type",
            "development",
            "--user",
            "alice",
        ],
    )
    assert code == 0
    assert out["match"]["id"] == 1


def test_find_compatible_child_ambiguous(capsys):
    children = [
        {
            "id": 1,
            "parent_id": 12345,
            "work_type": "development",
            "assigned_to": "alice",
            "taskweb_visible": True,
        },
        {
            "id": 2,
            "parent_id": 12345,
            "work_type": "development",
            "assigned_to": "alice",
            "taskweb_visible": True,
        },
    ]
    code, out = run_cli(
        capsys,
        [
            "find-compatible-child",
            "--children-json",
            json.dumps(children),
            "--work-type",
            "development",
            "--user",
            "alice",
        ],
    )
    assert code == 1
    assert out["error_type"] == "AmbiguousChildTaskError"


def test_should_create_child_no_existing(capsys):
    code, out = run_cli(capsys, ["should-create-child"])
    assert code == 0
    assert out == {"should_create": True}


def test_build_child_task_item(capsys):
    code, out = run_cli(capsys, ["build-child-task-item", "--parent-title", PARENT_TITLE])
    assert code == 0
    assert out["title"] == PARENT_TITLE


def test_needs_assignment(capsys):
    child = {
        "id": 1,
        "parent_id": 12345,
        "work_type": "development",
        "assigned_to": None,
        "taskweb_visible": False,
    }
    code, out = run_cli(
        capsys, ["needs-assignment", "--child-json", json.dumps(child), "--user", "alice"]
    )
    assert code == 0
    assert out == {"needs_assignment": True}


def test_build_assignment_update(capsys):
    code, out = run_cli(capsys, ["build-assignment-update", "--user", "alice"])
    assert code == 0
    assert out["path"] == "/fields/System.AssignedTo"


def test_taskweb_start_timer_unavailable(capsys):
    code, out = run_cli(capsys, ["taskweb-start-timer", "--child-task-id", "1"])
    assert code == 1
    assert out["error_type"] == "TaskwebUnavailableError"


def test_taskweb_stop_timer_unavailable(capsys):
    code, out = run_cli(capsys, ["taskweb-stop-timer", "--child-task-id", "1"])
    assert code == 1
    assert out["error_type"] == "TaskwebUnavailableError"


def test_taskweb_log_hours_unavailable(capsys):
    code, out = run_cli(
        capsys,
        [
            "taskweb-log-hours",
            "--child-task-id",
            "1",
            "--start",
            "2026-09-10T10:00:00",
            "--end",
            "2026-09-10T10:15:00",
        ],
    )
    assert code == 1
    assert out["error_type"] == "TaskwebUnavailableError"


def test_missing_subcommand_exits_nonzero():
    with pytest.raises(SystemExit):
        main([])


# -- _handle_action_status: success/error contract for TaskwebAdapter results --


def test_handle_action_status_success_exits_zero(capsys):
    """Regression test: ActionStatus.timestamp is a datetime, not natively
    JSON-serializable — this success path was previously unreachable
    through the CLI (UnavailableTaskwebAdapter always raises first), so
    the bug was latent until this direct test exercised it."""
    status = ActionStatus(success=True, message="timer started", timestamp=datetime.now())
    code = _handle_action_status(status)
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["success"] is True
    assert isinstance(out["timestamp"], str)


def test_parse_time_range_start_and_end(capsys):
    code, out = run_cli(
        capsys, ["parse-time-range", "--start", "10:00", "--end", "10:15"]
    )
    assert code == 0
    assert out["start"].endswith("10:00:00")
    assert out["end"].endswith("10:15:00")


def test_parse_time_range_duration_only(capsys):
    code, out = run_cli(capsys, ["parse-time-range", "--duration-minutes", "30"])
    assert code == 0
    assert "start" in out and "end" in out


def test_parse_time_range_invalid_combination(capsys):
    code, out = run_cli(capsys, ["parse-time-range", "--start", "10:00"])
    assert code == 1
    assert "error_type" in out


def test_classify_work_type_known_value(capsys):
    code, out = run_cli(capsys, ["classify-work-type", "--hint", "development"])
    assert code == 0
    assert out == {"work_type": "development"}


def test_classify_work_type_no_hint_defaults(capsys):
    code, out = run_cli(capsys, ["classify-work-type"])
    assert code == 0
    assert out == {"work_type": "business_analysis"}


def test_classify_work_type_unknown_hint(capsys):
    code, out = run_cli(capsys, ["classify-work-type", "--hint", "gardening"])
    assert code == 1
    assert out["error_type"] == "ValueError"


def test_handle_action_status_business_failure_exits_one(capsys):
    """A `success=False` ActionStatus (not an exception) must still exit 1.

    Regression test for a code-review finding: FakeTaskwebAdapter.log_hours
    returns success=False for an invalid interval instead of raising, and
    the CLI previously printed that as if via _print_ok with exit 0.
    """
    status = ActionStatus(success=False, message="end must be after start", timestamp=datetime.now())
    code = _handle_action_status(status)
    out = json.loads(capsys.readouterr().out)
    assert code == 1
    assert out == {"error": "end must be after start", "error_type": "ActionFailure"}


def test_work_type_to_activity(capsys):
    code, out = run_cli(capsys, ["work-type-to-activity", "--work-type", "development"])
    assert code == 0
    assert out == {"activity": "Development"}


def test_activity_to_work_type(capsys):
    code, out = run_cli(capsys, ["activity-to-work-type", "--activity", "Testing"])
    assert code == 0
    assert out == {"work_type": "test"}


def test_activity_to_work_type_unknown_activity(capsys):
    code, out = run_cli(capsys, ["activity-to-work-type", "--activity", "Design"])
    assert code == 1
    assert out["error_type"] == "UnknownActivityError"


def test_build_activity_update(capsys):
    code, out = run_cli(capsys, ["build-activity-update", "--work-type", "business_analysis"])
    assert code == 0
    assert out == {
        "op": "add",
        "path": "/fields/Microsoft.VSTS.Common.Activity",
        "value": "Requirements",
    }


# -- CLI error-contract safety net (code review finding) --------------------


def test_find_compatible_child_malformed_json_never_crashes(capsys):
    code, out = run_cli(
        capsys,
        [
            "find-compatible-child",
            "--children-json",
            "not valid json",
            "--work-type",
            "development",
            "--user",
            "alice",
        ],
    )
    assert code == 1
    assert "error" in out and "error_type" in out


def test_find_compatible_child_missing_key_never_crashes(capsys):
    children = [{"id": 1, "parent_id": 12345}]  # missing required ChildTask fields
    code, out = run_cli(
        capsys,
        [
            "find-compatible-child",
            "--children-json",
            json.dumps(children),
            "--work-type",
            "development",
            "--user",
            "alice",
        ],
    )
    assert code == 1
    assert "error" in out and "error_type" in out


def test_needs_assignment_unexpected_key_never_crashes(capsys):
    child = {
        "id": 1,
        "parent_id": 12345,
        "work_type": "development",
        "assigned_to": "alice",
        "taskweb_visible": True,
        "unexpected_field": "boom",
    }
    code, out = run_cli(
        capsys, ["needs-assignment", "--child-json", json.dumps(child), "--user", "alice"]
    )
    assert code == 1
    assert "error" in out and "error_type" in out
