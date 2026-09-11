"""TaskWeb PRO — Azure/Taskweb integration module.

Deterministic decision logic invoked by the TaskWeb PRO Claude Code skill.
Claude performs the actual Azure DevOps and Taskweb MCP tool calls; this
package only holds pure logic and internal interfaces (see techspec.md
under tasks/prd-integracao-azure-taskweb/).
"""

from taskweb_pro.logging_config import configure_logging

configure_logging()
