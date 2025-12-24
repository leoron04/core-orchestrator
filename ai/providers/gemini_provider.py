from __future__ import annotations

import importlib
import os
from typing import Iterable, List, Optional, Tuple

from .base import BaseProvider, Commands, Message, Tool


class GeminiProvider(BaseProvider):
    """
    Simplified Google Gemini provider facade.

    Mirrors the OpenAI provider behavior with an offline friendly fallback.
    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        super().__init__(model)
        self.api_key = os.getenv("GEMINI_API_KEY")

    async def send(self, messages: Iterable[Message], tools: Optional[Iterable[Tool]] = None) -> Tuple[str, Commands]:
        normalized = self._coerce_messages(messages)
        text = self._synthesized_text(normalized)
        commands: Commands = self._extract_commands(normalized)
        if not self.api_key:
            return text, commands

        spec = importlib.util.find_spec("google.genai")
        if not spec:
            return text, commands

        genai = importlib.import_module("google.genai")
        client = genai.Client(api_key=self.api_key)
        response = await client.responses.async_generate(
            model=self.model_name,
            messages=normalized,
            tools=list(tools) if tools else None,
        )
        content = response.output_text or text
        tool_calls = getattr(response, "function_calls", None) or []
        commands_json: Commands = []
        for call in tool_calls:
            if hasattr(call, "args"):
                commands_json.append(call.args)
        return content, commands_json

    def _synthesized_text(self, messages: List[Message]) -> str:
        last_user = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                last_user = message.get("content", "")
                break
        return f"[offline-gemini:{self.model_name}] {last_user}".strip()

    def _extract_commands(self, messages: List[Message]) -> Commands:
        for message in reversed(messages):
            if message.get("role") == "assistant" and "commands" in message:
                cmds = message.get("commands") or []
                return cmds if isinstance(cmds, list) else []
        return []
