"""Network manager with a simple state machine and retry/backoff support."""

from __future__ import annotations

import asyncio
import logging
from enum import Enum
from typing import Awaitable, Callable, Iterable, List, Optional

import httpx

from core.config import AppSettings

logger = logging.getLogger(__name__)


class NetworkState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


StateCallback = Callable[[NetworkState], Awaitable[None] | None]


class NetworkManager:
    """Manage connection lifecycle with structured state transitions."""

    def __init__(
        self,
        base_url: str,
        settings: Optional[AppSettings] = None,
        client: Optional[httpx.AsyncClient] = None,
        state_observers: Optional[Iterable[StateCallback]] = None,
        max_retries: int = 3,
        backoff_seconds: float = 0.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.settings = settings or AppSettings()
        self.client = client or httpx.AsyncClient(http2=self.settings.enable_http2)
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self._state: NetworkState = NetworkState.DISCONNECTED
        self._observers: List[StateCallback] = list(state_observers or [])

    @property
    def state(self) -> NetworkState:
        return self._state

    def add_observer(self, callback: StateCallback) -> None:
        """Register an observer invoked on state changes."""

        self._observers.append(callback)

    async def _notify_state(self) -> None:
        for observer in self._observers:
            result = observer(self._state)
            if asyncio.iscoroutine(result):
                await result

    async def connect(self) -> bool:
        """Attempt to connect to the configured base URL with retry/backoff."""

        await self._transition(NetworkState.CONNECTING)
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info("Connecting to %s (attempt %s)", self.base_url, attempt)
                response = await self.client.get(f"{self.base_url}/health", timeout=5.0)
                response.raise_for_status()
                await self._transition(NetworkState.CONNECTED)
                return True
            except httpx.HTTPError as exc:
                logger.warning("Connection attempt %s failed: %s", attempt, exc)
                await self._transition(NetworkState.ERROR)
                await asyncio.sleep(self.backoff_seconds * attempt)
        await self._transition(NetworkState.DISCONNECTED)
        return False

    async def disconnect(self) -> None:
        """Close the client and set state to disconnected."""

        await self.client.aclose()
        await self._transition(NetworkState.DISCONNECTED)

    async def send(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Send an HTTP request ensuring the connection is active."""

        if self._state != NetworkState.CONNECTED:
            msg = "Network is not connected"
            raise RuntimeError(msg)
        url = f"{self.base_url}/{path.lstrip('/') }"
        logger.debug("Sending %s %s", method, url)
        response = await self.client.request(method, url, **kwargs)
        return response

    async def _transition(self, state: NetworkState) -> None:
        self._state = state
        logger.debug("Transitioned to state: %s", state.value)
        await self._notify_state()

    async def __aenter__(self) -> "NetworkManager":  # pragma: no cover - convenience
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - convenience
        await self.disconnect()
