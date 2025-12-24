from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.request
from types import SimpleNamespace
from typing import Any, Dict, Optional


class HTTPError(Exception):
    pass


class Response:
    def __init__(self, status_code: int, data: bytes):
        self.status_code = status_code
        self._data = data

    def json(self) -> Any:
        try:
            return json.loads(self._data.decode("utf-8"))
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPError("Invalid JSON") from exc


class AsyncClient:
    def __init__(self, timeout: float = 3.0, headers: Optional[Dict[str, str]] = None, follow_redirects: bool = True):
        self.timeout = timeout
        self.headers = headers or {}
        self.follow_redirects = follow_redirects

    async def head(self, url: str) -> Response:
        return await self._request("HEAD", url)

    async def get(self, url: str) -> Response:
        return await self._request("GET", url)

    async def post(self, url: str, json: Optional[dict] = None) -> Response:
        data = None
        headers = dict(self.headers)
        if json is not None:
            data = json.dumps(json).encode("utf-8")
            headers["Content-Type"] = "application/json"
        return await self._request("POST", url, data=data, headers=headers)

    async def _request(self, method: str, url: str, data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None) -> Response:
        def _sync_request():
            request = urllib.request.Request(url, data=data, method=method, headers=headers or self.headers)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as resp:  # nosec B310
                    return Response(resp.status, resp.read())
            except urllib.error.HTTPError as exc:
                return Response(exc.code, exc.read())
            except Exception as exc:  # pragma: no cover - network edge
                raise HTTPError(str(exc)) from exc

        return await asyncio.to_thread(_sync_request)

    async def aclose(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()


__all__ = ["AsyncClient", "HTTPError", "Response"]
