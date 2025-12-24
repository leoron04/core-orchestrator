"""Configuration utilities for the Core Orchestrator."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseSettings, Field


class AppSettings(BaseSettings):
    """Application-level settings loaded from environment or configuration files."""

    environment: str = Field(
        "development",
        description="Deployment environment (development/staging/production).",
    )
    data_path: Path = Field(
        Path("./data"), description="Root directory for persisted data such as manifests or logs."
    )
    registry_path: Path = Field(
        Path("./manifests"), description="Location of registry manifest JSON files."
    )
    enable_http2: bool = Field(
        True, description="Whether HTTP/2 should be enabled for outbound network clients."
    )

    class Config:
        env_prefix = "CORE_"
        env_file = ".env"


def load_settings(**overrides: Any) -> AppSettings:
    """Load settings with optional overrides supplied at runtime."""

    return AppSettings(**overrides)


def settings_as_dict(settings: Optional[AppSettings] = None) -> Dict[str, Any]:
    """Return a serializable view of current settings for logging or debugging."""

    current = settings or AppSettings()
    return current.model_dump()
