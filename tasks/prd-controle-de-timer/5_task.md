# Task 5.0: Manual validation and test suite consolidation

## Overview

Walk through the PRD's example commands (start and stop, with and without conflicts/explicit references) against `references/orchestrate.md` (Task 4.0), confirm the automated suite is green, and document explicitly what remains unvalidated (Claude's start/stop intent recognition, and anything downstream of `taskweb-mcp`).

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

- [ ] 5.1 Run the full `pytest` suite and fix any gaps or flakiness.
- [ ] 5.2 Manually walk through a start-timer command, a stop-timer command with no reference, a stop-timer command with an explicit reference, a start-timer command while a different timer is already tracked as active (conflict path), and a stop-timer command with no active timer and no reference (`NoActiveTimerError` path) — confirming the expected CLI/skill call sequence for each against `references/orchestrate.md`.
- [ ] 5.3 Document remaining known gaps explicitly, not silently: Claude's start/stop intent extraction accuracy is not automatable; `taskweb-mcp` still disconnected; local state file does not reconcile with the real Taskweb timer state (already flagged in techspec.md → Known Risks).

## Implementation Details

See techspec.md → Testing Approach and → Known Risks.

## Success Criteria

- `pytest` passes with zero failures.
- Each of the five walkthrough scenarios in 5.2 has a documented, correct expected call sequence.

## Task Tests

- [ ] Unit tests: full suite green
- [ ] Integration tests: full suite green
- [ ] E2E tests: manual walkthrough documented (not automatable — see Known Risks)

## Relevant Files

- `tests/` (entire folder)
- `tasks/prd-controle-de-timer/techspec.md` (reference only)
