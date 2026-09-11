# Task 3.0: CLI wiring (5 new subcommands)

## Overview

Expose Tasks 1.0 and 2.0's functions as five `taskweb_pro.cli` subcommands, following the exact JSON-in/JSON-out contract already established there: `timer-get-active`, `timer-check-conflict`, `timer-save-active`, `timer-resolve-stop-target`, `timer-clear-active`.

<skills>
### Conformance with Skills

No local `.claude/skills` directory holds a skill for this yet (Task 4.0 creates it). This task extends the existing `taskweb_pro/cli.py` rather than creating a second CLI, per techspec.md → System Architecture.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- techspec.md → System Architecture → Component Overview (`taskweb_pro/cli.py` extended, not replaced)
- techspec.md → Implementation Design → Main Interfaces
</requirements>

## Subtasks

- [ ] 3.1 `timer-get-active` (no required args) → `{"active": null}` or `{"active": {child_task_id, parent_id, work_type, user, started_at}}`.
- [ ] 3.2 `timer-check-conflict --requested-child-task-id <id>` → `{"conflict": bool, "active": {...} | null}` (reads state internally via `load_active_timer`).
- [ ] 3.3 `timer-save-active --child-task-id <id> --parent-id <id> --work-type <wt> --user <user>` → builds an `ActiveTimer` with `started_at=datetime.now()`, persists it, returns `{"saved": true}`.
- [ ] 3.4 `timer-resolve-stop-target [--requested-child-task-id <id>]` → reads active state, returns `{"child_task_id": <id>}`; on `NoActiveTimerError`, follows the module's existing error contract (`{"error": ..., "error_type": "NoActiveTimerError"}`, exit 1).
- [ ] 3.5 `timer-clear-active` → clears the state file, returns `{"cleared": true}`.
- [ ] 3.6 Integration tests calling `taskweb_pro.cli.main` directly for all five subcommands (success and error paths), with a `tmp_path`-backed state file — following the pattern in `tests/test_orchestration.py`.

## Implementation Details

See techspec.md → Implementation Design → Main Interfaces and → Monitoring and Observability (log levels per outcome).

## Success Criteria

- All five subcommands print exactly one JSON object and exit 0 on success, 1 on a handled business error — never a raw traceback, matching the module-wide CLI contract documented in `cli.py`'s own docstring.

## Task Tests

- [ ] Unit tests: none new (covered in Tasks 1.0/2.0)
- [ ] Integration tests: all five subcommands, success and error paths, via `taskweb_pro.cli.main`

## Relevant Files

- `taskweb_pro/cli.py`
- `tests/test_orchestration.py` (or a new `tests/test_timer_cli.py`, matching existing test-file granularity)
