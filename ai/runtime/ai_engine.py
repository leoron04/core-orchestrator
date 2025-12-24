from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from ai.providers import BaseProvider

from .permission_gate import PermissionGate
from .policy_gate import PolicyGate
from .tool_dispatcher import ToolDispatcher


@dataclass
class AIEngineResult:
    text: str
    commands_executed: list
    policy: str
    state: str


class AIEngine:
    """
    Orchestrates the provider, safety gate, permission gate, and tool dispatcher.
    """

    def __init__(
        self,
        provider: BaseProvider,
        policy_gate: Optional[PolicyGate] = None,
        permission_gate: Optional[PermissionGate] = None,
        tool_dispatcher: Optional[ToolDispatcher] = None,
        role: str = "user",
    ):
        self.provider = provider
        self.policy_gate = policy_gate or PolicyGate()
        self.permission_gate = permission_gate or PermissionGate()
        self.tool_dispatcher = tool_dispatcher or ToolDispatcher({})
        self.role = role

    async def run(self, messages: Iterable[dict], tools: Optional[dict] = None) -> AIEngineResult:
        policy_state = self.policy_gate.classify_messages(messages)
        response_text, commands = await self.provider.send(messages, tools=tools.values() if tools else None)

        if policy_state == PolicyGate.BLOCKED:
            return AIEngineResult(
                text="Request blocked by policy.",
                commands_executed=[],
                policy=policy_state,
                state="blocked",
            )

        allowed_commands = self.permission_gate.filter_commands(commands, self.role)
        executed = []
        if tools and allowed_commands:
            dispatcher = self.tool_dispatcher if self.tool_dispatcher.registry else ToolDispatcher(tools)
            executed = dispatcher.execute(allowed_commands)

        return AIEngineResult(
            text=response_text,
            commands_executed=executed,
            policy=policy_state,
            state="ok" if policy_state == PolicyGate.SAFE else "confirm",
        )
