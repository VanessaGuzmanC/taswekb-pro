# Technical Specification

## Executive Summary

This module is delivered as a third Claude Code skill, `taskweb-pro-timer-control`, sitting alongside — and composing — the two already-implemented skills: `taskweb-pro-azure-integration` (child-task resolution/creation and the Taskweb `start-timer`/`stop-timer` actions) and `taskweb-pro-text-interpretation` (free-text extraction, which already produces an `is_start_of_activity` signal deferred to this module per its own techspec). No new external dependency and no new NLU logic beyond extending the existing text-interpretation conventions to also recognize a stop intent. The one genuinely new piece of state this module introduces is "which child task currently has an active timer for this user" — since every CLI invocation is a fresh process, this must be persisted to a small local JSON file (atomic write via stdlib `tempfile` + `os.replace`, per user-confirmed design: single active timer per user, no database, no new dependency). Two pure decision functions (conflict detection on start, stop-target resolution) plus that file-backed state make up the only new module, `taskweb_pro/timer_state.py`.

## System Architecture

### Component Overview

- **Skill definition** (new: `.claude/skills/taskweb-pro-timer-control/SKILL.md` + `references/orchestrate.md`): orchestrates a start-timer or stop-timer command end to end, calling into the other two skills' commands and the new CLI subcommands below. No compiled service process, same as the other two skills.
- **`taskweb_pro/models.py`** (extended): adds the `ActiveTimer` dataclass (`child_task_id`, `parent_id`, `work_type`, `user`, `started_at`) alongside the existing `ChildTask`/`ActionStatus`.
- **`taskweb_pro/timer_state.py`** (new module): pure decision functions — `has_conflicting_timer(active, requested_child_task_id)` and `resolve_stop_target(active, requested_child_task_id)` — plus the local persistence seam: `load_active_timer(path)`, `save_active_timer(timer, path)`, `clear_active_timer(path)`. The persistence functions are the one deliberate I/O seam in this module (mirroring how `taskweb_adapter.py` is the isolated seam for the pending Taskweb backend).
- **`taskweb_pro/cli.py`** (extended, not replaced): four new subcommands — `timer-get-active`, `timer-check-conflict`, `timer-save-active`, `timer-resolve-stop-target`, `timer-clear-active` — following the exact same JSON-in/JSON-out contract already established for every other subcommand.
- **Existing skills, reused as-is:** `taskweb-pro-azure-integration`'s `ensure-child-task` (start flow, full reuse-or-create) and `resolve-child-task` (stop flow, reuse-only — never create just to stop a timer), plus its `start-timer`/`stop-timer` commands.
- **Data flow (start):** operator's free text → text-interpretation extracts `{parent_id, work_type_hint, user, is_start_of_activity: true}` → `classify-work-type` → `ensure-child-task` resolves/creates the child task → `timer-check-conflict` against the locally tracked active timer → if conflicting, Claude asks for confirmation before proceeding → `taskweb-start-timer` → on success, `timer-save-active` persists the new tracked timer.
- **Data flow (stop):** operator's free text → text-interpretation extracts `{parent_id?, work_type_hint?, user, is_stop_of_activity: true}` (`parent_id` optional) → if a reference was given, `resolve-child-task` resolves its child task ID; otherwise none → `timer-resolve-stop-target` decides the child task ID to stop (explicit reference wins; otherwise the tracked active timer; error if neither exists) → `taskweb-stop-timer` → on success, `timer-clear-active` **only if** the stopped child task ID matches the currently tracked one (see Known Risks).

## Implementation Design

### Main Interfaces

```python
def has_conflicting_timer(
    active: ActiveTimer | None, requested_child_task_id: int
) -> bool: ...

def resolve_stop_target(
    active: ActiveTimer | None, requested_child_task_id: int | None
) -> int: ...  # raises NoActiveTimerError if both are absent

def load_active_timer(path: Path = DEFAULT_STATE_PATH) -> ActiveTimer | None: ...
def save_active_timer(timer: ActiveTimer, path: Path = DEFAULT_STATE_PATH) -> None: ...
def clear_active_timer(path: Path = DEFAULT_STATE_PATH) -> None: ...
```

`has_conflicting_timer` and `resolve_stop_target` are pure and total (no I/O, no exceptions besides the documented `NoActiveTimerError`). `load_active_timer`/`save_active_timer`/`clear_active_timer` isolate the only local-disk I/O this module performs.

### Data Models

