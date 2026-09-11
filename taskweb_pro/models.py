"""Shared data models for the Azure/Taskweb integration module.

See tasks/prd-integracao-azure-taskweb/techspec.md -> Implementation
Design -> Data Models for the authoritative definitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

WorkType = Literal["development", "test", "business_analysis"]


@dataclass(frozen=True, slots=True)
class ChildTask:
    id: int
    parent_id: int
    work_type: WorkType
    assigned_to: str | None
    taskweb_visible: bool


@dataclass(frozen=True, slots=True)
class ActionStatus:
    success: bool
    message: str
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class ActiveTimer:
    child_task_id: int
    parent_id: int
    work_type: WorkType
    user: str
    started_at: datetime
