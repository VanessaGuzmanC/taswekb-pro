# Task 5.0: Manual validation and test suite consolidation

## Overview

Walk through the PRD's example commands against `references/*.md` (Task 4.0), confirm the automated suite is green, and document explicitly what remains unvalidated (Claude's extraction accuracy, and anything downstream of `taskweb-mcp`).

<skills>
### Conformance with Skills

No additional skill-specific conventions beyond what Task 4.0 established.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- techspec.md → Testing Approach
- All tests from Tasks 1.0-3.0 passing
</requirements>

## Subtasks

- [x] 5.1 Run the full `pytest` suite and fix any gaps or flakiness — 86 passed, 0 failures
- [x] 5.2 Manually walk through each of the PRD's four example commands against `references/*.md`, confirming the extracted fields and the resulting CLI/skill call sequence are correct — ran `classify-work-type`/`parse-time-range` directly for all 4 examples; all four classified and time-computed correctly (see session transcript)
- [x] 5.3 Document remaining known gaps (Claude's extraction accuracy is not automatable; `taskweb-mcp` still disconnected) explicitly, not silently — documented in `techspec.md` → Known Risks and `references/extract-and-dispatch.md` steps 4-5

## Implementation Details

See `techspec.md` → Testing Approach and → Known Risks.

## Success Criteria

- `pytest` passes with zero failures
- Each PRD example command has a documented, correct expected call sequence

## Task Tests

- [x] Unit tests: full suite green (86 passed)
- [x] Integration tests: full suite green
- [x] E2E tests: manual walkthrough documented (not automatable — see Known Risks)

## Relevant Files

- `tests/` (entire folder)
- `tasks/prd-registro-horas-texto-livre/techspec.md` (reference only)
