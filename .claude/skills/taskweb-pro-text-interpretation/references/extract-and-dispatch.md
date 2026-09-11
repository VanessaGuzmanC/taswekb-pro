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

Exactly one of `end` / `duration_minutes` should be present for a completed-interval command (never both, per PRD 2.3) — if the sentence is genuinely ambiguous about which, treat it as an ambiguous case (step 3) rather than guessing.

## 2. Normalize (deterministic — always via the CLI, never by hand)

```
python3 -m taskweb_pro.cli classify-work-type --hint <work_type_hint or omit for null>
python3 -m taskweb_pro.cli parse-time-range --start <start?> --end <end?> --duration-minutes <duration_minutes?>
```

Both print one JSON object and exit `0` on success, `1` on a handled error (`{"error", "error_type"}`) — parse either way, never treat exit `1` as a crash.

- `classify-work-type` exit `1` (`error_type: ValueError`) means the hint you extracted is not one of the three known values — re-examine the sentence; do not retry with a guessed value.
- `parse-time-range` exit `1` means the interval as extracted is invalid (missing both `end`/`duration`, both given, or end <= start) — surface this to the operator plainly ("no entendí el horario/duración, ¿podés precisarlo?") rather than guessing a fallback.

## 3. Resolve the parent task

- If `parent_id` was extracted directly: use it.
- If not: attempt to match `activity_text` against context you have available (e.g. tasks recently discussed in this conversation). If a single confident match exists, propose it to the operator and require an explicit "yes" before proceeding (PRD 4.1) — never proceed silently on an inferred match.
- If no confident match exists (this is the expected outcome for "daily"/"reunião"-style commands with no ID): ask the operator directly for the parent task ID (PRD 4.2). Do not proceed without one — `taskweb-pro-azure-integration`'s `resolve-child-task` always requires a `parent_id`.

## 4. Dispatch to `taskweb-pro-azure-integration`

With `parent_id`, the `work_type` from step 2, and the requesting user:

- **`is_start_of_activity: false`** (a completed interval — the normal case for this module): run that skill's `ensure-child-task`, then, once the child task is resolved, its Taskweb log-hours action with the `start`/`end` from step 2. Today the Taskweb-side action always fails with `TaskwebUnavailableError` (`taskweb-mcp` disconnected) — report this plainly: "la tarea filha ya está lista/asignada en Azure; el registro en Taskweb queda pendiente hasta que se conecte taskweb-mcp." Do not present this as a full success.
- **`is_start_of_activity: true`** (e.g. "Empecé a desarrollar el PBI 1234112"): this module has no Timer Control module to hand off to yet — it does not exist in this codebase. Run `ensure-child-task` (so the child task is at least ready and assigned) and then tell the operator plainly that starting a timer from this phrasing is not supported yet, rather than silently doing nothing or misreporting success.

## 5. Report

Always state explicitly: what was registered/prepared in Azure, and whether the Taskweb-side effect actually happened or is blocked. Never report a command as fully completed when only the Azure-side steps ran.
