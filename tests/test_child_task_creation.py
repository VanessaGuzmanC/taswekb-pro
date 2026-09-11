"""Unit tests for Task 3.0 — child task creation in Azure (Feature 2)."""

import pytest

from taskweb_pro.azure_task_resolver import build_child_task_item, should_create_child
from taskweb_pro.models import ChildTask


def test_should_create_child_true_when_no_existing_match():
    assert should_create_child(None) is True


def test_should_create_child_false_when_existing_match():
    existing = ChildTask(
        id=1, parent_id=99, work_type="development", assigned_to="alice", taskweb_visible=True
    )
    assert should_create_child(existing) is False


def test_build_child_task_item_uses_parent_title_verbatim():
    item = build_child_task_item("PBI 1234112: Registrar horas")
    assert item["title"] == "PBI 1234112: Registrar horas"


def test_build_child_task_item_default_empty_description():
    item = build_child_task_item("Some Title")
    assert item["description"] == ""


def test_build_child_task_item_with_description():
    item = build_child_task_item("Some Title", description="context notes")
    assert item["description"] == "context notes"


def test_build_child_task_item_rejects_empty_title():
    with pytest.raises(ValueError):
        build_child_task_item("")
