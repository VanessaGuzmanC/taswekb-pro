# Task 5.0: Taskweb adapter interface (Feature 4 contract)

## Overview

Define and implement the internal `TaskwebAdapter` protocol and a mocked backend, so Feature 4 (Ações operacionais no Taskweb) has a stable, testable contract independent of `taskweb-mcp`, which is currently disconnected in this environment (permissions pending on the user's side).

<skills>
### Conformance with Skills

No local `.claude/skills` directory exists in this project. Follows the `phoenix-spec` convention of isolating a pending external dependency behind an internal interface rather than blocking on it.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- PRD requirements 4.1, 4.2, 4.3, 4.4
- techspec.md → Implementation Design → Main Interfaces (`TaskwebAdapter`)
- techspec.md → Technical Considerations → Known Risks (`taskweb-mcp` unavailability)
</requirements>

## Subtasks

- [x] 5.1 Define the `TaskwebAdapter` protocol (`start_timer`, `stop_timer`, `log_hours`) and the `ActionStatus` model (`ActionStatus` already added to `models.py` in Task 1.0)
- [x] 5.2 Implement a mock/fake adapter for tests and local development (`FakeTaskwebAdapter`)
- [x] 5.3 Implement fail-fast behavior when no real backend is wired (`UnavailableTaskwebAdapter`, raises `TaskwebUnavailableError`)
- [x] 5.4 Document the adapter's expected real-backend contract (assumed tool names) so it can be wired to `taskweb-mcp` once connectivity is restored (module docstring)

## Implementation Details

See `techspec.md` → Implementation Design → Main Interfaces (`TaskwebAdapter`) and → Technical Considerations → Known Risks. Reference, do not repeat, the interface signature already specified there.

## Success Criteria

- The adapter interface is stable and fully covered by tests using the mock backend
- Calling any adapter method without a real backend wired fails clearly and immediately, rather than silently or ambiguously

## Task Tests

- [x] Unit tests: mock adapter behavior for `start_timer`/`stop_timer`/`log_hours`, and the fail-fast path
- [ ] Integration tests: marked pending/skipped until `taskweb-mcp` connects, per techspec.md → Testing Approach
- [ ] E2E tests: not applicable until `taskweb-mcp` connects

## Relevant Files

- `taskweb_pro/taskweb_adapter.py`
- `tests/test_taskweb_adapter.py`
