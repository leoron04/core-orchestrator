"""Panel exports for the TUI."""

from core.tui.panels.ai_panel import AIPanel
from core.tui.panels.auth_panel import AuthPanel
from core.tui.panels.dashboard import DashboardPanel
from core.tui.panels.device_panel import DevicePanel
from core.tui.panels.modules_panel import ModulesPanel
from core.tui.panels.network_panel import NetworkPanel

__all__ = [
    "AIPanel",
    "AuthPanel",
    "DashboardPanel",
    "DevicePanel",
    "ModulesPanel",
    "NetworkPanel",
]
