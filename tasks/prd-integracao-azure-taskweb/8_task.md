# Task 8.0: Full automated test suite consolidation

## Overview

Consolidate and validate the complete pytest suite across Tasks 1.0-7.0, confirming that the testing approach and known risks from the techspec are covered, before this module is considered ready for use by downstream TaskWeb PRO modules.

<skills>
### Conformance with Skills

No local `.claude/skills` directory exists in this project — no additional skill-specific conventions apply beyond what Task 6.0 established.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- techspec.md → Testing Approach
- All tests from Tasks 1.0-7.0 passing
- No live credentials required to run the unit test suite
</requirements>

## Subtasks

- [x] 8.1 Run the full `pytest` suite locally and fix any gaps or flakiness — 53 passed, 0 failures
- [ ] 8.2 Confirm the integration tests against the Azure DevOps sandbox pass (manual trigger, with documented how-to) — **blocked**: no sandbox parent PBI/Bug provisioned yet in Azure DevOps for this project; see Known Risks below
- [x] 8.3 Document remaining known gaps (`taskweb-mcp` disconnected, the child-task uniqueness race condition) as explicit, named skipped/pending tests — not silent omissions (see each `[num]_task.md`'s Task Tests section and `techspec.md` → Known Risks)

## Implementation Details

See `techspec.md` → Testing Approach and → Technical Considerations → Known Risks. This task validates and documents; it does not add new product logic.

## Success Criteria

- `pytest` passes with zero failures for the fully mocked unit suite
- A documented, explicit list exists of what remains pending due to `taskweb-mcp`, plus the concurrency risk noted for future hardening

## Task Tests

- [x] Unit tests: full suite green (53 passed)
- [ ] Integration tests: Azure DevOps sandbox suite green (manual run) — pending sandbox provisioning
- [ ] E2E tests: documented as pending until `taskweb-mcp` connects

## Relevant Files

- `tests/` (entire folder)
- `tasks/prd-integracao-azure-taskweb/techspec.md` (reference only)
