"""Panel for authentication and authorization sessions."""
from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.widgets import DataTable, Static

from core.tui.panels.base import BasePanel
from core.tui.state import OrchestratorSnapshot


class AuthPanel(BasePanel):
    """Displays authentication sessions and roles."""

    PANEL_ID = "auth"
    DEFAULT_TITLE = "Auth"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._table: DataTable | None = None

    def compose(self) -> ComposeResult:
        yield Static("Sessioni e ruoli", classes="panel-title")
        table = DataTable(zebra_stripes=True, id="auth-table")
        table.add_columns("Utente", "Ruolo", "Attivo", "Ultima vista", "IP")
        self._table = table
        yield table

    def refresh(self, snapshot: OrchestratorSnapshot) -> None:
        if not self._table:
            return

        self._table.clear(columns=False)
        now = datetime.utcnow()
        for session in snapshot.auth_sessions:
            minutes_ago = (now - session.last_seen).total_seconds() / 60
            last_seen = f"{minutes_ago:.0f}m fa"
            self._table.add_row(
                session.user,
                session.role,
                "yes" if session.active else "no",
                last_seen,
                session.source_ip or "—",
            )
