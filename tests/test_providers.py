import asyncio

import pytest

from ai.providers import CustomProvider, GeminiProvider, OpenAIProvider


@pytest.mark.asyncio
async def test_openai_provider_offline():
    provider = OpenAIProvider(model="gpt-4")
    text, commands = await provider.send([{"role": "user", "content": "hello"}])
    assert "hello" in text
    assert commands == []


@pytest.mark.asyncio
async def test_gemini_provider_offline():
    provider = GeminiProvider()
    text, commands = await provider.send([{"role": "user", "content": "ping"}])
    assert "ping" in text
    assert commands == []


@pytest.mark.asyncio
async def test_custom_provider_fallback():
    provider = CustomProvider("http://127.0.0.1:9/nonexistent")
    text, commands = await provider.send([{"role": "user", "content": "custom"}])
    assert "custom" in text
    assert commands == []
