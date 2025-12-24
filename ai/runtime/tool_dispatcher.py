from __future__ import annotations

import inspect
from typing import Callable, Dict, Iterable, List, Tuple


class ToolValidationError(Exception):
    pass


class ToolDispatcher:
    """
    Validates and executes tool commands against a registry of callables.
    """

    def __init__(self, registry: Dict[str, Callable]):
        self.registry = registry

    def validate(self, commands: Iterable[dict]) -> List[dict]:
        validated = []
        for command in commands:
            name = command.get("name")
            args = command.get("arguments", {})
            if name not in self.registry:
                raise ToolValidationError(f"Unknown tool: {name}")
            if not isinstance(args, dict):
                raise ToolValidationError(f"Invalid arguments for {name}")
            validated.append({"name": name, "arguments": args})
        return validated

    def execute(self, commands: Iterable[dict]) -> List[Tuple[str, object]]:
        results = []
        validated_commands = self.validate(commands)
        for command in validated_commands:
            name = command["name"]
            args = command["arguments"]
            fn = self.registry[name]
            sig = inspect.signature(fn)
            try:
                sig.bind(**args)
            except TypeError as exc:
                raise ToolValidationError(f"Arguments mismatch for {name}: {exc}") from exc
            result = fn(**args)
            results.append((name, result))
        return results
