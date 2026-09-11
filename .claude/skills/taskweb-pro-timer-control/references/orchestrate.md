# Orchestrate — Timer control flow

All `python3 -m taskweb_pro.cli` calls print one JSON object to stdout and exit `0` on success, `1` on a handled business error (`{"error": ..., "error_type": ...}`). Parse the JSON either way — never treat a non-zero exit as a crash before checking for that shape.

## `start-timer`

Inputs: `parent_id` (int), `work_type` (`development` | `test` | `business_analysis`), `user`.

1. Run `taskweb-pro-azure-integration`'s `ensure-child-task` (see that skill's `references/orchestrate.md`) with `parent_id`, `work_type`, `user`. This resolves an existing compatible child task or creates and assigns one — full reuse, no duplicate logic here. Stop and surface the error if this step fails.
2. `python3 -m taskweb_pro.cli timer-check-conflict --requested-child-task-id <child task id from step 1>`.
   - `conflict: false` → proceed to step 3.
   - `conflict: true` → the response's `active` field names the child task currently tracked as having a timer running. **Ask the operator for confirmation** before proceeding ("ya tenés un timer corriendo en la tarea <active.child_task_id> — ¿querés iniciar igual el de la tarea <requested>?"). Only continue past this point on an explicit "yes"; on "no" or no clear answer, stop here and report that the existing timer was left untouched.
3. `python3 -m taskweb_pro.cli taskweb-start-timer --child-task-id <child task id from step 1>` (this is `taskweb-pro-azure-integration`'s command). Today this always exits `1` with `error_type: TaskwebUnavailableError` — `taskweb-mcp` is disconnected in this environment. Report this plainly ("la tarea ya está lista/asignada en Azure; el inicio del timer en Taskweb queda pendiente hasta que se conecte taskweb-mcp") rather than retrying.
4. Only on success (once `taskweb-mcp` is connected): `python3 -m taskweb_pro.cli timer-save-active --child-task-id <id> --parent-id <parent_id> --work-type <work_type> --user <user>` to persist this as the tracked active timer. Do not save if step 3 failed.
5. Report: whether the child task was reused or created (from step 1), whether a conflict was flagged and how the operator resolved it (step 2), and whether the timer actually started in Taskweb (step 3) or is pending `taskweb-mcp`.

## `stop-timer`

Inputs: `user`, and optionally `parent_id` + `work_type` (only when the operator's sentence actually named a task).

1. If `parent_id`/`work_type` were given: run `taskweb-pro-azure-integration`'s `resolve-child-task` (**not** `ensure-child-task` — never create a task just to stop a timer) to get that task's child task ID.
   - `match: null` → there is no child task for that reference at all; report this and stop — there is nothing to target.
   - Otherwise, this is the requested child task ID for step 2.
   - If `parent_id`/`work_type` were **not** given: skip this step, there is no requested child task ID.
2. `python3 -m taskweb_pro.cli timer-resolve-stop-target [--requested-child-task-id <id from step 1, if any>]`.
   - Exit `0` → `child_task_id` is the target to stop.
   - Exit `1`, `error_type: NoActiveTimerError` → **stop**. Report plainly that there is no timer being tracked and no task was specified to stop — do not guess a task reference.
3. `python3 -m taskweb_pro.cli taskweb-stop-timer --child-task-id <target from step 2>` (this is `taskweb-pro-azure-integration`'s command). Today this always exits `1` with `error_type: TaskwebUnavailableError`, same as `start-timer` step 3 — report the same way.
4. Only on success (once `taskweb-mcp` is connected): read the currently tracked timer with `python3 -m taskweb_pro.cli timer-get-active`; if its `child_task_id` equals the target stopped in step 3, run `python3 -m taskweb_pro.cli timer-clear-active`. If it differs (the operator explicitly stopped a *different* task than the one tracked as active), **do not clear** — the tracked timer is presumably still running; leave it as is (see techspec.md → Known Risks for why this is a deliberate simplification, not a bug).
5. Report: which child task's timer was targeted and why (explicit reference vs. tracked active timer), and whether the stop actually happened in Taskweb or is pending `taskweb-mcp`.

## Error handling

- A transient Azure DevOps MCP error (timeout, 5xx) may be retried **once**, same as `taskweb-pro-azure-integration`. Any other failure — including all `taskweb_pro.cli` business errors above — is surfaced to the operator immediately, with no further automatic retry.
- Never call any `wit_work_item_write`/`wit_work_item_link_write` action directly from this skill. Every Azure/Taskweb effect goes through `taskweb-pro-azure-integration`'s existing commands.
