# Orchestrate — Azure/Taskweb integration flow

Inputs for every command below: `parent_id` (int), `work_type` (`development` | `test` | `business_analysis`), `user` (Azure DevOps unique name/email of the requester). These normally arrive already parsed from an upstream module (text interpretation); until that module exists, accept them directly from the operator.

All `python3 -m taskweb_pro.cli` calls print one JSON object to stdout and exit `0` on success, `1` on a handled business error (`{"error": ..., "error_type": ...}`). Parse the JSON either way — never treat a non-zero exit as a crash before checking for that shape.

## `resolve-child-task`

1. `mcp__azure-devops__wit_work_item` (`action: "get"`, `id: parent_id`, `fields: ["System.WorkItemType", "System.Title"]`) — read the parent.
2. `python3 -m taskweb_pro.cli validate-parent-type --work-item-type "<System.WorkItemType>"`. On exit `1`, stop and surface the error to the operator — do not proceed.
3. `python3 -m taskweb_pro.cli build-children-wiql --parent-id <parent_id>` — get the WIQL string.
4. `mcp__azure-devops__wit_query` (`action: "wiql"`, `wiql: "<the string from step 3>"`) — get candidate child IDs.
5. `mcp__azure-devops__wit_work_item` (`action: "get_batch"`, `ids: [...]`, `fields: ["System.Id","System.Parent","Microsoft.VSTS.Common.Activity","System.AssignedTo"]`) — fetch full child details. `Microsoft.VSTS.Common.Activity` is the Scrum process's standard Task-classification field — this is where a child task's work_type actually lives in Azure, not a custom field. For each result, convert its Activity value with `python3 -m taskweb_pro.cli activity-to-work-type --activity "<value>"` before building the `ChildTask` shape (`id`, `parent_id`, `work_type`, `assigned_to`, `taskweb_visible`); on `error_type: UnknownActivityError` (the task carries an Activity this flow never wrote, e.g. "Design"), treat it as **not compatible** rather than failing the whole query — exclude it from the list passed to `find-compatible-child` and report it as an aside. Pass `System.AssignedTo` through as-is (as a plain string) into `assigned_to` — do **not** pre-process it; `find-compatible-child`/`needs-assignment` already normalize the common `"Display Name <email>"` shape internally. If a response instead returns a structured identity object (not a string) for this field, extract its `uniqueName`/`email` yourself before building `ChildTask` — the normalization is string-only (see `azure_task_resolver.py`'s `_normalize_identity`, flagged as unverified against this project's real API in `techspec.md` → Known Risks). `taskweb_visible` is not knowable from Azure alone, pass `false` as a placeholder here — it is not used by `find-compatible-child`.
6. `python3 -m taskweb_pro.cli find-compatible-child --children-json '<JSON array from step 5>' --work-type <work_type> --user <user>`.
   - Exit `0`, `match: null` → no compatible child task exists.
   - Exit `0`, `match: {...}` → this is the compatible child task; report its `id`.
   - Exit `1`, `error_type: AmbiguousChildTaskError` → **stop**. Report both conflicting task IDs to the operator per the message; do not guess which one to use.

## `ensure-child-task`

1. Run `resolve-child-task` above.
2. If a match was found, skip to step 5 (nothing to create).
3. If no match: re-run steps 3-6 of `resolve-child-task` **once more** (the duplicate re-check required by PRD 2.4) immediately before writing. If this second check now finds a match, use it and skip creation — do not create a duplicate.
4. Still no match:
   a. `python3 -m taskweb_pro.cli build-child-task-item --parent-title "<parent's System.Title>"`.
   b. `mcp__azure-devops__wit_work_item_write` (`action: "add_child"`, `parentId: parent_id`, `workItemType: "Task"`, `items: [<item from 4a>]`) — creates the child task **and** links it to the parent in one call. Do not also call `wit_work_item_link_write` for this link.
   c. Read the new child task's ID from the response.
   d. `add_child`'s `items` schema cannot set the Activity field, so the child is created **without** its work_type classification persisted yet. Immediately run `python3 -m taskweb_pro.cli build-activity-update --work-type <work_type>` and apply it in the assignment update below (step 5b) — do not leave a newly created child task without its Activity set, or a later `resolve-child-task` will not recognize it.
5. With the resolved child task ID (from a match or from creation):
   a. `python3 -m taskweb_pro.cli needs-assignment --child-json '<the child, as ChildTask JSON>' --user <user>`.
   b. Build the `updates` array for a single follow-up `mcp__azure-devops__wit_work_item_write` (`action: "update"`, `id: <child id>`) call: always include the result of `python3 -m taskweb_pro.cli build-assignment-update --user <user>` when `needs_assignment: true` (step 5a); when the child was just created in step 4, also include the result of step 4d's `build-activity-update`. Send both in the same `updates` array when both apply — one `update` call, not two.
6. Report the final child task ID and whether it was reused or created.

## `start-timer` / `stop-timer` / `log-hours`

Given an already-resolved child task ID (from `ensure-child-task`):

```
python3 -m taskweb_pro.cli taskweb-start-timer --child-task-id <id>
python3 -m taskweb_pro.cli taskweb-stop-timer  --child-task-id <id>
python3 -m taskweb_pro.cli taskweb-log-hours   --child-task-id <id> --start <ISO 8601> --end <ISO 8601>
```

Today these always exit `1` with `error_type: TaskwebUnavailableError` — `taskweb-mcp` is disconnected in this environment. Report this plainly to the operator ("Taskweb integration unavailable — the Azure-side steps above already completed") rather than retrying in a loop.

## Error handling

- A transient Azure DevOps MCP error (timeout, 5xx) may be retried **once**. Any other failure — including all `taskweb_pro.cli` business errors above — is surfaced to the operator immediately, with no further automatic retry.
- Never call any `wit_work_item_write` action that would modify the parent task's own fields, and never call an action that removes a child task. These operations are out of scope for this skill under every command above.
