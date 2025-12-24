"""Panel for module runtime state."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import DataTable, Static

from core.tui.panels.base import BasePanel
from core.tui.state import OrchestratorSnapshot, format_timedelta


class ModulesPanel(BasePanel):
    """Shows orchestrator modules and their health."""

    PANEL_ID = "modules"
    DEFAULT_TITLE = "Moduli"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._table: DataTable | None = None

    def compose(self) -> ComposeResult:
        yield Static("Moduli orchestratore", classes="panel-title")
        table = DataTable(zebra_stripes=True, id="modules-table")
        table.add_columns("Nome", "Stato", "Salute", "Versione", "Uptime")
        self._table = table
        yield table

    def refresh(self, snapshot: OrchestratorSnapshot) -> None:
        if not self._table:
            return

        self._table.clear(columns=False)
        for module in snapshot.modules:
            self._table.add_row(
                module.name,
                module.status,
                module.health,
                module.version,
                format_timedelta(module.uptime),
            )
