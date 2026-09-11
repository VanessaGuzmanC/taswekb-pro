# Technical Specification

## Executive Summary

TaskWeb PRO's Azure/Taskweb integration module is delivered as a **Claude Code/Desktop skill** (per user confirmation on the execution model), not a standalone service: Claude itself interprets the operator's free-text command and orchestrates calls to already-connected MCP tools. Azure DevOps access is fully covered by the `mcp__azure-devops__*` tools already available in this environment (`wit_work_item`, `wit_query`, `wit_work_item_write`, `wit_work_item_link_write`) — no custom Azure client is built. Taskweb access depends on `taskweb-mcp`, which is configured but currently disconnected (permissions pending on the user's side); its contract is defined now as an internal interface so Features 1-3 can be built and tested without waiting on that fix. Deterministic decision logic (child-task compatibility matching, reuse-vs-create) is implemented as a small Python helper module invoked by the skill, mirroring the `attach-ado.mjs` pattern already used elsewhere in this skill folder.

## System Architecture

### Component Overview

- **Skill definition** (`SKILL.md` + `references/*.md`): orchestration logic followed by Claude at runtime — receives the parsed intent (parent ID, work type, user) from the upstream text-interpretation module and drives the sequence of MCP calls. No compiled service process.
- **`azure_task_resolver.py`** (new): Python helper invoked via Bash during the skill flow. Encapsulates the compatibility decision (does an existing child task match work type + assignee?) and builds the WIQL filter used to search children of a parent. Pure logic, no network calls of its own — Claude performs the actual MCP calls and passes results in.
- **`taskweb_adapter.py`** (new): defines the internal contract for Taskweb operations (start timer, stop timer, log hours) as a Python `Protocol`. Backed by `taskweb-mcp` once connected; until then, calls through this interface fail fast with a clear "Taskweb integration unavailable" error.
- **Azure DevOps MCP tools** (existing, reused as-is): `wit_work_item` (read parent/children), `wit_query` (WIQL search for existing children), `wit_work_item_write` (`add_child`, `update` for assignment), `wit_work_item_link_write` (`link`, type `child`, to attach a created task to its parent).
- **Data flow:** upstream module → `{parent_id, work_type, user}` → `azure_task_resolver` evaluates reuse vs. create → Claude executes the corresponding Azure MCP calls → resulting child task ID is handed to `taskweb_adapter` for the timer/log action → status returned upstream.

## Implementation Design

### Main Interfaces

```python
class ChildTaskResolver(Protocol):
    def find_compatible_child(
        self, children: list[ChildTask], work_type: str, user: str
    ) -> ChildTask | None: ...

    def build_children_wiql(self, parent_id: int) -> str: ...


class TaskwebAdapter(Protocol):
    def start_timer(self, child_task_id: int) -> ActionStatus: ...
    def stop_timer(self, child_task_id: int) -> ActionStatus: ...
    def log_hours(self, child_task_id: int, start: datetime, end: datetime) -> ActionStatus: ...
```

`ChildTaskResolver` is pure (no I/O): Claude fetches candidates via `wit_query`/`wit_work_item`, passes them in, and the resolver returns the decision. `TaskwebAdapter` isolates the pending external dependency behind one seam.

### Data Models

- `ChildTask`: `id`, `parent_id`, `work_type` (`development` | `test` | `business_analysis`), `assigned_to`, `taskweb_visible: bool`.
- `ActionStatus`: `success: bool`, `message: str`, `timestamp: datetime`.

### API Endpoints

Not applicable — this module has no HTTP surface. It is invoked in-process by the skill orchestration and communicates exclusively through MCP tool calls, consistent with the "no dedicated backend framework" constraint in `architecture/tech_restrictions_context.md.md`.

## Integration Points

- **Azure DevOps** — via the MCP tools already connected in this environment. Query existing children with `wit_query` (action `wiql`); read parent/children details with `wit_work_item` (action `get`/`get_batch`); create with `wit_work_item_write` (action `add_child`); assign with `wit_work_item_write` (action `update`, path `/fields/System.AssignedTo`); link parent/child explicitly with `wit_work_item_link_write` (action `link`, type `child`) when `add_child` does not already establish it. Authentication is handled by the existing MCP session (token-based, per `architecture/tech_restrictions_context.md.md`).
- **Taskweb** — via `taskweb-mcp`, currently disconnected (certificate/permission issue on the user's side). Treated as a blocking external dependency for Feature 4 only; Features 1-3 (Azure-only) are unaffected and can be implemented and tested independently of this fix.
- **Error handling:** MCP failures (Azure or Taskweb) surface as explicit, user-facing messages. A single automatic retry is allowed for transient/network errors; no destructive fallback is attempted, consistent with the "do not modify the parent task" / "do not remove existing child tasks" rules in the PRD.

## Testing Approach

### Unit Tests

`pytest` for `azure_task_resolver.py`'s compatibility matrix (type match × assignee match × existing duplicates) and for `taskweb_adapter.py`'s contract shape. All Azure/Taskweb calls are replaced by fakes — the suite runs without live credentials.

### Integration Tests

Exercised directly against the Azure DevOps MCP tools (already connected) using a disposable PBI/child task in a sandbox project, created for this purpose. Taskweb integration tests are written against the `TaskwebAdapter` interface but marked pending/skipped until `taskweb-mcp` connects.

### E2E Tests

Not applicable in the Playwright sense (no UI). End-to-end validation is a full command → Azure → Taskweb round trip, performed manually once `taskweb-mcp` is reachable.

## Development Sequencing

### Build Order

1. **Consulta de tarefas pai e filhas** (Feature 1) — no external blockers; Azure MCP already available.
2. **Criação de tarefa filha** (Feature 2) — depends on Feature 1's compatibility check.
3. **Atribuição automática** (Feature 3) — depends on Feature 2 for new tasks, reuses Feature 1 for existing ones.
4. **Ações operacionais no Taskweb** (Feature 4) — blocked end-to-end until `taskweb-mcp` connects; the `TaskwebAdapter` interface and its unit tests can be built in parallel against mocks.

### Technical Dependencies

- Azure DevOps MCP (already available in this environment).
- `taskweb-mcp` connectivity — blocking for Feature 4 only (permission fix pending on the user's side).
- No additional infrastructure: no servers, containers, or databases, per `architecture/tech_restrictions_context.md.md`.

## Monitoring and Observability

No existing observability stack applies (`architecture/tech_stack_context.md.md` states no monitoring is planned for the MVP). Observability is limited to structured local logging (Python `logging` module) from `azure_task_resolver.py` and `taskweb_adapter.py`, recording: parent ID received, compatibility decision (reuse/create), child task ID acted upon, and the Taskweb action result. Sufficient for manual diagnosis at this stage.

## Technical Considerations

### Main Decisions

- Run as a Claude Code/Desktop skill rather than a standalone service (user-confirmed) — avoids building and operating a separate MCP client process; Claude already provides both the NLU and the MCP tool execution.
- Reuse the existing Azure DevOps MCP tool set instead of a custom REST client — smaller surface area, and avoids the "unnecessary full backend framework" prohibition in `architecture/tech_restrictions_context.md.md`.
- Define `TaskwebAdapter` as an internal `Protocol` now, deferring the concrete `taskweb-mcp` binding (user-confirmed) — unblocks design and unit testing of Features 1-3 without waiting on the pending permission fix.
- Deterministic matching logic lives in a Python helper module invoked by the skill, mirroring the `attach-ado.mjs` pattern already established in this same skill folder, using Python instead of Node to match this project's chosen stack.
- A child task's `work_type` (development/test/business_analysis) is persisted in Azure via the standard Scrum-process `Microsoft.VSTS.Common.Activity` field (Development/Testing/Requirements), discovered during implementation to be the correct mechanism — not a custom field. Because `wit_work_item_write`'s `add_child` action cannot set this field at creation time, it is set via a follow-up `update` call alongside assignment (see `references/orchestrate.md`).

### Known Risks

- `taskweb-mcp` unavailability blocks Feature 4 end-to-end validation; mitigated by defining the adapter contract independently and mocking it in tests.
- **Identity-format assumption (found via code review, fixed defensively, not yet fully verified):** Azure DevOps's `System.AssignedTo` is an identity reference, commonly rendered as `"Display Name <email>"` rather than a bare email/uniqueName. Comparing it against `user` with plain string equality would make every existing assignment look unassigned, causing `ensure-child-task` to create a duplicate child task on every run (violating PRD 2.4). `azure_task_resolver._identities_match`/`_normalize_identity` now extract the bracketed email before comparing, case-insensitively. This covers the common string shape but **has not been verified against this project's real Azure DevOps API responses** (no sandbox provisioned yet) — if a future response instead returns a structured identity object (e.g. `{"displayName":..., "uniqueName":...}`), the caller must extract the email/uniqueName field itself before building `ChildTask.assigned_to`, since `_normalize_identity` only operates on strings. Re-validate once a sandbox parent task exists.
- No existing codebase or Pharos index: Pharos MCP failed to connect this session (`UNABLE_TO_VERIFY_LEAF_SIGNATURE`), and TaskWeb PRO has no repository yet (`Status: Ideia` in `overview/project_goal_context.md.md`), so there is nothing for Pharos to index regardless of connectivity. This techspec is grounded in the reviewed `.specs`/context documents and in the Azure DevOps MCP schemas inspected directly in this session — re-validate with `map-codebase` once a first implementation exists.
- The "at most one compatible child task per user + work type" rule (from `overview/glossary_context.md.md`) is a business rule, not an Azure-enforced constraint — concurrent commands could create duplicates. Out of scope to prevent for the MVP given single-user, sequential CLI-style usage; flagged for future hardening.

### Conformance with Rules

No `.claude/rules` directory exists in this project yet — there is no project-specific rule set to check against.

### Conformance with Skills

Structured as a sibling to the `phoenix-spec`/`phoenix-bug` skills already present in this Claude Code environment (`SKILL.md` + `references/*.md` + a small helper script), following the same orchestration and attach conventions already established here.

### Relevant and Dependent Files

- `.specs/project/PROJECT.md` — vision, stack, and scope used to ground this spec.
- `overview/project_goal_context.md.md`, `product/scope_features_context.md.md`, `architecture/architecture_definition_context.md.md`, `architecture/tech_restrictions_context.md.md`, `architecture/tech_stack_context.md.md`, `overview/glossary_context.md.md` — source context read in full.
- `tasks/prd-integracao-azure-taskweb/prd.md` — this feature's PRD.
- MCP tool schemas inspected directly in this session: `mcp__azure-devops__wit_work_item`, `mcp__azure-devops__wit_query`, `mcp__azure-devops__wit_work_item_write`, `mcp__azure-devops__wit_work_item_link_write`.
- External reference consulted via Context7: `/modelcontextprotocol/python-sdk` (client connection/tool-call pattern).
- Pharos MCP: connection failed this session (certificate error) — not consulted; not applicable regardless, since no TaskWeb PRO codebase exists yet to index.
