# Task 2.0: Azure query & child-task compatibility resolver (Feature 1)

## Overview

Implement the pure-logic resolver that, given a parent task ID and its children (fetched via the Azure DevOps MCP tools), decides whether a compatible child task already exists. This is the entry point for PRD Feature 1 (Consulta de tarefas pai e filhas no Azure).

<skills>
### Conformance with Skills

No local `.claude/skills` directory exists in this project. Follows the `phoenix-spec` convention of keeping deterministic decision logic in a plain Python module invoked by the skill, separate from the orchestration prompt itself.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- PRD requirements 1.1, 1.2, 1.3, 1.4
- techspec.md → Implementation Design → Main Interfaces (`ChildTaskResolver`) and Data Models (`ChildTask`)
- techspec.md → Integration Points → Azure DevOps (`wit_query`, `wit_work_item`)
</requirements>

## Subtasks

- [x] 2.1 Implement the `ChildTask` model (`id`, `parent_id`, `work_type`, `assigned_to`, `taskweb_visible`)
- [x] 2.2 Implement `build_children_wiql(parent_id)`, producing the WIQL string to be run via `wit_query` (action `wiql`)
- [x] 2.3 Implement `find_compatible_child(children, work_type, user)` — the compatibility matrix (work-type match × assignee match), returning the single match or `None`
- [x] 2.4 Handle an invalid or nonexistent parent ID with a clear, typed error (PRD 1.4)

## Implementation Details

See `techspec.md` → Implementation Design → Main Interfaces / Data Models, and → Integration Points → Azure DevOps. Do not repeat the interface signatures here — implement exactly what is specified there.

## Success Criteria

- Given a parent ID and a list of children, the resolver deterministically returns the correct compatible match or `None`
- An invalid/nonexistent parent ID raises a clear, typed error instead of failing silently or crashing

## Task Tests

- [x] Unit tests: compatibility matrix cases (single match, no match, multiple candidates — apply the uniqueness rule from `overview/glossary_context.md.md`), invalid parent ID handling; identity-format normalization (`_identities_match`/`_normalize_identity`, added after a code-review finding — see `techspec.md` → Known Risks)
- [ ] Integration tests: WIQL query executed against the Azure DevOps MCP tools using a sandbox parent task with real children (pending — no sandbox project/parent task provisioned yet; would also validate the identity-normalization assumption above against real data)
- [x] E2E tests: not applicable for this task

## Relevant Files

- `taskweb_pro/azure_task_resolver.py`
- `taskweb_pro/models.py`
- `tests/test_azure_task_resolver.py`
