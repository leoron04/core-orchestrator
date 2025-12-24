from __future__ import annotations

import importlib
import json
import os
from typing import Iterable, List, Optional, Tuple

from .base import BaseProvider, Commands, Message, Tool


class OpenAIProvider(BaseProvider):
    """
    Lightweight OpenAI provider wrapper.

    The implementation intentionally avoids making outbound calls when the API
    key is absent, returning a deterministic echo response instead. This allows
    running tests and CI without secrets.
    """

    def __init__(self, model: str = "gpt-4"):
        super().__init__(model)
        self.api_key = os.getenv("OPENAI_API_KEY")

    async def send(self, messages: Iterable[Message], tools: Optional[Iterable[Tool]] = None) -> Tuple[str, Commands]:
        normalized = self._coerce_messages(messages)
        text = self._synthesized_text(normalized)
        commands: Commands = self._extract_commands(normalized, tools)
        if not self.api_key:
            return text, commands

        spec = importlib.util.find_spec("openai")
        if not spec:
            return text, commands

        openai = importlib.import_module("openai")
        client = openai.AsyncOpenAI(api_key=self.api_key)
        completion = await client.chat.completions.create(
            model=self.model_name,
            messages=normalized,
            tools=list(tools) if tools else None,
        )
        ai_message = completion.choices[0].message
        content = ai_message.content or text
        tool_calls = getattr(ai_message, "tool_calls", None) or []
        commands_json = [json.loads(call.function.arguments) if hasattr(call, "function") else {} for call in tool_calls]
        return content, commands_json

    def _synthesized_text(self, messages: List[Message]) -> str:
        last_user = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                last_user = message.get("content", "")
                break
        return f"[offline-openai:{self.model_name}] {last_user}".strip()

    def _extract_commands(self, messages: List[Message], tools: Optional[Iterable[Tool]]) -> Commands:
        if not tools:
            return []
        # Simple heuristic: look for a field "commands" in the last assistant message.
        for message in reversed(messages):
            if message.get("role") == "assistant" and "commands" in message:
                commands = message.get("commands") or []
                return commands if isinstance(commands, list) else []
        return []
