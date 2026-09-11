# Task 3.0: Child task creation in Azure (Feature 2)

## Overview

Create a new child task in Azure DevOps, but only when Task 2.0's resolver found no compatible match — satisfying PRD Feature 2 (Criação de tarefas filhas no Azure).

<skills>
### Conformance with Skills

No local `.claude/skills` directory exists in this project. Follows the `phoenix-spec` convention of reusing existing MCP write tools rather than building a custom API client.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- PRD requirements 2.1, 2.2, 2.3, 2.4
- techspec.md → Integration Points → Azure DevOps (`wit_work_item_write` action `add_child`, `wit_work_item_link_write`)
- techspec.md → Technical Considerations → Main Decisions (reuse Azure MCP tools, no custom client)
</requirements>

## Subtasks

- [x] 3.1 Implement the creation flow gated strictly by Task 2.0's resolver result — only create when no compatible child exists (`should_create_child`; wired end-to-end in Task 6.0's `ensure-child-task`)
- [x] 3.2 Ensure the created child task title matches the parent task's name (PRD 2.2) (`build_child_task_item`)
- [x] 3.3 Ensure the parent-child link is established — decided to use `wit_work_item_write` action `add_child`, which links in the same call; no separate `wit_work_item_link_write` needed (documented in `azure_task_resolver.py` and `references/orchestrate.md`)
- [x] 3.4 Guard against duplicate creation by re-checking compatibility immediately before writing (PRD 2.4) — encoded as the required second `resolve-child-task` pass in `references/orchestrate.md` step "ensure-child-task" 3

## Implementation Details

See `techspec.md` → Integration Points and → Technical Considerations → Main Decisions. Do not re-describe the Azure MCP call shapes here — reference them.

## Success Criteria

- A new child task is created with the correct title and a correct link to its parent
- No duplicate child task is created when a compatible one already exists

## Task Tests

- [x] Unit tests: gating logic (creation happens iff the resolver returned `None`), title propagation from parent to child
- [ ] Integration tests: real creation and link verified against an Azure DevOps sandbox project via the MCP tools (pending — no sandbox parent task provisioned yet)
- [x] E2E tests: not applicable for this task

## Relevant Files

- `taskweb_pro/azure_task_resolver.py` (or `taskweb_pro/azure_task_writer.py`, per the module split chosen in techspec.md)
- `tests/test_child_task_creation.py`
