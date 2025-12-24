from __future__ import annotations

from typing import Dict


class DeviceGuideModule:
    """
    Offers short device setup and troubleshooting guides.
    """

    GUIDES: Dict[str, str] = {
        "wifi": "Check router lights, reboot, verify SSID/password, forget and reconnect.",
        "bluetooth": "Ensure device discoverable, toggle Bluetooth, remove stale pairings.",
        "battery": "Calibrate by full discharge/charge cycle, review power settings.",
    }

    def guide(self, topic: str) -> str:
        return self.GUIDES.get(topic, "Guide not found.")

    def run(self, action: str, **kwargs):
        if action == "guide":
            return self.guide(kwargs.get("topic", ""))
        raise ValueError(f"Unknown action: {action}")
