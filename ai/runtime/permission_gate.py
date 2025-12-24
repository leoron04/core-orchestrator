from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Set


@dataclass
class PermissionGate:
    """
    Role-based permission checks for tool execution.
    """

    role_permissions: Dict[str, Set[str]] = field(
        default_factory=lambda: {
            "guest": set(),
            "user": {"read", "write_notes"},
            "admin": {"read", "write_notes", "system_control"},
        }
    )

    def is_allowed(self, action: str, role: str) -> bool:
        if role not in self.role_permissions:
            return False
        return action in self.role_permissions[role]

    def filter_commands(self, commands: Iterable[dict], role: str) -> list:
        allowed = []
        for command in commands:
            action = command.get("name")
            if action and self.is_allowed(action, role):
                allowed.append(command)
        return allowed