- `ActiveTimer` (new, in `taskweb_pro/models.py`): `child_task_id: int`, `parent_id: int`, `work_type: WorkType`, `user: str`, `started_at: datetime`. Mirrors `ChildTask`'s style (`frozen=True, slots=True`).
- `NoActiveTimerError(RuntimeError)` (new, in `timer_state.py`): raised by `resolve_stop_target` when there is nothing to stop and no explicit reference was given — satisfies PRD requirement 9 ("clear message, not a silent no-op").
- On-disk shape (`DEFAULT_STATE_PATH = Path.home() / ".taskweb_pro" / "active_timer.json"`): the `ActiveTimer` fields as a flat JSON object, `started_at` as an ISO-8601 string. A missing file or a file that fails to parse is treated as "no active timer" (logged at `WARNING` in the corrupted case, not raised — see Known Risks).

### API Endpoints

Not applicable — same as the other two modules, invoked in-process by skill orchestration via Bash, never over HTTP.

## Integration Points

- **`taskweb-pro-azure-integration` skill** (existing, unmodified): this module's only Azure/Taskweb touch point. It calls `ensure-child-task` (start flow), `resolve-child-task` (stop flow, when an explicit reference is given), `taskweb-start-timer`, and `taskweb-stop-timer` — no direct MCP calls of any kind happen here, and none of that skill's own logic is duplicated.
- **`taskweb-pro-text-interpretation` skill** (existing, extended): already emits `is_start_of_activity` per its own techspec; this module's skill extends that convention with a stop-intent signal ("Terminé", "Paré", with an optional PBI/bug reference) so `taskweb-pro-timer-control` has a single, consistent place to look for both.
- **No new external dependency.** Per the web research done for this techspec, the standard `tempfile.mkstemp()` + `os.replace()` pattern (both stdlib) is sufficient for a crash-safe, all-or-nothing state-file write; a locking library such as `filelock` exists specifically to arbitrate *genuinely concurrent* multi-process writers, which does not apply to this single-user, sequential CLI-style usage (same assumption already accepted for the "at most one compatible child task" rule in `tasks/prd-integracao-azure-taskweb/techspec.md` → Known Risks).

## Testing Approach

### Unit Tests

`pytest` for `timer_state.py`'s pure functions: `has_conflicting_timer` (no active timer, active timer for the same child task, active timer for a different child task) and `resolve_stop_target` (active + no explicit reference, active + matching explicit reference, active + differing explicit reference, no active + explicit reference, no active + no reference → `NoActiveTimerError`). The persistence functions are tested with `tmp_path`: round-trip save/load, missing file → `None`, corrupted/invalid JSON → `None` with a logged warning, and that a save is atomic (no partial file observable, verified by asserting the temp file created during the write is never the one read back).

### Integration Tests

The five new CLI subcommands are exercised the same way `tests/test_orchestration.py` exercises the first module's subcommands — direct calls to `taskweb_pro.cli.main`, asserting the JSON contract, with a `tmp_path`-backed state file.

### E2E Tests

Not applicable in the Playwright sense. As with the other two modules, the full start-timer/stop-timer round trip against a real Taskweb backend cannot be automated until `taskweb-mcp` connects; validated manually against the PRD's example commands once that dependency clears.

## Development Sequencing

### Build Order

1. `ActiveTimer` dataclass in `taskweb_pro/models.py` — no dependencies.
2. `timer_state.py`'s pure functions (`has_conflicting_timer`, `resolve_stop_target`) — depend only on (1).
3. `timer_state.py`'s persistence functions (`load_active_timer`/`save_active_timer`/`clear_active_timer`) — depend only on (1), can be built in parallel with (2).
4. CLI subcommand wiring into `taskweb_pro/cli.py` — depends on (2) and (3).
5. Skill definition (`taskweb-pro-timer-control`) composing (4) with the existing `taskweb-pro-azure-integration` and `taskweb-pro-text-interpretation` skills.
6. Manual validation against the PRD's example commands and full test suite consolidation.

### Technical Dependencies

- The already-implemented `taskweb_pro` package and both existing skills (all done).
- None of this module's automated tests depend on `taskweb-mcp`; only the manual end-to-end validation of an actual start/stop round trip does — the same already-documented blocker carried over from Module 1.

## Monitoring and Observability

Same approach as the other two modules: stdlib `logging`, no external stack. `timer_state.py` logs, at `INFO`: conflict-check outcome, stop-target resolution outcome, and every state-file write/clear; at `WARNING`: a corrupted state file being treated as absent, and a stop request with no active timer and no explicit reference (before the `NoActiveTimerError` is raised).

## Technical Considerations

### Main Decisions

