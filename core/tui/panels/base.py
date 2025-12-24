"""Base classes for TUI panels."""
from __future__ import annotations

from typing import Protocol

from textual.binding import Binding
from textual.containers import VerticalScroll

from core.tui.state import OrchestratorSnapshot


class RefreshablePanel(Protocol):
    """Protocol for panels that can render from a snapshot."""

    def refresh(self, snapshot: OrchestratorSnapshot) -> None:  # pragma: no cover - protocol
        ...


class BasePanel(VerticalScroll):
    """Shared behavior for all panels."""

    PANEL_ID: str = "panel"
    DEFAULT_TITLE: str = "Panel"

    BINDINGS = [
        Binding("r", "panel_refresh", "Aggiorna", show=False),
    ]

    def __init__(self, title: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.title = title or self.DEFAULT_TITLE

    def action_panel_refresh(self) -> None:
        """Request a refresh from the parent app."""

        if hasattr(self.app, "refresh_from_panel"):
            # The main app exposes this hook to avoid tight coupling.
            self.app.refresh_from_panel(self)

    def refresh(self, snapshot: OrchestratorSnapshot) -> None:  # pragma: no cover - default
        """Update widgets with the latest snapshot. Override in subclasses."""

        del snapshot
