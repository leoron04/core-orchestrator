import pytest

httpx = pytest.importorskip("httpx")

from core.network import NetworkManager, NetworkState


@pytest.mark.asyncio
async def test_network_manager_connects_with_mock_transport():
    async def handler(request: httpx.Request) -> httpx.Response:  # type: ignore[type-arg]
        if request.url.path.endswith("/health"):
            return httpx.Response(200, json={"status": "ok"})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    manager = NetworkManager(base_url="https://example.com", client=client, max_retries=1)

    connected = await manager.connect()

    assert connected is True
    assert manager.state == NetworkState.CONNECTED

    await manager.disconnect()
    assert manager.state == NetworkState.DISCONNECTED
