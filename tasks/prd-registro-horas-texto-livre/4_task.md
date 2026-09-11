# Task 4.0: Skill definition (`taskweb-pro-text-interpretation`)

## Overview

Create the second Claude Code skill, which instructs Claude on what to extract from the operator's free text and how to combine the Task 3.0 CLI subcommands with the existing `taskweb-pro-azure-integration` skill's commands to complete a registration.

<skills>
### Conformance with Skills

Sibling to the existing `taskweb-pro-azure-integration` skill — same `SKILL.md` + `references/*.md` shape, calling into that skill's commands rather than duplicating any Azure/Taskweb logic (techspec.md → Conformance with Skills).
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- PRD requirements 1.1, 1.2, 1.3
- techspec.md → System Architecture (skill definition, data flow)
- Must never call an MCP tool directly — only the CLI subcommands and the existing skill's commands
</requirements>

## Subtasks

- [x] 4.1 Write `SKILL.md` describing the trigger (free-text time-registration commands) and the module's role
- [x] 4.2 Write `references/*.md` detailing exactly what to extract from the sentence (`activity_text`, `parent_id?`, `work_type_hint?`, `start?`, `end?`, `duration_minutes?`, `is_start_of_activity`) and the call sequence into Task 3.0's subcommands and `taskweb-pro-azure-integration`
- [x] 4.3 Document the confirmation-before-acting rule (PRD Feature 4) explicitly as a step, not an aside
- [x] 4.4 Document that a "start of activity" intent currently has no downstream module to hand off to (Timer Control is not yet built) — state this limitation plainly rather than pretending it works

## Implementation Details

See `techspec.md` → System Architecture and → Known Risks (Claude's extraction accuracy is not unit-testable).

## Success Criteria

- Given one of the PRD's example commands, following `references/*.md` step by step produces the correct sequence of CLI and existing-skill calls
- The "start of activity" case is explicitly flagged as unactionable today, not silently dropped

## Task Tests

- [x] Unit tests: not applicable (this task is documentation, not code)
- [x] Integration tests: not applicable
- [x] E2E tests: manual walkthrough against the PRD's example commands (Task 5.0)

## Relevant Files

- `.claude/skills/taskweb-pro-text-interpretation/SKILL.md`
- `.claude/skills/taskweb-pro-text-interpretation/references/*.md`
