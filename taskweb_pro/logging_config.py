"""Local logging setup for TaskWeb PRO.

No external observability stack is planned for the MVP (see
architecture/tech_stack_context.md.md). Feature modules call
`logging.getLogger(__name__)` and rely on this configuration for
manual diagnosis; see techspec.md -> Monitoring and Observability.
"""

from __future__ import annotations

import logging

_CONFIGURED = False


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root logger once, idempotently.

    Safe to call multiple times (e.g. from tests) without duplicating
    handlers or log lines.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    _CONFIGURED = True
