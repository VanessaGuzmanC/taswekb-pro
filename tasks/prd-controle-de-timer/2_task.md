# Task 2.0: Local active-timer persistence (atomic load/save/clear)

## Overview

Implement the one deliberate I/O seam this module introduces: a small local JSON file tracking the last active timer per user, written atomically so a crash mid-write can never leave a corrupted file, and read defensively so a corrupted or missing file degrades to "no active timer" rather than a hard failure.

<skills>
### Conformance with Skills

No local `.claude/skills` directory holds a skill for this yet (Task 4.0 creates it).
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- techspec.md → Implementation Design → Data Models (on-disk shape, `DEFAULT_STATE_PATH`)
- techspec.md → Integration Points (stdlib `tempfile` + `os.replace`, no `filelock`)
- techspec.md → Technical Considerations → Known Risks (corrupted file → treated as absent, logged at WARNING)
</requirements>

## Subtasks

- [ ] 2.1 Add `DEFAULT_STATE_PATH = Path.home() / ".taskweb_pro" / "active_timer.json"` to `timer_state.py`.
- [ ] 2.2 Implement `save_active_timer(timer: ActiveTimer, path: Path = DEFAULT_STATE_PATH) -> None` using `tempfile.mkstemp(dir=path.parent)` + `os.replace()` for an atomic write; create `path.parent` if missing.
- [ ] 2.3 Implement `load_active_timer(path: Path = DEFAULT_STATE_PATH) -> ActiveTimer | None`: returns `None` when the file does not exist; returns `None` and logs a `WARNING` when the file exists but fails to parse into a valid `ActiveTimer`.
- [ ] 2.4 Implement `clear_active_timer(path: Path = DEFAULT_STATE_PATH) -> None`: removes the file if present, no-op (no error) if already absent.
- [ ] 2.5 Unit tests using `tmp_path`: save→load round-trip; load on a missing file; load on a corrupted/invalid-JSON file (asserts `None` + a logged warning); clear on an existing file and on an already-absent one; a save leaves no stray temp file behind.

## Implementation Details

See techspec.md → Implementation Design → Data Models and → Integration Points for the atomic-write rationale (stdlib `tempfile`/`os.replace`, no new dependency).

## Success Criteria

- No test ever leaves a partially-written state file observable (atomicity holds even when the write path is exercised repeatedly in the test suite).
- A corrupted file never raises out of `load_active_timer` — it returns `None` and logs at `WARNING`.

## Task Tests

- [ ] Unit tests: round-trip, missing file, corrupted file, clear (present/absent), no stray temp file after save
- [ ] Integration tests: none at this layer (covered once wired into the CLI in Task 3.0)

## Relevant Files

- `taskweb_pro/timer_state.py`
- `tests/test_timer_state.py`
