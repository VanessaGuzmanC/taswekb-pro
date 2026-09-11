# Technical Specification

## Executive Summary

This module is delivered as a second Claude Code skill (`taskweb-pro-text-interpretation`), sitting in front of the already-implemented `taskweb-pro-azure-integration` skill. Claude performs the actual natural-language extraction (activity description, explicit references, raw time/duration text, start-vs-completed-interval intent) — no NLP library or model is added. Two small, pure Python functions in the existing `taskweb_pro` package normalize that extraction into a strict structured shape: `parse_time_range` (start/end/duration → concrete datetimes) and `classify_work_type` (hint or `None` → one of the three known `WorkType` values, defaulting to `business_analysis` per the user's confirmed decision for daily/meeting-style activities). The result is handed to the existing `taskweb-pro-azure-integration` skill's `ensure-child-task` / timer commands — this module never touches Azure DevOps or Taskweb itself.

## System Architecture

### Component Overview

- **Skill definition** (new: `.claude/skills/taskweb-pro-text-interpretation/SKILL.md` + `references/*.md`): instructs Claude on what raw fields to extract from the operator's sentence and in what order to call the two CLI subcommands below and the existing `taskweb-pro-azure-integration` skill's commands.
- **`taskweb_pro/time_parsing.py`** (new module, same package as the rest of the product): `parse_time_range(start, end, duration_minutes, now)` — pure, no I/O.
- **`taskweb_pro/activity_classification.py`** (new module): `classify_work_type(hint)` — pure, no I/O.
- **`taskweb_pro/cli.py`** (extended, not replaced): two new subcommands, `parse-time-range` and `classify-work-type`, following the exact same JSON-in/JSON-out contract already established for every other subcommand (see `tasks/prd-integracao-azure-taskweb/techspec.md`).
- **Data flow:** operator's free text → Claude extracts `{activity_text, parent_id?, work_type_hint?, start?, end?, duration_minutes?, is_start_of_activity}` → Claude calls `classify-work-type` and (for a completed interval) `parse-time-range` → Claude calls the `taskweb-pro-azure-integration` skill's `resolve-child-task`/`ensure-child-task` with the resulting `{parent_id, work_type, user}`, then either its `log-hours` command (completed interval) or defers to the future Timer Control module (start-of-activity intent) → confirmation is shown to the operator.

## Implementation Design

### Main Interfaces

```python
def parse_time_range(
    start: str | None,    # "HH:MM", 24h
    end: str | None,      # "HH:MM", 24h
    duration_minutes: int | None,
    now: datetime,
) -> tuple[datetime, datetime]: ...

def classify_work_type(hint: str | None) -> WorkType: ...
```

`parse_time_range` accepts exactly one of two shapes — `(start, end)` or `(start, duration_minutes)`/`(None, duration_minutes)` (duration ending at `now`) — and raises `ValueError` on any other combination or an invalid (end <= start) result. `classify_work_type` accepts one of the three known `WorkType` string values or `None` (→ `business_analysis`); any other string raises `ValueError`, mirroring `validate_parent_type`'s style in `azure_task_resolver.py`.

### Data Models

No new dataclass is needed: `WorkType` (already in `taskweb_pro/models.py`) is reused as-is. The tuple return of `parse_time_range` is intentionally not a new model — it is immediately serialized to two ISO-8601 strings at the CLI boundary, the same pattern `taskweb_pro.cli` already uses.

### API Endpoints

Not applicable — same as the first module, this is invoked in-process by the skill orchestration, never over HTTP.

## Integration Points

- **`taskweb-pro-azure-integration` skill** (existing): this module's only "integration point". It calls that skill's `resolve-child-task`, `ensure-child-task`, and (once `taskweb-mcp` connects) `log-hours`/`start-timer`/`stop-timer` commands with the structured output this module produces. No direct MCP calls of any kind happen here.
- **No new external dependency.** Per the web research done for this techspec, `datetime.strptime("%H:%M")` (stdlib) is sufficient once Claude has already normalized the sentence to a strict `HH:MM` 24-hour value — a natural-language date library (`dateutil`, `dateparser`) exists specifically for parsing free-form text directly, which is not this module's job; adding one here would duplicate what Claude already does and violates the "no unnecessary framework" restriction in `architecture/tech_restrictions_context.md.md`.

## Testing Approach

### Unit Tests

`pytest` for `parse_time_range` (start+end, start+duration, duration-only-ends-now, invalid combinations, end<=start) and `classify_work_type` (three known values, `None` → `business_analysis`, unknown string → `ValueError`). No mocks needed — both functions are pure.

### Integration Tests

The CLI subcommands (`parse-time-range`, `classify-work-type`) are exercised the same way `tests/test_orchestration.py` exercises the first module's subcommands — direct calls to `taskweb_pro.cli.main`, asserting the JSON contract.

### E2E Tests

Not applicable in the Playwright sense. The one thing that *cannot* be unit-tested here is Claude's own extraction accuracy (whether it correctly pulls `start`/`end`/`duration` and the start-vs-completed intent out of an arbitrary sentence) — that is inherent to this architecture (Claude, not code, does the NLU) and is validated manually against the example commands in the PRD, not by an automated suite.

## Development Sequencing

### Build Order

1. `classify_work_type` — no dependencies, smallest surface.
2. `parse_time_range` — no dependencies on (1), can be built in parallel.
3. CLI subcommands wiring (1) and (2) into `taskweb_pro/cli.py`.
4. Skill definition (`SKILL.md` + `references/*.md`) composing the CLI subcommands with the existing `taskweb-pro-azure-integration` skill.
5. Manual validation against the PRD's example commands.

### Technical Dependencies

- The already-implemented `taskweb_pro` package and `taskweb-pro-azure-integration` skill (both done).
- None of this module's automated tests depend on `taskweb-mcp`; only the manual end-to-end validation of a "log completed hours" command does, and only for the final Taskweb-side effect (already a known, documented blocker from the first module).

## Monitoring and Observability

Same approach as the first module: stdlib `logging`, no external stack. `parse_time_range` and `classify_work_type` log their input/decision at `INFO`, and the invalid-combination/unknown-hint cases at `WARNING`, via `logging.getLogger(__name__)` in each new module — consistent with `taskweb_pro/logging_config.py`'s existing single `configure_logging()` call.

## Technical Considerations

### Main Decisions

- Extend the existing `taskweb_pro` package and its single `cli.py` rather than create a second package/CLI — keeps one deterministic-logic surface for the whole product, consistent with the first module's own `references/orchestrate.md` calling convention.
- Daily/meeting-style activities with no recognizable development/test signal classify as `business_analysis` — user-confirmed in this session, avoiding a fourth `WorkType` value and any change to the `WORK_TYPE_TO_ACTIVITY` mapping already implemented in `azure_task_resolver.py`.
- No date library is added; `datetime.strptime` is sufficient because Claude, not this module, absorbs all natural-language ambiguity (AM/PM, relative dates, "tomorrow"-style expressions) before handing over a strict `HH:MM` value.
- This module is intentionally scoped to *interpretation only* — it never calls an MCP tool directly, matching the "modules of integration execute actions, other modules interpret" boundary from `architecture/architecture_definition_context.md.md`.

### Known Risks

- Claude's extraction accuracy for edge-case phrasing (e.g. sentences mixing an implicit "this week" reference, or ambiguous AM/PM) is not unit-testable; the PRD's 90% goal can only be validated manually against its example commands, not by an automated gate.
- `parse_time_range` assumes a single calendar day (no cross-midnight interval, no explicit date support) — acceptable for the MVP's same-day logging use case per the PRD, but a real limitation if a user ever reports a shift crossing midnight.
- The "start of activity" vs. "completed interval" distinction (PRD 1.2) depends entirely on Claude correctly reading verb tense/phrasing (e.g. "Empecé a..." vs. "Estuve..."); no deterministic fallback exists if Claude misclassifies this, beyond the general confirmation-before-acting rule already in the PRD (Feature 4).
- No `.specs/codebase/*` documents exist for this repository (no `map-codebase` has been run). This techspec relies instead on direct, current-session knowledge of `taskweb_pro`'s actual code (all of it written earlier in this same conversation) rather than on Pharos or generated codebase docs — Pharos MCP remains disconnected (`UNABLE_TO_VERIFY_LEAF_SIGNATURE`) this session, consistent with the first module's techspec.

### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.

### Conformance with Skills

Adds a second skill, `taskweb-pro-text-interpretation`, as a sibling to the existing `taskweb-pro-azure-integration` — same `SKILL.md` + `references/*.md` shape, and it calls the existing skill's commands rather than duplicating any Azure/Taskweb logic.

### Relevant and Dependent Files

- `tasks/prd-registro-horas-texto-livre/prd.md` — this feature's PRD.
- `tasks/prd-integracao-azure-taskweb/techspec.md` and `.claude/skills/taskweb-pro-azure-integration/` — the existing module this one calls into; read in full to ground the integration point.
- `taskweb_pro/models.py`, `taskweb_pro/azure_task_resolver.py`, `taskweb_pro/cli.py` — existing code inspected directly (Pharos unavailable) to confirm the `WorkType` type, the `WORK_TYPE_TO_ACTIVITY` mapping, and the CLI's JSON contract this module must match.
- `overview/glossary_context.md.md` — source of the three known work-type classifications.
- `architecture/tech_restrictions_context.md.md` — grounds the "no unnecessary framework" decision against adding a date-parsing library.
- Web research consulted: stdlib `datetime.strptime` vs. `dateutil`/`dateparser` scope boundaries; natural-language temporal-ambiguity pitfalls (AM/PM, point-vs-span, implicit references) informing the Known Risks above.
