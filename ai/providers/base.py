from __future__ import annotations

import abc
from typing import Iterable, List, Optional, Tuple


Message = dict
Tool = dict
Commands = List[dict]


class BaseProvider(abc.ABC):
    """
    Abstract AI provider. Implementations must return a tuple of (text, commands_json).
    commands_json is expected to be a list of command dictionaries that match the tool
    dispatcher schema.
    """

    model_name: str = "base"

    def __init__(self, model: Optional[str] = None):
        if model:
            self.model_name = model

    @abc.abstractmethod
    async def send(self, messages: Iterable[Message], tools: Optional[Iterable[Tool]] = None) -> Tuple[str, Commands]:
        raise NotImplementedError

    def _coerce_messages(self, messages: Iterable[Message]) -> List[Message]:
        normalized = []
        for message in messages:
            if not isinstance(message, dict):
                raise TypeError("messages must be dictionaries with role/content")
            normalized.append(message)
        return normalized
