"""Dashboard panel for orchestration overview."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import DataTable, Static

from core.tui.panels.base import BasePanel
from core.tui.state import OrchestratorSnapshot


class DashboardPanel(BasePanel):
    """Top-level overview for orchestrator health."""

    PANEL_ID = "dashboard"
    DEFAULT_TITLE = "Dashboard"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._metrics_table: DataTable | None = None
        self._message = Static()

    def compose(self) -> ComposeResult:
        yield Static("Panoramica sistema", classes="panel-title")
        metrics = DataTable(zebra_stripes=True, id="dashboard-metrics")
        metrics.add_columns("Metrica", "Valore")
        self._metrics_table = metrics
        yield metrics
        self._message.id = "dashboard-message"
        yield self._message

    def refresh(self, snapshot: OrchestratorSnapshot) -> None:
        if not self._metrics_table:
            return

        self._metrics_table.clear(columns=False)
        for key, value in snapshot.dashboard_metrics.items():
            self._metrics_table.add_row(str(key), str(value))

        message = snapshot.message or "Snapshot aggiornato"
        self._message.update(f"ℹ️ {message}")
