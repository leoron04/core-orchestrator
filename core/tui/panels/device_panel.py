"""Panel for orchestrated devices."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import DataTable, Static

from core.tui.panels.base import BasePanel
from core.tui.state import OrchestratorSnapshot


class DevicePanel(BasePanel):
    """Displays device health and telemetry."""

    PANEL_ID = "devices"
    DEFAULT_TITLE = "Dispositivi"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._table: DataTable | None = None

    def compose(self) -> ComposeResult:
        yield Static("Dispositivi gestiti", classes="panel-title")
        table = DataTable(zebra_stripes=True, id="devices-table")
        table.add_columns("Nome", "Tipo", "Salute", "CPU%", "Memoria%", "Temp °C")
        self._table = table
        yield table

    def refresh(self, snapshot: OrchestratorSnapshot) -> None:
        if not self._table:
            return

        self._table.clear(columns=False)
        for device in snapshot.devices:
            self._table.add_row(
                device.name,
                device.kind,
                device.health,
                f"{device.cpu:.0f}%",
                f"{device.memory:.0f}%",
                f"{device.temperature:.1f}",
            )
