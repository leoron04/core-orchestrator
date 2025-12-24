import importlib
import importlib.util


def load_httpx():
    spec = importlib.util.find_spec("httpx")
    if spec and spec.origin:
        return importlib.import_module("httpx")
    from core import httpx_stub

    return httpx_stub


httpx = load_httpx()

__all__ = ["httpx", "load_httpx"]
