import asyncio

import pytest

from core.network import HealthCheckConfig, NetworkManager, NetworkState


class DummyNetworkManager(NetworkManager):
    def __init__(self, dns_ok=True, http_ok=True, api_ok=True, captive=False):
        super().__init__(HealthCheckConfig(max_retries=1, backoff_base=0.01))
        self._dns_ok = dns_ok
        self._http_ok = http_ok
        self._api_ok = api_ok
        self._captive = captive

    async def _check_dns(self):
        return self._dns_ok

    async def _check_http(self):
        if self._captive:
            return False, 511
        return self._http_ok, 200 if self._http_ok else 500

    async def _check_api(self):
        return self._api_ok, 200 if self._api_ok else 500


@pytest.mark.asyncio
async def test_network_online():
    manager = DummyNetworkManager()
    report = await manager.evaluate_state()
    assert report.state == NetworkState.ONLINE


@pytest.mark.asyncio
async def test_network_captive_portal():
    manager = DummyNetworkManager(captive=True)
    report = await manager.evaluate_state()
    assert report.state == NetworkState.CAPTIVE_PORTAL


@pytest.mark.asyncio
async def test_network_degraded_dns():
    manager = DummyNetworkManager(dns_ok=False)
    report = await manager.evaluate_state()
    assert report.state == NetworkState.OFFLINE
