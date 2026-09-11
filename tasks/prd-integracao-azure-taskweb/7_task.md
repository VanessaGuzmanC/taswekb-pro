# Task 7.0: Local observability

## Overview

Add structured local logging across the module, per the techspec's Monitoring and Observability section, sufficient for manual diagnosis during MVP validation — this project has no external observability stack.

<skills>
### Conformance with Skills

No local `.claude/skills` directory exists in this project — no additional skill-specific conventions apply beyond what Task 6.0 established.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- techspec.md → Monitoring and Observability
- `architecture/tech_restrictions_context.md.md` → credentials must never be exposed (including in logs)
</requirements>

## Subtasks

- [x] 7.1 Add logging calls at each decision point (resolve, create, assign, Taskweb action)
- [x] 7.2 Ensure log messages never include secrets/tokens (verified by `test_logging.py`'s `_assert_no_secrets`)
- [x] 7.3 Document how to enable and inspect local logs for manual diagnosis (see "Relevant Files" below)

## Implementation Details

See `techspec.md` → Monitoring and Observability. This task adds logging only — it does not change any decision logic from Tasks 2.0-6.0.

## Success Criteria

- Every major decision/action produces a log line sufficient to reconstruct what happened for a single command
- No credentials or tokens appear in any log output

## Task Tests

- [x] Unit tests: log emission assertions at each decision point (e.g., via `caplog`)
- [x] Integration tests: not applicable for this task
- [x] E2E tests: not applicable for this task

## Relevant Files

- `taskweb_pro/*.py`
- `tests/test_logging.py`
- `README.md` (local logging how-to)
