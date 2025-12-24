"""Domain models for the Core Orchestrator."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class OrchestratorBaseModel(BaseModel):
    """Pydantic base model configured for ORM compatibility."""

    class Config:
        from_attributes = True


class OrchestratorOrmBase(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


class ActionLog(OrchestratorOrmBase):
    """Example persisted log of orchestrator actions."""

    __tablename__ = "action_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def to_model(self) -> "ActionLogModel":
        return ActionLogModel(
            id=self.id,
            tool=self.tool,
            action=self.action,
            status=self.status,
            created_at=self.created_at,
        )


class ActionLogModel(OrchestratorBaseModel):
    """Pydantic representation of an action log entry."""

    id: Optional[int] = Field(None, description="Primary key.")
    tool: str
    action: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)


__all__ = [
    "ActionLog",
    "ActionLogModel",
    "OrchestratorBaseModel",
    "OrchestratorOrmBase",
]
