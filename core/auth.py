"""Authentication and authorization primitives."""

from __future__ import annotations

import functools
import logging
from enum import Enum
from typing import Any, Callable, Optional

import keyring
from pydantic import BaseModel, Field
from sqlalchemy import Column, Enum as SAEnum, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)


class Role(str, Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


class Base(BaseModel):
    """Base Pydantic model with orm support."""

    class Config:
        from_attributes = True


class AuthUser(Base):
    username: str
    role: Role = Role.GUEST
    token: Optional[str] = None


class Credentials(Base):
    username: str
    password: str = Field("", description="Optional password for user login.")


class OrmBase(DeclarativeBase):
    """SQLAlchemy declarative base for persistence."""


class UserRecord(OrmBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[Role] = mapped_column(SAEnum(Role), default=Role.USER, nullable=False)
    token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def to_model(self) -> AuthUser:
        return AuthUser(username=self.username, role=self.role, token=self.token)


class AuthProvider:
    """Provider responsible for issuing and validating authentication tokens."""

    def __init__(self, service_name: str = "core-orchestrator") -> None:
        self.service_name = service_name

    def login_guest(self) -> AuthUser:
        """Create a guest session without persistence."""

        logger.info("Logging in as guest")
        return AuthUser(username="guest", role=Role.GUEST, token=None)

    def store_token(self, username: str, token: str) -> None:
        """Persist a token in the OS keyring."""

        keyring.set_password(self.service_name, username, token)
        logger.debug("Stored token for user %s", username)

    def retrieve_token(self, username: str) -> Optional[str]:
        """Fetch a token from the OS keyring if it exists."""

        token = keyring.get_password(self.service_name, username)
        logger.debug("Retrieved token for %s: %s", username, bool(token))
        return token

    def login(self, credentials: Credentials) -> AuthUser:
        """Simulated login flow that issues a token and persists it."""

        token = f"token-{credentials.username}"
        self.store_token(credentials.username, token)
        return AuthUser(username=credentials.username, role=Role.USER, token=token)

    def elevate(self, user: AuthUser) -> AuthUser:
        """Elevate a user to admin for privileged operations (placeholder)."""

        logger.warning("Elevating user %s to admin (placeholder)", user.username)
        return AuthUser(username=user.username, role=Role.ADMIN, token=user.token)


def require_role(required: Role) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator enforcing role-based access on functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(user: AuthUser, *args: Any, **kwargs: Any):
            if user.role not in {required, Role.ADMIN}:
                msg = f"User {user.username} lacks required role {required}"
                logger.error(msg)
                raise PermissionError(msg)
            return func(user, *args, **kwargs)

        return wrapper

    return decorator


__all__ = [
    "Role",
    "AuthUser",
    "Credentials",
    "AuthProvider",
    "UserRecord",
    "OrmBase",
    "require_role",
]
