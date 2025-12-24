from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional


class MemoryStore:
    """
    SQLite-backed append-only memory store with facts.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS facts (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

    def log_event(self, kind: str, payload: Dict) -> int:
        record = (time.time(), kind, json.dumps(payload))
        with self._lock, self._conn:
            cursor = self._conn.execute("INSERT INTO events (ts, kind, payload) VALUES (?, ?, ?)", record)
            return cursor.lastrowid

    def get_events(self, limit: Optional[int] = None, keyword: Optional[str] = None) -> List[Dict]:
        query = "SELECT id, ts, kind, payload FROM events"
        params = []
        if keyword:
            query += " WHERE payload LIKE ?"
            params.append(f"%{keyword}%")
        query += " ORDER BY id DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor = self._conn.execute(query, params)
        events = []
        for row in cursor.fetchall():
            events.append(
                {"id": row["id"], "ts": row["ts"], "kind": row["kind"], "payload": json.loads(row["payload"])}
            )
        return events

    def store_fact(self, key: str, value: str):
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO facts(key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (key, value),
            )

    def get_fact(self, key: str) -> Optional[str]:
        cursor = self._conn.execute("SELECT value FROM facts WHERE key=?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else None

    def search_events(self, keyword: str, limit: int = 10) -> List[Dict]:
        return self.get_events(limit=limit, keyword=keyword)

    def close(self):
        self._conn.close()
