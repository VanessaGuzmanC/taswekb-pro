# Task 2.0: Work-type classification (`classify_work_type`)

## Overview

Implement the pure function that maps a work-type hint (already extracted by Claude, or `None` for daily/meeting-style activities) to one of the three known `WorkType` values, satisfying PRD requirement 1.4.

<skills>
### Conformance with Skills

No local `.claude/skills` directory holds a skill for this yet (Task 4.0 creates it).
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- PRD requirement 1.4
- techspec.md → Implementation Design → Main Interfaces (`classify_work_type`)
- techspec.md → Technical Considerations → Main Decisions (daily/meeting → `business_analysis`, user-confirmed)
</requirements>

## Subtasks

- [x] 2.1 Accept any of the three known `WorkType` values verbatim
- [x] 2.2 Map `None` (no recognizable hint) to `business_analysis`
- [x] 2.3 Reject any other string with a clear, typed error, mirroring `validate_parent_type`'s style in `azure_task_resolver.py`

## Implementation Details

See `techspec.md` → Implementation Design → Main Interfaces. Reference, do not repeat, `taskweb_pro.models.WorkType`.

## Success Criteria

- Every known `WorkType` value passes through unchanged
- `None` always resolves to `business_analysis`
- Any unrecognized string raises a typed error, never silently defaults

## Task Tests

- [x] Unit tests: three known values, `None`, an unknown string (5 tests, `tests/test_activity_classification.py`)
- [x] Integration tests: not applicable for this task
- [x] E2E tests: not applicable for this task

## Relevant Files

- `taskweb_pro/activity_classification.py`
- `tests/test_activity_classification.py`
