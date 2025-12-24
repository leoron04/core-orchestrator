import asyncio
import enum
import socket
from dataclasses import dataclass, field
from typing import Optional, Tuple

from core.httpx_fallback import httpx


class NetworkState(str, enum.Enum):
    OFFLINE = "OFFLINE"
    CAPTIVE_PORTAL = "CAPTIVE_PORTAL"
    DEGRADED = "DEGRADED"
    ONLINE = "ONLINE"


@dataclass
class HealthCheckConfig:
    dns_host: str = "1.1.1.1"
    http_url: str = "https://example.com"
    api_url: Optional[str] = None
    timeout: float = 3.0
    max_retries: int = 3
    backoff_base: float = 0.5
    backoff_factor: float = 2.0
    user_agent: str = "core-orchestrator/0.1"

    def backoff(self, attempt: int) -> float:
        return self.backoff_base * (self.backoff_factor ** attempt)


@dataclass
class HealthReport:
    dns_ok: bool
    http_ok: bool
    api_ok: bool
    detail: str = ""
    captive_portal: bool = False

    @property
    def state(self) -> NetworkState:
        if self.captive_portal:
            return NetworkState.CAPTIVE_PORTAL
        if not self.dns_ok:
            return NetworkState.OFFLINE
        if not self.http_ok:
            return NetworkState.DEGRADED
        if not self.api_ok:
            return NetworkState.DEGRADED
        return NetworkState.ONLINE


class NetworkManager:
    """
    Asynchronous network state machine with exponential backoff.

    The manager performs DNS, HTTP, and optional API endpoint health checks to
    infer the network state. It is intentionally side-effect free: callers
    should persist state externally if required.
    """

    def __init__(self, config: Optional[HealthCheckConfig] = None):
        self.config = config or HealthCheckConfig()
        self._state: NetworkState = NetworkState.OFFLINE
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def state(self) -> NetworkState:
        return self._state

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {"User-Agent": self.config.user_agent}
            self._client = httpx.AsyncClient(timeout=self.config.timeout, headers=headers, follow_redirects=True)
        return self._client

    async def _check_dns(self) -> bool:
        loop = asyncio.get_event_loop()
        try:
            await loop.getaddrinfo(self.config.dns_host, None, proto=socket.IPPROTO_TCP)
            return True
        except socket.gaierror:
            return False

    async def _check_http(self) -> Tuple[bool, Optional[int]]:
        client = await self._ensure_client()
        try:
            response = await client.head(self.config.http_url)
            if response.status_code == 511:
                return False, 511
            if response.status_code >= 400:
                return False, response.status_code
            return True, response.status_code
        except httpx.HTTPError:
            return False, None

    async def _check_api(self) -> Tuple[bool, Optional[int]]:
        if not self.config.api_url:
            return True, None
        client = await self._ensure_client()
        try:
            response = await client.get(self.config.api_url)
            if response.status_code >= 400:
                return False, response.status_code
            return True, response.status_code
        except httpx.HTTPError:
            return False, None

    async def _attempt_checks(self) -> HealthReport:
        dns_ok = await self._check_dns()
        http_ok, http_code = await self._check_http()
        api_ok, api_code = await self._check_api()

        detail_parts = []
        if not dns_ok:
            detail_parts.append("DNS resolution failed")
        if not http_ok:
            detail_parts.append(f"HTTP unhealthy (code={http_code})")
            if http_code == 511:
                return HealthReport(dns_ok, False, api_ok, "Captive portal detected", captive_portal=True)
        if not api_ok:
            detail_parts.append(f"API unhealthy (code={api_code})")

        detail = "; ".join(detail_parts)
        return HealthReport(dns_ok, http_ok, api_ok, detail)

    async def evaluate_state(self) -> HealthReport:
        attempt = 0
        last_report: Optional[HealthReport] = None
        while attempt < self.config.max_retries:
            report = await self._attempt_checks()
            last_report = report
            self._state = report.state
            if report.state == NetworkState.ONLINE:
                return report
            if report.state == NetworkState.CAPTIVE_PORTAL:
                self._state = NetworkState.CAPTIVE_PORTAL
                return report

            await asyncio.sleep(self.config.backoff(attempt))
            attempt += 1

        if last_report:
            self._state = last_report.state
            return last_report
        fallback = HealthReport(False, False, False, "No checks executed")
        self._state = fallback.state
        return fallback

    async def monitor(self, interval: float = 30.0):
        """
        Async generator yielding health reports every interval seconds.
        """
        while True:
            report = await self.evaluate_state()
            yield report
            await asyncio.sleep(interval)

    async def aclose(self):
        if self._client:
            await self._client.aclose()
            self._client = None
