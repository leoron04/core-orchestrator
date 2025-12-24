from __future__ import annotations

import asyncio
from typing import Optional

from core.memory_store import MemoryStore
from core.network import NetworkManager, NetworkState


class SystemHealthModule:
    """
    Aggregates network and memory store health indicators.
    """

    def __init__(self, network_manager: Optional[NetworkManager] = None, store: Optional[MemoryStore] = None):
        self.network_manager = network_manager or NetworkManager()
        self.store = store or MemoryStore()

    async def network_status(self):
        report = await self.network_manager.evaluate_state()
        return {"state": report.state, "detail": report.detail}

    def storage_status(self):
        events = self.store.get_events(limit=1)
        return {"event_log_ready": bool(events is not None)}

    async def run(self, action: str):
        if action == "network":
            return await self.network_status()
        if action == "storage":
            return self.storage_status()
        if action == "full":
            net, storage = await asyncio.gather(self.network_status(), asyncio.to_thread(self.storage_status))
            return {"network": net, "storage": storage}
        raise ValueError(f"Unknown action: {action}")
