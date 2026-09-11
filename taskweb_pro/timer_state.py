"""Local tracking of the last active timer per user (Módulo 4 — Controle de timer).

Every `taskweb_pro.cli` invocation is a fresh process, so "which child task
currently has an active timer" cannot live in memory between a start and a
later stop command — it has to be persisted to disk. This module is the one
deliberate I/O seam that introduces: a small local JSON file, written
atomically (stdlib `tempfile` + `os.replace`, no third-party locking
library — see tasks/prd-controle-de-timer/techspec.md -> Integration Points
for why `filelock` is unnecessary here).
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from taskweb_pro.models import ActiveTimer

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = Path.home() / ".taskweb_pro" / "active_timer.json"


class NoActiveTimerError(RuntimeError):
    """Raised when a stop command has nothing to stop: no tracked active timer
    and no explicit task reference was given either (PRD requirement 9)."""


def has_conflicting_timer(active: ActiveTimer | None, requested_child_task_id: int) -> bool:
    """Return True when `active` tracks a *different* child task than requested.

    No active timer, or an active timer for the same child task, is not a
    conflict (PRD requirement 4).
    """
    conflict = active is not None and active.child_task_id != requested_child_task_id
    logger.info(
        "conflict check: active=%s requested_child_task_id=%s -> conflict=%s",
        active.child_task_id if active else None,
        requested_child_task_id,
        conflict,
    )
    return conflict


def resolve_stop_target(active: ActiveTimer | None, requested_child_task_id: int | None) -> int:
    """Decide which child task a stop command should target (PRD requirements 7, 8, 9).

    An explicit `requested_child_task_id` always wins over the tracked
    `active` timer. Without one, falls back to `active.child_task_id`.
    Raises `NoActiveTimerError` when neither is available.
    """
    if requested_child_task_id is not None:
        logger.info("stop target resolved from explicit reference: %s", requested_child_task_id)
        return requested_child_task_id
    if active is not None:
        logger.info("stop target resolved from tracked active timer: %s", active.child_task_id)
        return active.child_task_id
    logger.warning("stop requested with no active timer and no explicit reference")
    raise NoActiveTimerError(
        "No active timer is being tracked and no task reference was given to stop"
    )


def active_timer_to_dict(timer: ActiveTimer) -> dict:
    """JSON-serializable representation of `timer` (`started_at` as ISO-8601)."""
    data = asdict(timer)
    data["started_at"] = timer.started_at.isoformat()
    return data


def _timer_from_dict(data: dict) -> ActiveTimer:
    fields = dict(data)
    fields["started_at"] = datetime.fromisoformat(fields["started_at"])
    return ActiveTimer(**fields)


def save_active_timer(timer: ActiveTimer, path: Path | None = None) -> None:
    """Persist `timer` as the tracked active timer, replacing any previous one.

    Written atomically: the new content is written to a temp file in the
    same directory, flushed and fsync'd to disk, then swapped into place
    with `os.replace`, so a crash mid-write — or a crash/power loss right
    after it — can never leave a corrupted or partial file at `path`.
    """
    path = path or DEFAULT_STATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".active_timer-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(active_timer_to_dict(timer), f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        os.unlink(tmp_name)
        raise
    logger.info("saved active timer: child_task_id=%s user=%r", timer.child_task_id, timer.user)


def load_active_timer(path: Path | None = None) -> ActiveTimer | None:
    """Return the tracked active timer, or None if there isn't one.

    A missing file is the normal "no active timer" case. A file that exists
    but fails to parse is treated the same way (never raises) but logged at
    WARNING, since it usually means an earlier write was interrupted outside
    of `save_active_timer`'s own atomic path, or the file was hand-edited.
    """
    path = path or DEFAULT_STATE_PATH
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return _timer_from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        logger.warning("active timer state file at %s is corrupted, treating as absent: %s", path, exc)
        return None


def clear_active_timer(path: Path | None = None) -> None:
    """Remove the tracked active timer, if any. A no-op when already absent."""
    path = path or DEFAULT_STATE_PATH
    path.unlink(missing_ok=True)
    logger.info("cleared active timer state at %s", path)
