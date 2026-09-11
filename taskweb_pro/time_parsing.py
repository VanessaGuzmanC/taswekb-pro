"""Time range parsing for free-text time registration.

Claude extracts start/end as strict "HH:MM" 24-hour strings and
duration as a plain integer number of minutes from the operator's
sentence before this runs — this module absorbs no natural-language
ambiguity itself (no AM/PM guessing, no relative dates, no cross-
midnight support). See tasks/prd-registro-horas-texto-livre/techspec.md
-> Known Risks for why a date-parsing library is deliberately not
used here.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _parse_clock(value: str, reference: datetime) -> datetime:
    parsed = datetime.strptime(value, "%H:%M")
    return reference.replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)


def parse_time_range(
    start: str | None,
    end: str | None,
    duration_minutes: int | None,
    now: datetime,
) -> tuple[datetime, datetime]:
    """Resolve a (start, end) datetime pair from a start/end/duration combination.

    Exactly one of these shapes is accepted (PRD 2.1, 2.2, 3.1, 3.2):
      - start + end
      - start + duration_minutes
      - duration_minutes alone (end = now, start = now - duration)

    Any other combination — including both `end` and `duration_minutes`
    given together, or neither given — raises ValueError, as does a
    non-positive duration or a resulting end <= start (PRD 2.3).
    """
    if duration_minutes is not None and (
        not isinstance(duration_minutes, int) or isinstance(duration_minutes, bool)
    ):
        raise TypeError(f"duration_minutes must be an int, got {duration_minutes!r}")
    if duration_minutes is not None and duration_minutes <= 0:
        raise ValueError(f"duration_minutes must be positive, got {duration_minutes!r}")

    if end is not None and duration_minutes is not None:
        raise ValueError("provide either end or duration_minutes, not both")
    if end is None and duration_minutes is None:
        raise ValueError("provide at least one of end or duration_minutes")

    if start is not None:
        start_dt = _parse_clock(start, now)
    else:
        if duration_minutes is None:
            raise ValueError("without start, duration_minutes is required")
        start_dt = now.replace(second=0, microsecond=0) - timedelta(minutes=duration_minutes)

    if end is not None:
        end_dt = _parse_clock(end, now)
    elif start is not None:
        end_dt = start_dt + timedelta(minutes=duration_minutes)
    else:
        end_dt = now.replace(second=0, microsecond=0)

    if end_dt <= start_dt:
        raise ValueError(
            f"end ({end_dt.isoformat()}) must be after start ({start_dt.isoformat()})"
        )

    logger.info("parsed time range: %s -> %s", start_dt.isoformat(), end_dt.isoformat())
    return start_dt, end_dt
