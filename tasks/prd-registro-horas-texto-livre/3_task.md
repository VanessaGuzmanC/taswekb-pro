# Task 3.0: CLI wiring

## Overview

Expose Tasks 1.0 and 2.0's pure functions as `parse-time-range` and `classify-work-type` subcommands on the existing `taskweb_pro.cli`, following the exact JSON-in/JSON-out contract already established there.

<skills>
### Conformance with Skills

No local `.claude/skills` directory holds a skill for this yet (Task 4.0 creates it). This task extends the existing `taskweb_pro/cli.py` rather than creating a second CLI, per techspec.md → Main Decisions.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- techspec.md → System Architecture → Component Overview (`taskweb_pro/cli.py` extended, not replaced)
- The CLI's existing documented contract: one JSON object per subcommand, exit 0 on success, exit 1 with `{"error", "error_type"}` on a handled error, never a raw traceback (see `taskweb_pro/cli.py` module docstring and its `main()` safety net)
</requirements>

## Subtasks

- [x] 3.1 Add `parse-time-range` subcommand (`--start`, `--end`, `--duration-minutes`, all optional) returning `{"start": <ISO>, "end": <ISO>}`
- [x] 3.2 Add `classify-work-type` subcommand (`--hint`, optional) returning `{"work_type": <value>}`
- [x] 3.3 Confirm both subcommands go through `main()`'s existing top-level exception safety net — no per-command duplication needed

## Implementation Details

See `taskweb_pro/cli.py`'s existing subcommands (e.g. `work-type-to-activity`) for the pattern to follow. Do not duplicate the safety-net logic already in `main()`.

## Success Criteria

- Both subcommands round-trip correctly through `taskweb_pro.cli.main`
- Malformed input (e.g. neither `--end` nor `--duration-minutes`) exits 1 with the documented JSON error shape, never a traceback

## Task Tests

- [x] Unit tests: not applicable beyond Task 1.0/2.0's own unit tests
- [x] Integration tests: both subcommands exercised via `taskweb_pro.cli.main`, valid and invalid input (`tests/test_orchestration.py`)
- [x] E2E tests: not applicable for this task

## Relevant Files

- `taskweb_pro/cli.py`
- `tests/test_orchestration.py`
