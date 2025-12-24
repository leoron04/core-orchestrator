from __future__ import annotations

from typing import Iterable


class PolicyGate:
    """
    Very light heuristic policy classifier.
    """

    SAFE = "SAFE"
    CONFIRM = "CONFIRM"
    BLOCKED = "BLOCKED"

    BLOCKLIST = {"delete system32", "format /dev", "rm -rf /"}
    CONFIRM_LIST = {"shutdown", "reboot", "restart"}

    def classify(self, text: str) -> str:
        normalized = text.lower()
        for token in self.BLOCKLIST:
            if token in normalized:
                return self.BLOCKED
        for token in self.CONFIRM_LIST:
            if token in normalized:
                return self.CONFIRM
        return self.SAFE

    def classify_messages(self, messages: Iterable[dict]) -> str:
        combined = " ".join([m.get("content", "") for m in messages])
        return self.classify(combined)
