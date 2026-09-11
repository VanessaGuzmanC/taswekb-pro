# Service Spec

> Source: Pharos MCP consultation attempted during techspec generation for `tasks/prd-integracao-azure-taskweb/`. Pharos MCP failed to connect in this session (`UNABLE_TO_VERIFY_LEAF_SIGNATURE`) — treated as a connection failure, not as an assertion that no capability exists. Additionally, TaskWeb PRO has no existing repository yet (`Status: Ideia`, `overview/project_goal_context.md.md`), so no codebase exists for Pharos to index regardless of connectivity. All entries below come from direct inspection of MCP tool schemas and the reviewed `.specs`/context documents, not from Pharos.

## Impacted Services

| # | Service Name | Pharos Node ID | Impact Type | Reason / Touch Point | Pharos Tool Source |
|---|---|---|---|---|---|
| — | — | — | — | No services returned — Pharos unreachable and no indexed codebase exists for this greenfield project | N/A |

## Services not covered by Pharos

1. **Azure DevOps** — In scope per PRD Features 1-3 (query, create, and assign child tasks). Not returned by Pharos because Pharos was unreachable this session and no TaskWeb PRO codebase exists to index. Accessed instead via the already-connected `mcp__azure-devops__*` MCP tools (`wit_work_item`, `wit_query`, `wit_work_item_write`, `wit_work_item_link_write`), confirmed directly in this session. Indexing follow-up: once a TaskWeb PRO repository exists and is registered with Pharos, re-run project analysis to confirm this dependency surfaces via `find_external_systems`/`find_service_dependencies`.
2. **Taskweb** — In scope per PRD Feature 4 (timer start/stop, hour logging). Not returned by Pharos for the same reason above, and additionally its dedicated MCP (`taskweb-mcp`) is itself disconnected in this environment (permissions pending on the user's side). Indexing follow-up: same as above, plus resolving `taskweb-mcp` connectivity is a prerequisite for any real (non-mocked) integration test.
3. **Claude (Code/Desktop runtime)** — In scope as the interpretation/orchestration layer (per `architecture/architecture_definition_context.md.md` and the user-confirmed execution model). Not a discrete "service" in the Pharos sense — there is no service code to index; Claude Code/Desktop itself is the runtime the skill executes in.

## Notes

- Total services impacted: 2 external systems (Azure DevOps, Taskweb) + Claude Code/Desktop as execution runtime (not counted as an external service).
- Direct changes: 0 — no new service infrastructure is created; both external systems are accessed via existing or pending MCP tool connections.
- Transitive / indirect impacts: 0 identified — the MVP has no other internal services.
- Cross-service data flows detected: none via Pharos (unreachable). Manually identified flow, per `overview/glossary_context.md.md`: a child task's state in Azure DevOps (created, assigned) determines its visibility and usability for time apontamento in Taskweb.
- Messaging topology touched: none — no Kafka/ActiveMQ/listeners, no persistence or async processing in this MVP, per `architecture/tech_stack_context.md.md`.
