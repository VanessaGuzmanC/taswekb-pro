"""Work-type classification for free-text time registration.

Claude extracts a work-type hint from the operator's sentence (one of
the three known `WorkType` values, or `None` when no development/test
signal is present — e.g. "daily", "reunião"). This module applies the
one business rule the PRD adds on top of that: no hint classifies as
`business_analysis` (user-confirmed decision, see
tasks/prd-registro-horas-texto-livre/techspec.md -> Main Decisions).
"""

from __future__ import annotations

import logging
from typing import get_args

from taskweb_pro.models import WorkType

logger = logging.getLogger(__name__)

_KNOWN_WORK_TYPES: frozenset[str] = frozenset(get_args(WorkType))
_DEFAULT_WORK_TYPE: WorkType = "business_analysis"


def classify_work_type(hint: str | None) -> WorkType:
    """Return the `WorkType` for a hint extracted from free text (PRD 1.4).

    `hint` must be one of the three known `WorkType` values, or `None`
    (daily/meeting-style activity with no development/test signal,
    which defaults to `business_analysis`). Any other string raises
    ValueError rather than silently defaulting.
    """
    if hint is None:
        logger.info("no work_type hint -> defaulting to %r", _DEFAULT_WORK_TYPE)
        return _DEFAULT_WORK_TYPE
    if hint not in _KNOWN_WORK_TYPES:
        logger.warning("rejected unknown work_type hint=%r", hint)
        raise ValueError(
            f"Unknown work_type hint {hint!r}; expected one of {sorted(_KNOWN_WORK_TYPES)} or None"
        )
    logger.info("work_type hint=%r accepted", hint)
    return hint  # type: ignore[return-value]
