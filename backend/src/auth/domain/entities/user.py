"""User domain entity."""

from datetime import datetime, timezone
from uuid import UUID

from src.auth.domain.value_objects import Email, Role
from src.shared.domain.entity import Entity


class User(Entity):
    """User entity representing a system user."""

    def __init__(
        self,
        id: UUID,
        email: Email,
        hashed_password: str,
        first_name: str,
        last_name: str,
        role: Role,
        is_active: bool = True,
        created_at: datetime | None = None,
    ) -> None:
        """Initialize user entity."""
        super().__init__(id)
        self.email = email
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)

    def get_full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}"