- Track "the last active timer per user" as a small local JSON file, written atomically via `tempfile.mkstemp` + `os.replace` (stdlib only) rather than a third-party locking library — matches the project's "no database, no unnecessary dependency" constraints and needs no real concurrency guarantee given single-user, sequential CLI-style usage.
- An explicit task reference on the stop command always wins over the tracked "last active timer" (PRD requirement 8) — never silently guesses when the user has been unambiguous.
- Starting a new timer while a different one is tracked as active never silently overwrites the tracked state: the deterministic layer only computes the conflict flag (`has_conflicting_timer`); pausing and asking the user is the orchestrating skill's responsibility, consistent with the "confirmação assistida" pattern already established in the text-interpretation module.
- Stopping a timer that differs from the currently tracked one (explicit-reference case) leaves the tracked state untouched rather than guessing whether to clear or update it — a deliberate simplification, not an oversight (see Known Risks).
- `ensure-child-task`/`resolve-child-task` from `taskweb-pro-azure-integration` are reused verbatim for locating/creating the child task; no duplicate resolution logic is added here, matching the precedent already set by the text-interpretation module.

### Known Risks

- `taskweb-mcp` unavailability still blocks Feature 1/2 end-to-end validation for this module, exactly as for the other two — mitigated the same way, by testing everything up to the Taskweb call itself.
- The local state file is single-user, single-machine: it does not sync across machines or checkouts, and does not reconcile with the Taskweb backend's own notion of an active timer. If a timer is started or stopped directly in the Taskweb UI (bypassing TaskWeb PRO), the local file silently drifts from the truth — the PRD explicitly places this reconciliation out of scope; the only mitigation is the explicit-reference fallback on stop.
- A corrupted or unreadable state file is treated as "no active timer" rather than a hard failure, to avoid a single bad write permanently blocking the (already-optional) stop-without-reference convenience — logged at `WARNING` so a recurring corruption is still visible, but this could mask a real bug in the write path if it happens repeatedly.
- Stopping an explicitly-referenced timer that differs from the tracked "last active" one leaves the tracked state unchanged; if that untracked timer was in fact still running, the next reference-less stop will target the wrong (already-stopped) child task and fail with `NoActiveTimerError`'s sibling case or a Taskweb-side no-op — acceptable for the MVP per the PRD's explicit "no multiple simultaneous timers" scope, but worth re-visiting if real usage shows this happening often.
- No `.specs/codebase/*` documents exist for this repository beyond `.specs/project/PROJECT.md` (no `map-codebase` has been run). Pharos MCP failed to connect this session (`CONNECT_TIMEOUT`), consistent with both prior modules' techspecs — this document is grounded directly in the current `taskweb_pro` codebase (read in full this session) and in the `.specs`/context documents, not in Pharos or generated codebase docs.

### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.

### Conformance with Skills

Adds a third skill, `taskweb-pro-timer-control`, as a sibling to the existing `taskweb-pro-azure-integration` and `taskweb-pro-text-interpretation` — same `SKILL.md` + `references/*.md` shape, composing both existing skills' commands rather than duplicating any Azure/Taskweb or text-extraction logic.

### Relevant and Dependent Files

- `tasks/prd-controle-de-timer/prd.md` — this feature's PRD.
- `tasks/prd-integracao-azure-taskweb/techspec.md`, `.claude/skills/taskweb-pro-azure-integration/` — the existing module this one calls into for child-task resolution and the Taskweb actions; read in full to ground reuse.
- `tasks/prd-registro-horas-texto-livre/techspec.md`, `.claude/skills/taskweb-pro-text-interpretation/` — the existing text-interpretation module whose `is_start_of_activity` signal this module consumes, and whose extraction conventions the new stop-intent extends.
- `taskweb_pro/models.py`, `taskweb_pro/azure_task_resolver.py`, `taskweb_pro/taskweb_adapter.py`, `taskweb_pro/cli.py` — existing code inspected directly (Pharos unavailable) to confirm the `WorkType`/`ChildTask` shapes, the `TaskwebAdapter` contract already exposing `start_timer`/`stop_timer`, and the CLI's JSON contract this module must match.
- `architecture/tech_restrictions_context.md.md` — grounds the "no database, no unnecessary dependency" decision behind the local-file design.
- `product/scope_features_context.md.md` (Módulo 4 — "Controle de timer") — source of the two features this techspec implements.
- Web research consulted: `tempfile` + `os.replace` atomic-write pattern for crash-safe local JSON state (stdlib-only); `filelock`'s intended use case (genuinely concurrent multi-process writers) confirming it is unnecessary here.
- Pharos MCP: connection failed this session (`CONNECT_TIMEOUT`) — not consulted, consistent with both prior modules' techspecs.
