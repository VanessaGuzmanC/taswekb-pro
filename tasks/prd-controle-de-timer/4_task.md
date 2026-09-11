# Task 4.0: Skill definition (`taskweb-pro-timer-control`)

## Overview

Create the third Claude Code skill, which instructs Claude on how to recognize a start-timer or stop-timer free-text command and how to combine Task 3.0's CLI subcommands with the existing `taskweb-pro-azure-integration` (`ensure-child-task`, `resolve-child-task`, `taskweb-start-timer`, `taskweb-stop-timer`) and `taskweb-pro-text-interpretation` (extraction conventions) skills to complete the flow end to end.

<skills>
### Conformance with Skills

Sibling to the existing `taskweb-pro-azure-integration` and `taskweb-pro-text-interpretation` skills — same `SKILL.md` + `references/*.md` shape, composing both existing skills' commands rather than duplicating any Azure/Taskweb or text-extraction logic (techspec.md → Conformance with Skills).
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- PRD requirements 1, 2, 3, 4, 5 (start timer); 6, 7, 8, 9, 10 (stop timer)
- techspec.md → System Architecture → Component Overview (data flow: start, stop)
</requirements>

## Subtasks

- [ ] 4.1 `SKILL.md`: purpose, trigger, prerequisites (mirroring `taskweb-pro-azure-integration/SKILL.md`'s structure), and an explicit statement that this skill never calls Azure/Taskweb MCP tools directly — only through the existing skill's commands.
- [ ] 4.2 `references/orchestrate.md` → start-timer sequence: extend text-interpretation's extraction → `classify-work-type` → `ensure-child-task` → `timer-check-conflict` → if `conflict: true`, ask the user for confirmation before proceeding → `taskweb-start-timer` → on success, `timer-save-active`.
- [ ] 4.3 `references/orchestrate.md` → stop-timer sequence: extraction (reference optional) → if a reference was given, `resolve-child-task` to get its child task ID; otherwise none → `timer-resolve-stop-target` → `taskweb-stop-timer` → on success, `timer-clear-active` **only if** the stopped child task ID matches the one currently tracked by `timer-get-active` (per techspec.md → Known Risks).
- [ ] 4.4 Document the `NoActiveTimerError` case in `references/orchestrate.md`: report plainly to the operator, do not retry or guess a task reference.
- [ ] 4.5 Document error handling consistent with the other two skills: a transient Azure DevOps MCP error may be retried once; every other failure (including all `timer_pro.cli` business errors) is surfaced immediately.

## Implementation Details

See techspec.md → System Architecture → Component Overview (data flow: start, stop) and → Technical Considerations → Main Decisions.

## Success Criteria

- Following `references/orchestrate.md` for a start command never bypasses the conflict check, and following it for a stop command never bypasses `resolve_stop_target`'s explicit-reference-wins rule.
- The skill never calls `wit_work_item_write`/`wit_work_item_link_write` directly — every Azure/Taskweb action goes through `taskweb-pro-azure-integration`'s existing commands.

## Task Tests

- [ ] Unit tests: none (this task is documentation/orchestration, no new Python logic)
- [ ] Integration tests: none beyond Task 3.0's CLI-level tests
- [ ] E2E tests: manual walkthrough in Task 5.0

## Relevant Files

- `.claude/skills/taskweb-pro-timer-control/SKILL.md`
- `.claude/skills/taskweb-pro-timer-control/references/orchestrate.md`
