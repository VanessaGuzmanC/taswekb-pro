# Service Spec

> Source: Pharos MCP consultation attempted during techspec generation for `tasks/prd-registro-horas-texto-livre/`. Pharos MCP remains disconnected in this session (`UNABLE_TO_VERIFY_LEAF_SIGNATURE`), consistent with `tasks/prd-integracao-azure-taskweb/servicespec.md`. All entries below come from direct inspection of the existing `taskweb_pro` package/skill (written earlier in this same session) and the reviewed `.specs`/context documents, not from Pharos.

## Impacted Services

| # | Service Name | Pharos Node ID | Impact Type | Reason / Touch Point | Pharos Tool Source |
|---|---|---|---|---|---|
| — | — | — | — | No services returned — Pharos unreachable this session | N/A |

## Services not covered by Pharos

1. **Azure DevOps** — Transitively impacted: this module never calls it directly, but every command it produces is consumed by the `taskweb-pro-azure-integration` skill, which does call it (see that module's `servicespec.md`). Not returned by Pharos for the same connectivity reason as before.
2. **Taskweb** — Transitively impacted, same reasoning as Azure DevOps above: this module's "start of activity"/"completed interval" output eventually reaches Taskweb only through the existing skill, once `taskweb-mcp` connects.
3. **Claude (Code/Desktop runtime)** — Direct: this module's core function (extracting activity/time/intent from free text) *is* Claude's own interpretation, executed as this new skill. Not a discrete service in the Pharos sense, same as documented in the first module's service spec.
4. **`taskweb-pro-azure-integration` (this repository's own first module)** — Direct dependency, in-repo: this module calls its `resolve-child-task` / `ensure-child-task` / (pending) `log-hours`/`start-timer`/`stop-timer` commands. Not an "external service" in the Pharos sense (same codebase, same repository, no network boundary) — listed here for completeness since it is the one thing this module directly depends on and could break if that skill's CLI contract changes.

## Notes

- Total services impacted: 2 external systems (Azure DevOps, Taskweb, both transitive) + Claude Code/Desktop as execution runtime + 1 in-repo dependency (the first module's skill/CLI).
- Direct changes: 0 external systems — this module adds two pure Python functions and two CLI subcommands to the existing `taskweb_pro` package; it does not modify `azure_task_resolver.py`, `taskweb_adapter.py`, or any existing subcommand's behavior.
- Transitive / indirect impacts: Azure DevOps and Taskweb, both only through the existing first module — see above.
- Cross-service data flows detected: none via Pharos (unreachable). Manually identified flow: this module's structured output (`parent_id`, `work_type`, start/end datetimes) becomes the direct input to the first module's `ensure-child-task`/`log-hours` commands.
- Messaging topology touched: none — no Kafka/ActiveMQ/listeners, no persistence or async processing, consistent with `architecture/tech_stack_context.md.md`.
