# Task 1.0: `ActiveTimer` model and pure decision logic (`has_conflicting_timer`, `resolve_stop_target`)

## Overview

Add the `ActiveTimer` dataclass to `taskweb_pro/models.py` and implement the two pure, no-I/O decision functions this feature needs: whether starting a new timer conflicts with one already tracked as active, and which child task ID a stop command should target.

<skills>
### Conformance with Skills

No local `.claude/skills` directory holds a skill for this yet (Task 4.0 creates it). This task follows the `taskweb-pro-azure-integration`/`taskweb-pro-text-interpretation` convention of keeping deterministic logic in a plain, pure Python module.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- PRD requirements 4, 6, 7, 8, 9
- techspec.md → Implementation Design → Main Interfaces, Data Models
</requirements>

## Subtasks

- [ ] 1.1 Add `ActiveTimer` (`child_task_id: int`, `parent_id: int`, `work_type: WorkType`, `user: str`, `started_at: datetime`, `frozen=True, slots=True`) to `taskweb_pro/models.py`.
- [ ] 1.2 Create `taskweb_pro/timer_state.py` with `has_conflicting_timer(active: ActiveTimer | None, requested_child_task_id: int) -> bool`.
- [ ] 1.3 Add `NoActiveTimerError(RuntimeError)` to `timer_state.py`.
- [ ] 1.4 Implement `resolve_stop_target(active: ActiveTimer | None, requested_child_task_id: int | None) -> int` in `timer_state.py`: explicit reference wins when given; otherwise falls back to `active.child_task_id`; raises `NoActiveTimerError` when both are absent.
- [ ] 1.5 Unit tests for both functions covering every combination described in techspec.md → Testing Approach → Unit Tests (conflict matrix; resolve-target matrix including the `NoActiveTimerError` case).

## Implementation Details

See techspec.md → Implementation Design → Main Interfaces, Data Models, and → Technical Considerations → Main Decisions (explicit reference always wins; conflict is only flagged, never auto-resolved here).

## Success Criteria

- `has_conflicting_timer` and `resolve_stop_target` are pure functions with no I/O and no dependency on Task 2.0.
- Every case in the unit-test matrix from techspec.md → Testing Approach → Unit Tests passes.

## Task Tests

- [ ] Unit tests: `has_conflicting_timer` (no active, active for same child, active for different child); `resolve_stop_target` (active+no reference, active+matching reference, active+differing reference, no active+reference, no active+no reference → `NoActiveTimerError`)
- [ ] Integration tests: none at this layer (covered once wired into the CLI in Task 3.0)

## Relevant Files

- `taskweb_pro/models.py`
- `taskweb_pro/timer_state.py`
- `tests/test_timer_state.py`
