from __future__ import annotations

from typing import List


class SecurityHygieneModule:
    """
    Provides reminders and quick checks for common hygiene tasks.
    """

    CHECKLIST = [
        "Update operating system and packages",
        "Rotate SSH keys and credentials",
        "Review MFA status on critical accounts",
        "Audit running services",
        "Review firewall rules",
    ]

    def checklist(self) -> List[str]:
        return self.CHECKLIST

    def run(self, action: str):
        if action == "checklist":
            return self.checklist()
        raise ValueError(f"Unknown action: {action}")
