# Core Orchestrator

Modular AI orchestrator with autonomous workflows, hardware abstraction, and a hacker-style Textual TUI. The project targets PC first while keeping the API portable to embedded devices.

## Setup

Requirements:

- Python >= 3.11
- pip or uv/poetry for dependency management

Install in editable mode with dev tools:

```bash
pip install -e .[dev]
```

Run the TUI entrypoint:

```bash
python -m core.tui.app
```

## Architecture Overview

- **Registry (`core/registry.py`)**: Loads JSON manifests from `manifests/`, validates schema via Pydantic, and exposes lookup APIs for tools/actions. Intended to back both the AI protocol catalog (`ai/protocol`) and the TUI command palette.
- **Network Manager (`core/network.py`)**: Async state machine for connectivity (`Disconnected`, `Connecting`, `Connected`, `Error`) with retry/backoff and hooks for UI observers.
- **Authentication (`core/auth.py`)**: Pydantic and SQLAlchemy models for users/roles (`guest`, `user`, `admin`), token storage via keyring, and role-check helpers.
- **Hardware Abstraction (`core/hardware/pc_sim_adapter.py`)**: Simulated sensors/actuators with listeners for easy mocking and future embedded portability.
- **Models (`core/models/`)**: Shared Pydantic/SQLAlchemy skeletons for persisted logs and ORM integration.
- **Configuration (`core/config.py`)**: Pydantic settings to harmonize environment variables, manifest paths, and HTTP/2 support.
- **TUI (`core/tui/app.py`)**: Textual-based UI with six panels (header, footer, controls, status, log, viewport/metrics) and placeholder commands for registry reloads and network connect.
- **AI Protocol (`ai/protocol/`)**: System prompt and tool catalog describing orchestrator-facing tools.

## Development Workflow

- Format with `black` and lint with `ruff` (config in `pyproject.toml`).
- Run tests with `pytest` (config via `pyproject.toml` / `pytest.ini`).
- Add new manifests under `manifests/` to extend the registry and keep them aligned with `ai/protocol/tool_catalog.json`.

## Testing & Quality

```bash
pytest
ruff check
black --check .
```

Quality gates prioritize deterministic tests, idempotent changes, and clear logging for observability.

## ADRs

Architecture decisions live under `adr/`:

- `0001-architecture.md` — core layering and registry-driven design.
- `0002-ui-framework-textual.md` — rationale for choosing Textual for the multi-panel console UI.
