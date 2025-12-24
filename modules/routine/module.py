from __future__ import annotations

from typing import List, Optional

from core.memory_store import MemoryStore


class RoutineModule:
    """
    Tracks routines and recurring tasks.
    """

    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()
        self.namespace = "routine"

    def add_task(self, task: str) -> str:
        tasks = self._get_tasks()
        tasks.append(task)
        self.store.store_fact(self.namespace, "\n".join(tasks))
        self.store.log_event("routine_task_added", {"task": task})
        return task

    def list_tasks(self) -> List[str]:
        return self._get_tasks()

    def _get_tasks(self) -> List[str]:
        fact = self.store.get_fact(self.namespace)
        if not fact:
            return []
        return [line for line in fact.split("\n") if line]

    def run(self, action: str, **kwargs):
        if action == "add":
            return self.add_task(kwargs["task"])
        if action == "list":
            return self.list_tasks()
        raise ValueError(f"Unknown action: {action}")
