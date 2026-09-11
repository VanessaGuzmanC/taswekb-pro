# Task 6.0: Skill orchestration end-to-end

## Overview

Wire Tasks 2.0-5.0 together into the actual Claude Code skill flow (`SKILL.md` + `references/*.md`) that receives `{parent_id, work_type, user}` from the upstream text-interpretation module and drives the full sequence: resolve → create/assign → Taskweb action → status.

<skills>
### Conformance with Skills

No local `.claude/skills` directory exists in this project yet — this task is what creates the first one, structured as a sibling to `phoenix-spec`/`phoenix-bug` (global Claude Code skills directory): `SKILL.md` + `references/*.md` + Python helper modules.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- techspec.md → System Architecture → Component Overview (skill definition)
- PRD → User Experience (module has no UI of its own; consumed by other modules)
- techspec.md → Integration Points → Error handling (single retry for transient errors, no destructive fallback)
</requirements>

## Subtasks

- [x] 6.1 Write `SKILL.md` describing the module's trigger and its role within TaskWeb PRO
- [x] 6.2 Write `references/*.md` detailing the exact orchestration sequence (query → resolve → create/assign → Taskweb action) for Claude to follow at runtime
- [x] 6.3 Wire error handling: a single retry for transient MCP errors, clear user-facing messages otherwise (documented in `references/orchestrate.md` → Error handling; enforced by the orchestrating skill at runtime, not by `taskweb_pro.cli` itself)
- [x] 6.4 Verify the flow never modifies the parent task nor removes existing child tasks, on any path (no code path in `taskweb_pro` builds a parent-modifying or child-removing payload; `references/orchestrate.md` states this restriction explicitly for every command)

## Implementation Details

See `techspec.md` → System Architecture and → Integration Points → Error handling. This task composes the modules from Tasks 2.0-5.0; it does not reimplement their logic.

## Success Criteria

- A full command-shaped input produces the correct end-to-end sequence of MCP calls and a clear final status
- The parent task and any pre-existing child tasks remain untouched throughout every tested path

## Task Tests

- [x] Unit tests: orchestration logic with mocked resolver and adapter (`tests/test_orchestration.py`, exercising the `taskweb_pro.cli` seam directly)
- [ ] Integration tests: full flow against an Azure DevOps sandbox project with Taskweb mocked (pending — no sandbox parent task provisioned yet)
- [ ] E2E tests: manual end-to-end run once `taskweb-mcp` connects (documented as pending per techspec.md)

## Relevant Files

- `SKILL.md`
- `references/*.md`
- `taskweb_pro/*.py`
- `tests/test_orchestration.py`
