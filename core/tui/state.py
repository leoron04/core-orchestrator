"""Shared data structures and providers for the TUI.

This module centralizes the orchestration snapshot models and exposes a
provider that can be backed either by the real orchestrator or by demo data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Iterable, Mapping, Optional


@dataclass
class ModuleInfo:
    """Runtime information for a single module."""

    name: str
    status: str
    uptime: timedelta
    version: str
    health: str = "unknown"


@dataclass
class DeviceInfo:
    """Hardware device health details."""

    name: str
    kind: str
    health: str
    cpu: float
    memory: float
    temperature: float


@dataclass
class AIJob:
    """AI job or agent activity."""

    job_id: str
    model: str
    status: str
    progress: float
    owner: str


@dataclass
class NetworkLink:
    """Network link status for orchestrated devices."""

    name: str
    latency_ms: float
    bandwidth_mbps: float
    status: str
    jitter_ms: float | None = None


@dataclass
class AuthSession:
    """Authentication and authorization session info."""

    user: str
    role: str
    last_seen: datetime
    active: bool
    source_ip: str | None = None


@dataclass
class OrchestratorSnapshot:
    """Aggregated view of orchestrator state for the TUI."""

    modules: list[ModuleInfo] = field(default_factory=list)
    devices: list[DeviceInfo] = field(default_factory=list)
    ai_jobs: list[AIJob] = field(default_factory=list)
    network: list[NetworkLink] = field(default_factory=list)
    auth_sessions: list[AuthSession] = field(default_factory=list)
    dashboard_metrics: Mapping[str, str | int | float] = field(default_factory=dict)
    message: Optional[str] = None


class OrchestratorDataProvider:
    """Fetch snapshots from a real orchestrator or demo data.

    Parameters
    ----------
    loader:
        Optional callable that returns an :class:`OrchestratorSnapshot`. If not
        provided, a demo generator is used so that the TUI can run offline.
    """

    def __init__(self, loader: Callable[[], OrchestratorSnapshot] | None = None) -> None:
        self._loader = loader or self._load_demo_snapshot

    def fetch(self) -> OrchestratorSnapshot:
        """Return the latest orchestrator snapshot."""

        return self._loader()

    def _load_demo_snapshot(self) -> OrchestratorSnapshot:
        """Return a demo snapshot with plausible fake data."""

        now = datetime.utcnow()
        return OrchestratorSnapshot(
            modules=[
                ModuleInfo(
                    name="planner",
                    status="running",
                    uptime=timedelta(hours=5, minutes=42),
                    version="1.4.2",
                    health="ok",
                ),
                ModuleInfo(
                    name="scheduler",
                    status="running",
                    uptime=timedelta(hours=12, minutes=7),
                    version="1.4.2",
                    health="ok",
                ),
                ModuleInfo(
                    name="sensor-fusion",
                    status="degraded",
                    uptime=timedelta(hours=1, minutes=3),
                    version="0.9.8",
                    health="warn",
                ),
            ],
            devices=[
                DeviceInfo(
                    name="edge-node-01",
                    kind="x86_64",
                    health="ok",
                    cpu=42.0,
                    memory=61.0,
                    temperature=62.0,
                ),
                DeviceInfo(
                    name="edge-node-02",
                    kind="jetson",
                    health="warn",
                    cpu=73.0,
                    memory=82.0,
                    temperature=74.0,
                ),
            ],
            ai_jobs=[
                AIJob(
                    job_id="job-214",
                    model="gpt-vision",
                    status="running",
                    progress=0.68,
                    owner="autonomy",
                ),
                AIJob(
                    job_id="job-187",
                    model="planner-large",
                    status="queued",
                    progress=0.0,
                    owner="mission-control",
                ),
            ],
            network=[
                NetworkLink(
                    name="wan",
                    latency_ms=34.5,
                    bandwidth_mbps=120.0,
                    status="stable",
                    jitter_ms=2.1,
                ),
                NetworkLink(
                    name="lan",
                    latency_ms=2.3,
                    bandwidth_mbps=940.0,
                    status="stable",
                    jitter_ms=0.5,
                ),
            ],
            auth_sessions=[
                AuthSession(
                    user="ops",
                    role="admin",
                    last_seen=now - timedelta(minutes=3),
                    active=True,
                    source_ip="10.0.0.12",
                ),
                AuthSession(
                    user="automation",
                    role="service",
                    last_seen=now - timedelta(minutes=12),
                    active=True,
                    source_ip="10.0.0.32",
                ),
                AuthSession(
                    user="analyst",
                    role="viewer",
                    last_seen=now - timedelta(hours=2),
                    active=False,
                    source_ip="192.168.1.23",
                ),
            ],
            dashboard_metrics={
                "modules": 3,
                "devices": 2,
                "ai_jobs": 2,
                "alerts": 1,
                "uptime_hours": 12.5,
            },
            message="Demo snapshot loaded",
        )


def format_timedelta(delta: timedelta) -> str:
    """Render a ``timedelta`` into a compact human-readable string."""

    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def percent(value: float) -> str:
    """Format a floating ratio into a percentage string."""

    bounded = min(max(value, 0.0), 1.0)
    return f"{bounded * 100:.0f}%"
