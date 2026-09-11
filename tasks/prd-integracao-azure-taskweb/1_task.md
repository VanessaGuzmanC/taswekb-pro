# Task 1.0: Project scaffolding

## Overview

Set up the Python package skeleton for the Azure/Taskweb integration module, pinned dependency management, and the pytest harness that every later task builds on.

<skills>
### Conformance with Skills

No local `.claude/skills` directory exists in this project. This task follows the structure of the `phoenix-spec` skill (global Claude Code skills directory) that generated this spec: a package with small, single-responsibility Python modules invoked by a skill, mirroring its `attach-ado.mjs` helper-script pattern.
</skills>

<rules>
### Conformance with Rules

No `.claude/rules` directory exists in this project — no project-specific rule set to check against.
</rules>

<requirements>
- Python 3.12 (per `architecture/tech_stack_context.md.md`)
- `requirements.txt` with pinned versions (pip freeze convention)
- `pytest` as the test runner
- Package layout matching techspec.md → System Architecture → Component Overview
</requirements>

## Subtasks

- [x] 1.1 Create the package structure (`taskweb_pro/` with `models.py`, `azure_task_resolver.py`, `taskweb_adapter.py` stubs)
- [x] 1.2 Create `requirements.txt` with pinned versions and a short local-setup note
- [x] 1.3 Configure `pytest` (`pyproject.toml` or `pytest.ini`) and a `tests/` folder mirroring the package
- [x] 1.4 Add the local logging configuration stub (Python `logging`), wired but not yet emitting feature-specific logs

## Implementation Details

See `techspec.md` → System Architecture → Component Overview, and → Monitoring and Observability. Do not re-derive the module split here — follow it as specified.

## Success Criteria

- `pytest` runs (even with zero real tests) without error
- The package is importable (`import taskweb_pro`)
- `pip install -r requirements.txt` reproduces the environment from a clean venv

## Task Tests

- [x] Unit tests: smoke test importing each module
- [x] Integration tests: not applicable for this task
- [x] E2E tests: not applicable for this task

## Relevant Files

- `requirements.txt`
- `pyproject.toml` or `pytest.ini`
- `taskweb_pro/__init__.py`
- `taskweb_pro/models.py`
- `taskweb_pro/azure_task_resolver.py`
- `taskweb_pro/taskweb_adapter.py`
- `tests/`
