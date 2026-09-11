# Service Spec

> Source: Pharos MCP consultation attempted during techspec generation for `tasks/prd-controle-de-timer/`. Pharos MCP remains disconnected in this session (`CONNECT_TIMEOUT`), consistent with `tasks/prd-integracao-azure-taskweb/servicespec.md` and `tasks/prd-registro-horas-texto-livre/servicespec.md`. All entries below come from direct inspection of the existing `taskweb_pro` package/skills (read in full this session) and the reviewed `.specs`/context documents, not from Pharos.

## Impacted Services

| # | Service Name | Pharos Node ID | Impact Type | Reason / Touch Point | Pharos Tool Source |
|---|---|---|---|---|---|
| — | — | — | — | No services returned — Pharos unreachable this session | N/A |

## Services not covered by Pharos

1. **Azure DevOps** — Transitively impacted: this module never calls it directly, but every child-task resolution/creation it triggers goes through `taskweb-pro-azure-integration`, which does call it (see that module's `servicespec.md`). Not returned by Pharos for the same connectivity reason as before.
2. **Taskweb** — Direct, but currently blocked: this module's whole purpose is to call `taskweb-pro-azure-integration`'s `start-timer`/`stop-timer` commands, which act on Taskweb once `taskweb-mcp` connects. Not returned by Pharos (unreachable), and Taskweb itself has no MCP connectivity in this environment yet either.
3. **Claude (Code/Desktop runtime)** — Direct: the free-text recognition of start/stop intent (extending `taskweb-pro-text-interpretation`'s conventions) *is* Claude's own interpretation, executed as this new skill, same as documented in the other two modules' service specs.
4. **`taskweb-pro-azure-integration` (this repository's own first module)** — Direct dependency, in-repo: this module calls its `ensure-child-task`, `resolve-child-task`, `taskweb-start-timer`, and `taskweb-stop-timer` commands verbatim. Not an "external service" in the Pharos sense (same codebase, same repository, no network boundary) — listed for completeness since a change to that skill's CLI contract could break this module.
5. **`taskweb-pro-text-interpretation` (this repository's own second module)** — Direct dependency, in-repo: this module reuses/extends its free-text extraction conventions (the existing `is_start_of_activity` signal, plus a new stop-intent signal). Same in-repo caveat as (4).
6. **Local filesystem (new in this module)** — Direct, in-repo, not a Pharos-tracked "service": the JSON state file at `~/.taskweb_pro/active_timer.json` that tracks the last active timer per user. Listed here because it is the one genuinely new I/O surface this module introduces (no database, no network call).

## Notes

- Total services impacted: 2 external systems (Azure DevOps, Taskweb — both only reachable transitively/through existing skills) + Claude Code/Desktop as execution runtime + 2 in-repo skill dependencies (Modules 1 and 3) + 1 new local-filesystem surface (the active-timer state file).
- Direct changes: 0 external systems — this module adds one dataclass, one new pure/I/O module, and five CLI subcommands to the existing `taskweb_pro` package; it does not modify `azure_task_resolver.py` or `taskweb_adapter.py`'s existing behavior.
- Transitive / indirect impacts: Azure DevOps and Taskweb, both only through `taskweb-pro-azure-integration`'s existing commands — see above.
- Cross-service data flows detected: none via Pharos (unreachable). Manually identified flow: text-interpretation's extracted `{parent_id, work_type, user, is_start_of_activity | is_stop_of_activity}` → this module's conflict/stop-target decision → `taskweb-pro-azure-integration`'s `ensure-child-task`/`resolve-child-task` and `taskweb-start-timer`/`taskweb-stop-timer` → local state file updated on success.
- Messaging topology touched: none — no Kafka/ActiveMQ/listeners, no database, consistent with `architecture/tech_stack_context.md.md`.
