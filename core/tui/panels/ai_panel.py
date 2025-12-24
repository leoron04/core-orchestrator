"""Panel for AI workloads and jobs."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import DataTable, Static

from core.tui.panels.base import BasePanel
from core.tui.state import OrchestratorSnapshot, percent


class AIPanel(BasePanel):
    """Displays AI job queue and progress."""

    PANEL_ID = "ai"
    DEFAULT_TITLE = "AI"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._table: DataTable | None = None

    def compose(self) -> ComposeResult:
        yield Static("Job AI attivi", classes="panel-title")
        table = DataTable(zebra_stripes=True, id="ai-table")
        table.add_columns("ID", "Modello", "Stato", "Avanzamento", "Owner")
        self._table = table
        yield table

    def refresh(self, snapshot: OrchestratorSnapshot) -> None:
        if not self._table:
            return

        self._table.clear(columns=False)
        for job in snapshot.ai_jobs:
            self._table.add_row(
                job.job_id,
                job.model,
                job.status,
                percent(job.progress),
                job.owner,
            )
