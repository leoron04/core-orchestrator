import pytest

from modules.device_guide.module import DeviceGuideModule
from modules.notes.module import NotesModule
from modules.routine.module import RoutineModule
from modules.security_hygiene.module import SecurityHygieneModule
from modules.system_health.module import SystemHealthModule


def test_notes_module_add_and_list(tmp_path):
    store_path = tmp_path / "notes.db"
    notes = NotesModule(store=None)
    notes.add_note("first")
    assert "first" in notes.list_notes()


def test_routine_module_add_and_list():
    routine = RoutineModule()
    routine.add_task("daily standup")
    assert "daily standup" in routine.list_tasks()


def test_security_hygiene_checklist():
    module = SecurityHygieneModule()
    checklist = module.run("checklist")
    assert checklist


def test_device_guide():
    module = DeviceGuideModule()
    assert "router" in module.run("guide", topic="wifi").lower()


@pytest.mark.asyncio
async def test_system_health_module(monkeypatch):
    class DummyManager:
        async def evaluate_state(self):
            class Report:
                state = "ONLINE"
                detail = ""

            return Report()

    module = SystemHealthModule(network_manager=DummyManager())
    result = await module.run("full")
    assert "network" in result
