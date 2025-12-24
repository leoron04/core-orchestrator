from __future__ import annotations

from typing import List, Optional

from core.memory_store import MemoryStore


class NotesModule:
    """
    Simple note taking module backed by MemoryStore facts.
    """

    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()
        self.namespace = "notes"

    def add_note(self, text: str) -> str:
        notes = self._get_notes()
        notes.append(text)
        self.store.store_fact(self.namespace, "\n".join(notes))
        self.store.log_event("note_added", {"text": text})
        return text

    def list_notes(self) -> List[str]:
        return self._get_notes()

    def _get_notes(self) -> List[str]:
        fact = self.store.get_fact(self.namespace)
        if not fact:
            return []
        return [line for line in fact.split("\n") if line]

    def run(self, action: str, **kwargs):
        if action == "add":
            return self.add_note(kwargs["text"])
        if action == "list":
            return self.list_notes()
        raise ValueError(f"Unknown action: {action}")
