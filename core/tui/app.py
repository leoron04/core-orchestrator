"""Textual TUI entrypoint for the Core Orchestrator."""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable, Optional

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Log, Static

from core.registry import Registry

logger = logging.getLogger(__name__)


class OrchestratorApp(App[None]):
    """Multi-panel TUI orchestrating registry, network, and hardware interactions."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 4;
        grid-rows: 1fr 3fr 3fr 1fr;
        grid-columns: 1fr 1fr;
    }

    #header { grid-column: 1 / span 2; }
    #footer { grid-column: 1 / span 2; }

    #controls { border: solid green; }
    #status { border: solid yellow; }
    #log { border: solid blue; }
    #viewport { border: solid magenta; }
    #notifications { border: solid cyan; }
    #metrics { border: solid red; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reload_registry", "Reload registry"),
        ("c", "connect", "Connect network"),
    ]

    registry: reactive[Optional[Registry]] = reactive(None)

    def __init__(
        self,
        registry_paths: Optional[Iterable[str]] = None,
    ) -> None:
        super().__init__()
        self.registry_paths = list(registry_paths or ["./manifests"])

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        with Container(id="main-body"):
            with Horizontal():
                yield Static("Controls", id="controls")
                yield Static("Status", id="status")
            with Horizontal():
                yield Log(id="log")
                yield Static("Viewport", id="viewport")
            with Horizontal():
                yield Static("Notifications", id="notifications")
                yield Static("Metrics", id="metrics")
        yield Footer(id="footer")

    async def on_mount(self) -> None:
        self._initialize_registry()
        await self._log_message("TUI initialized. Press 'r' to reload registry.")

    def _initialize_registry(self) -> None:
        self.registry = Registry(manifest_path=self.registry_paths[0])
        self.registry.load()
        logger.info("Loaded %s tool(s) into registry", len(self.registry))

    async def _log_message(self, message: str) -> None:
        log_widget = self.query_one("#log", Log)
        log_widget.write_line(message)

    async def action_quit(self) -> None:  # pragma: no cover - Textual handles this
        await super().action_quit()

    async def action_reload_registry(self) -> None:
        if not self.registry:
            self._initialize_registry()
        else:
            self.registry.reload()
        await self._log_message("Registry reloaded")

    async def action_connect(self) -> None:
        await self._log_message("Connect action triggered (network stub).")

    async def on_key(self, event: events.Key) -> None:  # pragma: no cover - passthrough
        await super().on_key(event)
        await self._log_message(f"Key pressed: {event.key}")


def main() -> None:
    """CLI entrypoint for `python -m core.tui.app`."""

    asyncio.run(OrchestratorApp().run_async())


if __name__ == "__main__":
    main()
