"""User repository interface (Protocol)."""

from typing import Protocol
from uuid import UUID

from src.auth.domain.entities.user import User
from src.auth.domain.value_objects import Email


class UserRepository(Protocol):
    """Protocol for User repository operations."""

    async def save(self, user: User) -> None:
        """Save a user to the repository."""
        ...

    async def find_by_email(self, email: Email) -> User | None:
        """Find a user by email address."""
        ...

    async def find_by_id(self, user_id: UUID) -> User | None:
        """Find a user by ID."""
        ...

    async def email_exists(self, email: Email) -> bool:
        """Check if an email already exists in the repository."""
        ...
