# Task 4.0: Automatic child task assignment (Feature 3)

## Overview

Ensure the child task — whether reused from Task 2.0 or created in Task 3.0 — ends up assigned to the requesting user, satisfying PRD Feature 3 (Atribuição automática de tarefas filhas).

<skills>
### Conformance with Skills

No local `.claude/skills` directory exists in this project. Follows the `phoenix-spec` convention of reusing existing MCP write tools rather than building a custom API client.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- PRD requirements 3.1, 3.2
- techspec.md → Integration Points → Azure DevOps (`wit_work_item_write` action `update`, path `/fields/System.AssignedTo`)
</requirements>

## Subtasks

- [x] 4.1 Implement the assignment check — skip the write when the child task is already assigned to the correct user (`needs_assignment`)
- [x] 4.2 Implement the assignment update call, covering both the reuse path (Task 2.0) and the creation path (Task 3.0) (`build_assignment_update`; wired for both paths in `references/orchestrate.md` step 5)
- [x] 4.3 Surface a clear success/failure status for the assignment step (Azure MCP `update` call result surfaced directly by the orchestration)

## Implementation Details

See `techspec.md` → Integration Points and → Implementation Design → Data Models (`ChildTask.assigned_to`). Reference, do not repeat, the call shape already specified there.

## Success Criteria

- The child task is assigned to the requesting user on every path (reused or newly created)
- No redundant write occurs when the task is already correctly assigned

## Task Tests

- [x] Unit tests: assignment-needed vs. already-assigned branches, including the `"Display Name <email>"` identity-format case (added after a code-review finding — see `techspec.md` → Known Risks)
- [ ] Integration tests: real assignment update verified against an Azure DevOps sandbox project (pending — no sandbox parent task provisioned yet; would also validate the identity-normalization assumption above against real data)
- [x] E2E tests: not applicable for this task

## Relevant Files

- `taskweb_pro/azure_task_resolver.py` (or `taskweb_pro/azure_task_writer.py`, per the module split chosen in techspec.md)
- `tests/test_assignment.py`
