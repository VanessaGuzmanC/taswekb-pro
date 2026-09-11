"""Unit tests for Task 2.0 — work-type classification (`classify_work_type`)."""

import pytest

from taskweb_pro.activity_classification import classify_work_type


@pytest.mark.parametrize("work_type", ["development", "test", "business_analysis"])
def test_known_work_type_passes_through(work_type):
    assert classify_work_type(work_type) == work_type


def test_none_defaults_to_business_analysis():
    assert classify_work_type(None) == "business_analysis"


def test_unknown_hint_raises():
    with pytest.raises(ValueError):
        classify_work_type("gardening")
