"""Smoke tests for Task 1.0 — project scaffolding.

Confirms the package and its planned modules are importable before any
real logic exists (Tasks 2.0-5.0 fill these modules in).
"""

import importlib


def test_package_importable():
    importlib.import_module("taskweb_pro")


def test_models_importable():
    module = importlib.import_module("taskweb_pro.models")
    assert hasattr(module, "ChildTask")
    assert hasattr(module, "ActionStatus")


def test_azure_task_resolver_importable():
    importlib.import_module("taskweb_pro.azure_task_resolver")


def test_taskweb_adapter_importable():
    importlib.import_module("taskweb_pro.taskweb_adapter")


def test_logging_configure_is_idempotent():
    from taskweb_pro.logging_config import configure_logging

    configure_logging()
    configure_logging()
