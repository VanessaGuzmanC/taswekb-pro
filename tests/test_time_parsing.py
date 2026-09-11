"""Unit tests for Task 1.0 — time range parsing (`parse_time_range`)."""

from datetime import datetime, timedelta

import pytest

from taskweb_pro.time_parsing import parse_time_range

NOW = datetime(2026, 9, 10, 15, 30)


def test_start_and_end():
    start, end = parse_time_range("10:00", "10:15", None, NOW)
    assert start == datetime(2026, 9, 10, 10, 0)
    assert end == datetime(2026, 9, 10, 10, 15)


def test_start_and_duration():
    start, end = parse_time_range("15:00", None, 60, NOW)
    assert start == datetime(2026, 9, 10, 15, 0)
    assert end == datetime(2026, 9, 10, 16, 0)


def test_duration_only_ends_now():
    start, end = parse_time_range(None, None, 120, NOW)
    assert end == NOW
    assert start == NOW - timedelta(minutes=120)


def test_missing_end_and_duration_raises():
    with pytest.raises(ValueError):
        parse_time_range("10:00", None, None, NOW)


def test_both_end_and_duration_given_raises():
    with pytest.raises(ValueError):
        parse_time_range("10:00", "10:15", 60, NOW)


def test_end_without_start_or_duration_raises():
    with pytest.raises(ValueError):
        parse_time_range(None, "10:15", None, NOW)


def test_end_before_start_raises():
    with pytest.raises(ValueError):
        parse_time_range("10:15", "10:00", None, NOW)


def test_end_equal_start_raises():
    with pytest.raises(ValueError):
        parse_time_range("10:00", "10:00", None, NOW)


def test_zero_duration_raises():
    with pytest.raises(ValueError):
        parse_time_range(None, None, 0, NOW)


def test_negative_duration_raises():
    with pytest.raises(ValueError):
        parse_time_range(None, None, -5, NOW)


def test_bool_duration_rejected():
    with pytest.raises(TypeError):
        parse_time_range(None, None, True, NOW)


def test_non_int_duration_rejected():
    with pytest.raises(TypeError):
        parse_time_range("10:00", None, "60", NOW)


def test_malformed_clock_string_raises():
    with pytest.raises(ValueError):
        parse_time_range("10am", "11am", None, NOW)
