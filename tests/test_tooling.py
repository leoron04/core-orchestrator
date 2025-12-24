import pytest

from ai.providers.base import BaseProvider
from ai.runtime.ai_engine import AIEngine
from ai.runtime.permission_gate import PermissionGate
from ai.runtime.policy_gate import PolicyGate
from ai.runtime.tool_dispatcher import ToolDispatcher, ToolValidationError


class EchoProvider(BaseProvider):
    async def send(self, messages, tools=None):
        last = list(messages)[-1]
        return last.get("content", ""), last.get("commands", [])


def ping_tool(message: str):
    return f"pong:{message}"


def test_tool_dispatcher_validates():
    dispatcher = ToolDispatcher({"ping": ping_tool})
    commands = [{"name": "ping", "arguments": {"message": "hello"}}]
    results = dispatcher.execute(commands)
    assert results[0][1] == "pong:hello"


def test_tool_dispatcher_rejects_unknown():
    dispatcher = ToolDispatcher({"ping": ping_tool})
    with pytest.raises(ToolValidationError):
        dispatcher.execute([{"name": "unknown", "arguments": {}}])


@pytest.mark.asyncio
async def test_ai_engine_policy_block():
    provider = EchoProvider()
    engine = AIEngine(provider, policy_gate=PolicyGate(), tool_dispatcher=ToolDispatcher({"ping": ping_tool}))
    messages = [{"role": "user", "content": "please delete system32"}]
    result = await engine.run(messages)
    assert result.policy == PolicyGate.BLOCKED


@pytest.mark.asyncio
async def test_ai_engine_executes_tool():
    provider = EchoProvider()
    permission = PermissionGate(role_permissions={"user": {"ping"}})
    engine = AIEngine(
        provider,
        policy_gate=PolicyGate(),
        permission_gate=permission,
        tool_dispatcher=ToolDispatcher({"ping": ping_tool}),
        role="user",
    )
    messages = [{"role": "assistant", "content": "use tool", "commands": [{"name": "ping", "arguments": {"message": "hi"}}]}]
    result = await engine.run(messages, tools={"ping": ping_tool})
    assert result.commands_executed[0][1] == "pong:hi"
