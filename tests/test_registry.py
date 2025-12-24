from pathlib import Path

import pytest

pytest.importorskip("pydantic")

from core.registry import Registry


def test_registry_loads_example_manifest():
    registry = Registry(manifest_path=Path("manifests"))
    registry.load()

    tools = registry.list_tools()
    assert "core-orchestrator" in tools

    actions = registry.list_actions("core-orchestrator")
    assert "registry:list" in actions
    assert registry.lookup_action("core-orchestrator", "network:probe") is not None
