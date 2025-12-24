from core.memory_store import MemoryStore


def test_memory_store_events_and_facts(tmp_path):
    db_path = tmp_path / "memory.db"
    store = MemoryStore(str(db_path))

    event_id = store.log_event("test", {"value": 1})
    assert event_id == 1

    store.store_fact("pref.theme", "dark")
    assert store.get_fact("pref.theme") == "dark"

    results = store.search_events("value")
    assert results[0]["payload"]["value"] == 1

    store.close()
