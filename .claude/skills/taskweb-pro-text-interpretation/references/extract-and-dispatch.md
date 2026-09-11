# Extract and dispatch — free-text time registration

## 1. Extract from the operator's sentence

From the sentence, extract:

| Field | Type | Notes |
|---|---|---|
| `activity_text` | string | The raw activity description, always extract it even when an ID is present — used to phrase confirmation questions. |
| `parent_id` | int or `null` | Only when the operator states a PBI/bug ID explicitly (e.g. "PBI 1234112", "bug 123910"). Never invent one. |
| `work_type_hint` | `"development"` \| `"test"` \| `"business_analysis"` \| `null` | Infer from verbs like "desarrollando"/"developing" → `development`, "testeando"/"testing" → `test`. `null` for anything else (daily, reunião, and any activity with no clear signal) — `classify-work-type` will default that to `business_analysis`. Never invent a 4th value. |
| `start` | `"HH:MM"` (24h) or `null` | Convert 12h/AM-PM phrasing to 24h yourself before passing it on — `parse-time-range` only accepts 24h `HH:MM`. |
| `end` | `"HH:MM"` (24h) or `null` | Same conversion rule as `start`. |
| `duration_minutes` | int or `null` | Convert "1 hora" → `60`, "2 horas" → `120`, etc. |
| `is_start_of_activity` | bool | `true` for phrasing that means "I just started X" (e.g. "Empecé a..."), as opposed to a completed interval ("Tuve...", "Estuve..."). |
| `is_stop_of_activity` | bool | `true` for phrasing that means "I just finished/stopped X" (e.g. "Terminé", "Paré", "Terminé el PBI 1234112"). `parent_id` is optional here — a bare "Terminé"/"Paré" with no task reference is the expected common case (see `taskweb-pro-timer-control`). |

Exactly one of `end` / `duration_minutes` should be present for a completed-interval command (never both, per PRD 2.3) — if the sentence is genuinely ambiguous about which, treat it as an ambiguous case (step 3) rather than guessing. Likewise, at most one of `is_start_of_activity` / `is_stop_of_activity` / a completed-interval command (`end` or `duration_minutes` given) should be true for a single sentence — if the phrasing genuinely reads as more than one, treat it as ambiguous rather than guessing.

## 2. Normalize (deterministic — always via the CLI, never by hand)

`start`/`end`/`duration_minutes` are only ever populated for a completed-interval command — `is_start_of_activity`/`is_stop_of_activity` commands never carry a time range (a bare "Empecé"/"Terminé" has none to extract). Run each of the following only when it applies:

```
python3 -m taskweb_pro.cli classify-work-type --hint <work_type_hint or omit for null>
```

Run `classify-work-type` whenever a `work_type` is going to be passed onward at all: always for a completed interval or `is_start_of_activity: true`; for `is_stop_of_activity: true`, only if a `parent_id` was actually extracted (see step 3) — a reference-less stop needs no `work_type`.

```
python3 -m taskweb_pro.cli parse-time-range --start <start?> --end <end?> --duration-minutes <duration_minutes?>
```

Run `parse-time-range` **only** for a completed interval (`is_start_of_activity: false` and `is_stop_of_activity: false`). Calling it for a start/stop command is a bug, not a stricter check: with `start`/`end`/`duration_minutes` all null it always exits `1` (`ValueError: provide at least one of end or duration_minutes`), which would wrongly reject a valid bare "Terminé" as an unparseable time.

Both commands print one JSON object and exit `0` on success, `1` on a handled error (`{"error", "error_type"}`) — parse either way, never treat exit `1` as a crash.

- `classify-work-type` exit `1` (`error_type: ValueError`) means the hint you extracted is not one of the three known values — re-examine the sentence; do not retry with a guessed value.
- `parse-time-range` exit `1` means the interval as extracted is invalid (missing both `end`/`duration`, both given, or end <= start) — surface this to the operator plainly ("no entendí el horario/duración, ¿podés precisarlo?") rather than guessing a fallback.

## 3. Resolve the parent task

- **`is_stop_of_activity: true` and no `parent_id` extracted:** skip this step entirely — a bare "Terminé"/"Paré" with no reference is the expected common case, and `taskweb-pro-timer-control`'s stop flow resolves the target from its own tracked active timer, not from a parent task. Only run the steps below when a reference is actually needed (see step 4).
- Otherwise, if `parent_id` was extracted directly: use it.
- If not: attempt to match `activity_text` against context you have available (e.g. tasks recently discussed in this conversation). If a single confident match exists, propose it to the operator and require an explicit "yes" before proceeding (PRD 4.1) — never proceed silently on an inferred match.
- If no confident match exists (this is the expected outcome for "daily"/"reunião"-style commands with no ID): ask the operator directly for the parent task ID (PRD 4.2). Do not proceed without one — `taskweb-pro-azure-integration`'s `resolve-child-task` always requires a `parent_id`.

## 4. Dispatch

With `parent_id` (when resolved), the `work_type` from step 2, and the requesting user:

- **A completed interval** (`is_start_of_activity: false`, `is_stop_of_activity: false` — the normal case for this module): run `taskweb-pro-azure-integration`'s `ensure-child-task`, then, once the child task is resolved, its Taskweb log-hours action with the `start`/`end` from step 2. Today the Taskweb-side action always fails with `TaskwebUnavailableError` (`taskweb-mcp` disconnected) — report this plainly: "la tarea filha ya está lista/asignada en Azure; el registro en Taskweb queda pendiente hasta que se conecte taskweb-mcp." Do not present this as a full success.
- **`is_start_of_activity: true`** (e.g. "Empecé a desarrollar el PBI 1234112"): hand off to the `taskweb-pro-timer-control` skill's start-timer flow (read its `SKILL.md`) with `parent_id`, `work_type`, and `user` — do not call `ensure-child-task` or any Taskweb action directly here, that skill owns the whole start sequence (child-task resolution, conflict check, and the actual timer start).
- **`is_stop_of_activity: true`** (e.g. "Terminé", "Paré", "Terminé el PBI 1234112"): hand off to the `taskweb-pro-timer-control` skill's stop-timer flow with the requesting user and, only when one was actually resolved in step 3, `parent_id`/`work_type`. Do not force a parent resolution just to have something to pass — the stop flow is designed to work from no reference at all.

## 5. Report

Always state explicitly: what was registered/prepared in Azure, and whether the Taskweb-side effect actually happened or is blocked. Never report a command as fully completed when only the Azure-side steps ran. For start/stop timer commands, this means relaying whatever `taskweb-pro-timer-control` reports (including any conflict confirmation it asks for) rather than summarizing it as a plain success.
