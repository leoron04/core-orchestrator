"""Panel for network health and throughput."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import DataTable, Static

from core.tui.panels.base import BasePanel
from core.tui.state import OrchestratorSnapshot


class NetworkPanel(BasePanel):
    """Displays network link performance."""

    PANEL_ID = "network"
    DEFAULT_TITLE = "Rete"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._table: DataTable | None = None

    def compose(self) -> ComposeResult:
        yield Static("Rete e throughput", classes="panel-title")
        table = DataTable(zebra_stripes=True, id="network-table")
        table.add_columns("Link", "Stato", "Latenza ms", "Banda Mbps", "Jitter ms")
        self._table = table
        yield table

    def refresh(self, snapshot: OrchestratorSnapshot) -> None:
        if not self._table:
            return

        self._table.clear(columns=False)
        for link in snapshot.network:
            jitter = f"{link.jitter_ms:.1f}" if link.jitter_ms is not None else "—"
            self._table.add_row(
                link.name,
                link.status,
                f"{link.latency_ms:.1f}",
                f"{link.bandwidth_mbps:.1f}",
                jitter,
            )
