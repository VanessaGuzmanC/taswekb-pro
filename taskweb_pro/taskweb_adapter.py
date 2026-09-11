"""Internal Taskweb integration contract.

`taskweb-mcp` is configured but currently disconnected in this
environment (permissions pending on the user's side). This module
defines the contract the orchestrating skill (Task 6.0) programs
against, so Features 1-3 are not blocked on that fix — see
tasks/prd-integracao-azure-taskweb/techspec.md -> Technical
Considerations -> Known Risks.

Assumed real-backend contract (to confirm once `taskweb-mcp` connects):
a `start_timer`, `stop_timer` and `log_time` tool, each keyed by child
task ID, mirroring the shape of `TaskwebAdapter` below.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import NoReturn, Protocol

from taskweb_pro.models import ActionStatus

logger = logging.getLogger(__name__)


class TaskwebUnavailableError(RuntimeError):
    """Raised when a `TaskwebAdapter` method is called with no real backend wired.

    This is the expected error while `taskweb-mcp` remains
    disconnected — it signals "not yet possible", not a bug.
    """


class TaskwebAdapter(Protocol):
    """Contract for Taskweb operations (PRD Feature 4, requirements 4.1-4.3)."""

    def start_timer(self, child_task_id: int) -> ActionStatus: ...

    def stop_timer(self, child_task_id: int) -> ActionStatus: ...

    def log_hours(self, child_task_id: int, start: datetime, end: datetime) -> ActionStatus: ...


class UnavailableTaskwebAdapter:
    """Fail-fast `TaskwebAdapter` used until `taskweb-mcp` connectivity is restored.

    Every method raises `TaskwebUnavailableError` immediately (PRD
    4.4's "confirm success or failure" is satisfied by raising, not by
    returning a silently-failed `ActionStatus`).
    """

    def _unavailable(self, child_task_id: int) -> NoReturn:
        logger.warning("taskweb action rejected: backend unavailable, child_task_id=%s", child_task_id)
        raise TaskwebUnavailableError(
            f"Taskweb integration unavailable (taskweb-mcp disconnected); "
            f"cannot act on child task {child_task_id}"
        )

    def start_timer(self, child_task_id: int) -> ActionStatus:
        self._unavailable(child_task_id)

    def stop_timer(self, child_task_id: int) -> ActionStatus:
        self._unavailable(child_task_id)

    def log_hours(self, child_task_id: int, start: datetime, end: datetime) -> ActionStatus:
        self._unavailable(child_task_id)


class FakeTaskwebAdapter:
    """In-memory fake `TaskwebAdapter` for tests and local development.

    Records every call in `self.calls` so tests can assert on
    interaction without a real Taskweb backend.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple]] = []

    def start_timer(self, child_task_id: int) -> ActionStatus:
        self.calls.append(("start_timer", (child_task_id,)))
        logger.info("taskweb start_timer child_task_id=%s -> success", child_task_id)
        return ActionStatus(success=True, message="timer started", timestamp=datetime.now())

    def stop_timer(self, child_task_id: int) -> ActionStatus:
        self.calls.append(("stop_timer", (child_task_id,)))
        logger.info("taskweb stop_timer child_task_id=%s -> success", child_task_id)
        return ActionStatus(success=True, message="timer stopped", timestamp=datetime.now())

    def log_hours(self, child_task_id: int, start: datetime, end: datetime) -> ActionStatus:
        if end <= start:
            logger.warning(
                "taskweb log_hours child_task_id=%s -> rejected (end <= start)", child_task_id
            )
            return ActionStatus(
                success=False, message="end must be after start", timestamp=datetime.now()
            )
        self.calls.append(("log_hours", (child_task_id, start, end)))
        logger.info("taskweb log_hours child_task_id=%s -> success", child_task_id)
        return ActionStatus(success=True, message="hours logged", timestamp=datetime.now())
