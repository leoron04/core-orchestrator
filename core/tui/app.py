"""Textual TUI entrypoint for the orchestrator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import ContentSwitcher, Footer, Header, Static, Tab, Tabs

from core.tui.panels import (
    AIPanel,
    AuthPanel,
    DashboardPanel,
    DevicePanel,
    ModulesPanel,
    NetworkPanel,
)
from core.tui.panels.base import BasePanel
from core.tui.state import OrchestratorDataProvider, OrchestratorSnapshot


@dataclass
class PanelConfig:
    """Configuration for panel registration."""

    key: str
    title: str
    factory: Callable[[], BasePanel]


class OrchestratorApp(App):
    """Textual application that routes between orchestrator panels."""

    TITLE = "core-orchestrator"
    CSS = """
    Screen { layout: vertical; }
    #shell { layout: vertical; padding: 1 2; }
    #top-bar { layout: horizontal; height: 3; }
    #panel-switcher { height: 1fr; }
    Tabs { margin-bottom: 1; }
    .panel-title { margin: 0 0 1 0; text-style: bold; }
    DataTable { height: 1fr; }
    """

    BINDINGS = [
        Binding("ctrl+d", "switch('dashboard')", "Dashboard"),
        Binding("ctrl+m", "switch('modules')", "Moduli"),
        Binding("ctrl+e", "switch('devices')", "Device"),
        Binding("ctrl+a", "switch('ai')", "AI"),
        Binding("ctrl+n", "switch('network')", "Rete"),
        Binding("ctrl+u", "switch('auth')", "Auth"),
        Binding("r", "refresh", "Aggiorna"),
        Binding("q", "quit", "Esci", priority=True),
    ]

    def __init__(self, data_loader: Callable[[], OrchestratorSnapshot] | None = None, **kwargs) -> None:
        self._data_provider = OrchestratorDataProvider(loader=data_loader)
        self._active_panel = "dashboard"
        self._panels: dict[str, BasePanel] = {}
        self._panel_configs = self._build_panel_configs()
        self._snapshot: OrchestratorSnapshot | None = None
        super().__init__(**kwargs)

    def _build_panel_configs(self) -> list[PanelConfig]:
        return [
            PanelConfig("dashboard", "Dashboard", DashboardPanel),
            PanelConfig("modules", "Moduli", ModulesPanel),
            PanelConfig("devices", "Device", DevicePanel),
            PanelConfig("ai", "AI", AIPanel),
            PanelConfig("network", "Rete", NetworkPanel),
            PanelConfig("auth", "Auth", AuthPanel),
        ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="shell"):
            with Horizontal(id="top-bar"):
                yield Static("Orchestrator", id="app-title")
                yield Static("Hotkeys: ctrl+d/m/e/a/n/u, r = refresh", id="shortcuts")

            tabs = Tabs(*[Tab(cfg.title, id=cfg.key) for cfg in self._panel_configs], id="panel-tabs")
            yield tabs

            panels = {cfg.key: cfg.factory()(id=cfg.key) for cfg in self._panel_configs}
            self._panels.update(panels)
            switcher = ContentSwitcher(
                *panels.values(), initial=self._active_panel, id="panel-switcher"
            )
            yield switcher
        yield Footer()

    def on_mount(self) -> None:
        tabs = self.query_one(Tabs)
        tabs.active = self._active_panel
        self.refresh_from_orchestrator()

    def action_switch(self, panel: str) -> None:
        """Switch to a panel via hotkey."""

        if panel not in self._panels:
            return
        self._active_panel = panel
        self._apply_panel_switch()

    def action_refresh(self) -> None:
        self.refresh_from_orchestrator()

    def refresh_from_panel(self, panel: BasePanel) -> None:
        """Hook called by panels requesting a refresh."""

        del panel
        self.refresh_from_orchestrator()

    def refresh_from_orchestrator(self) -> None:
        self._snapshot = self._data_provider.fetch()
        for panel in self._panels.values():
            panel.refresh(self._snapshot)
        self.sub_title = self._snapshot.message or ""

    def _apply_panel_switch(self) -> None:
        switcher = self.query_one(ContentSwitcher)
        switcher.current = self._active_panel
        tabs = self.query_one(Tabs)
        tabs.active = self._active_panel

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        if event.tab.id is not None:
            self._active_panel = event.tab.id
            self._apply_panel_switch()

    def on_key(self, event: events.Key) -> None:
        # Provide number shortcuts for quick navigation.
        if event.key in {"1", "2", "3", "4", "5", "6"}:
            index = int(event.key) - 1
            if 0 <= index < len(self._panel_configs):
                self._active_panel = self._panel_configs[index].key
                self._apply_panel_switch()

    def get_snapshot(self) -> OrchestratorSnapshot | None:
        """Expose the latest snapshot for consumers."""

        return self._snapshot


if __name__ == "__main__":
    OrchestratorApp().run()
