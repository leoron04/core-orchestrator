"""Registry for orchestrator tools and actions described via JSON manifests."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator

logger = logging.getLogger(__name__)


class Parameter(BaseModel):
    """Parameter specification for a registry action."""

    name: str
    type: str = Field(..., description="The expected type of the parameter (for documentation).")
    description: str = Field("", description="Human-readable explanation of the parameter.")
    required: bool = Field(True, description="Whether the parameter must be provided.")
    default: Optional[str] = Field(None, description="Optional default value.")


class ActionDefinition(BaseModel):
    """Action available within a tool manifest."""

    name: str
    description: str
    parameters: List[Parameter] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value:
            msg = "Action name cannot be empty"
            raise ValueError(msg)
        return value


class ToolManifest(BaseModel):
    """Manifest describing a tool and the actions it supports."""

    name: str
    version: str = "0.1.0"
    description: str = ""
    actions: List[ActionDefinition] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value:
            msg = "Tool name cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        if not value:
            msg = "Tool version cannot be empty"
            raise ValueError(msg)
        return value


@dataclass(slots=True)
class RegistryEntry:
    """Concrete entry stored in the registry index."""

    manifest: ToolManifest
    source_path: Path


class Registry:
    """Registry that loads tool manifests and exposes lookup APIs."""

    def __init__(self, manifest_path: Path | str = Path("./manifests")) -> None:
        self.manifest_path = Path(manifest_path)
        self._index: Dict[str, RegistryEntry] = {}

    def load(self) -> None:
        """Load all manifests from the configured path."""

        logger.info("Loading manifests from %s", self.manifest_path)
        self._index.clear()
        if not self.manifest_path.exists():
            logger.warning("Manifest path %s does not exist", self.manifest_path)
            return

        for manifest_file in self.manifest_files:
            manifest = self._load_manifest(manifest_file)
            if manifest:
                self._index[manifest.name] = RegistryEntry(
                    manifest=manifest, source_path=manifest_file
                )

    @property
    def manifest_files(self) -> Iterable[Path]:
        """Yield JSON manifest files from the manifest path."""

        return sorted(self.manifest_path.glob("*.json"))

    def _load_manifest(self, manifest_file: Path) -> Optional[ToolManifest]:
        try:
            raw = manifest_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            manifest = ToolManifest.model_validate(data)
            logger.debug("Loaded manifest %s", manifest.name)
            return manifest
        except FileNotFoundError:
            logger.error("Manifest file %s missing", manifest_file)
        except json.JSONDecodeError as exc:
            logger.error("Malformed JSON in %s: %s", manifest_file, exc)
        except ValidationError as exc:
            logger.error("Validation error in %s: %s", manifest_file, exc)
        return None

    def list_tools(self) -> List[str]:
        """Return a list of loaded tool identifiers."""

        return sorted(self._index.keys())

    def get_tool(self, name: str) -> Optional[ToolManifest]:
        """Retrieve a tool manifest by name."""

        entry = self._index.get(name)
        return entry.manifest if entry else None

    def list_actions(self, tool_name: str) -> List[str]:
        """List action names for a given tool."""

        tool = self.get_tool(tool_name)
        if not tool:
            return []
        return [action.name for action in tool.actions]

    def lookup_action(self, tool_name: str, action_name: str) -> Optional[ActionDefinition]:
        """Retrieve an action definition for a given tool."""

        tool = self.get_tool(tool_name)
        if not tool:
            return None
        for action in tool.actions:
            if action.name == action_name:
                return action
        return None

    def reload(self) -> None:
        """Reload manifests from disk, replacing any existing index."""

        self.load()

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._index)

    def __iter__(self):  # pragma: no cover - convenience
        for entry in self._index.values():
            yield entry.manifest


__all__ = [
    "Registry",
    "RegistryEntry",
    "ToolManifest",
    "ActionDefinition",
    "Parameter",
]
