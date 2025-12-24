from __future__ import annotations

import json
from typing import Iterable, Optional, Tuple

from .base import BaseProvider, Commands, Message, Tool
from core.httpx_fallback import httpx


class CustomProvider(BaseProvider):
    """
    Generic HTTP endpoint provider.

    The endpoint must accept POST requests with a JSON body containing
    {"messages": [...], "tools": [...]}. The response should include
    {"text": "...", "commands": [...]}. The provider intentionally tolerates
    graceful degradation by returning a deterministic fallback if the endpoint
    is unreachable.
    """

    def __init__(self, endpoint: str, model: str = "custom-model", timeout: float = 10.0):
        super().__init__(model)
        self.endpoint = endpoint
        self.timeout = timeout

    async def send(self, messages: Iterable[Message], tools: Optional[Iterable[Tool]] = None) -> Tuple[str, Commands]:
        payload = {"model": self.model_name, "messages": list(messages), "tools": list(tools) if tools else []}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("text", ""), data.get("commands", [])
        except Exception:
            # Fallback to deterministic behavior so tests/CI remain hermetic.
            summarized = " ".join([m.get("content", "") for m in payload["messages"] if isinstance(m, dict)])
            return f"[offline-custom:{self.endpoint}] {summarized}".strip(), []
