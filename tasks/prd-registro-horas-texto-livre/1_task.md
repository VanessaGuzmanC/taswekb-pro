# Task 1.0: Time range parsing (`parse_time_range`)

## Overview

Implement the pure function that turns a start/end/duration combination (already extracted by Claude from free text) into a concrete `(start, end)` datetime pair, satisfying PRD Features 2 and 3 (registro por rango horario / por duração).

<skills>
### Conformance with Skills

No local `.claude/skills` directory holds a skill for this yet (Task 4.0 creates it). This task follows the `taskweb-pro-azure-integration` skill's convention of keeping deterministic logic in a plain, pure Python module.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- PRD requirements 2.1, 2.2, 2.3, 3.1, 3.2
- techspec.md → Implementation Design → Main Interfaces (`parse_time_range`)
- techspec.md → Technical Considerations → Known Risks (single-calendar-day assumption)
</requirements>

## Subtasks

- [x] 1.1 Implement start+end → `(start, end)` datetimes, both on `now`'s calendar day (PRD 2.1)
- [x] 1.2 Implement start+duration → `(start, start + duration)` (PRD 2.2)
- [x] 1.3 Implement duration-only (no start, no end) → `(now - duration, now)` (PRD 3.1, 3.2)
- [x] 1.4 Reject invalid combinations (neither end nor duration given; both end and duration given; end <= start; non-positive duration) with a clear, typed error (PRD 2.3)

## Implementation Details

See `techspec.md` → Implementation Design → Main Interfaces. Do not add a date-parsing dependency — `datetime.strptime("%H:%M")` is sufficient per the techspec's Reuse vs. Build decision.

## Success Criteria

- All three valid input shapes produce the correct `(start, end)` pair
- Every invalid combination raises a typed error instead of silently producing a wrong interval

## Task Tests

- [x] Unit tests: each valid shape, each invalid combination, end==start edge case (13 tests, `tests/test_time_parsing.py`)
- [x] Integration tests: not applicable for this task
- [x] E2E tests: not applicable for this task

## Relevant Files

- `taskweb_pro/time_parsing.py`
- `tests/test_time_parsing.py`
