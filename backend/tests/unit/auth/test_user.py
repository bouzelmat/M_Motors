"""Unit tests for User entity."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.auth.domain.entities import User
from src.auth.domain.value_objects import Email, Role


def test_user_creation() -> None:
    """Should create User with valid attributes."""
    user_id = uuid4()
    email = Email("test@example.com")
    user = User(
        id=user_id,
        email=email,
        hashed_password="hashed_password",
        first_name="John",
        last_name="Doe",
        role=Role.CLIENT,
    )
    assert user.id == user_id
    assert user.email == email
    assert user.hashed_password == "hashed_password"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.role == Role.CLIENT
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)


def test_user_with_custom_created_at() -> None:
    """Should create User with custom created_at timestamp."""
    user_id = uuid4()
    email = Email("test@example.com")
    created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    user = User(
        id=user_id,
        email=email,
        hashed_password="hashed_password",
        first_name="John",
        last_name="Doe",
        role=Role.CLIENT,
        created_at=created_at,
    )
    assert user.created_at == created_at


def test_user_with_is_active_false() -> None:
    """Should create User with is_active set to False."""
    user_id = uuid4()
    email = Email("test@example.com")
    user = User(
        id=user_id,
        email=email,
        hashed_password="hashed_password",
        first_name="John",
        last_name="Doe",
        role=Role.CLIENT,
        is_active=False,
    )
    assert user.is_active is False


def test_user_get_full_name() -> None:
    """Should return full name combining first and last name."""
    user_id = uuid4()
    email = Email("test@example.com")
    user = User(
        id=user_id,
        email=email,
        hashed_password="hashed_password",
        first_name="John",
        last_name="Doe",
        role=Role.CLIENT,
    )
    assert user.get_full_name() == "John Doe"


def test_user_equality_by_id() -> None:
    """Should consider two users with same id as equal."""
    user_id = uuid4()
    email1 = Email("test1@example.com")
    email2 = Email("test2@example.com")
    user1 = User(
        id=user_id,
        email=email1,
        hashed_password="hashed1",
        first_name="John",
        last_name="Doe",
        role=Role.CLIENT,
    )
    user2 = User(
        id=user_id,
        email=email2,
        hashed_password="hashed2",
        first_name="Jane",
        last_name="Smith",
        role=Role.ADMIN,
    )
    assert user1 == user2


def test_user_inequality_by_id() -> None:
    """Should consider two users with different ids as not equal."""
    email = Email("test@example.com")
    user1 = User(
        id=uuid4(),
        email=email,
        hashed_password="hashed1",
        first_name="John",
        last_name="Doe",
        role=Role.CLIENT,
    )
    user2 = User(
        id=uuid4(),
        email=email,
        hashed_password="hashed2",
        first_name="John",
        last_name="Doe",
        role=Role.CLIENT,
    )
    assert user1 != user2


def test_user_with_admin_role() -> None:
    """Should create User with ADMIN role."""
    user_id = uuid4()
    email = Email("admin@example.com")
    user = User(
        id=user_id,
        email=email,
        hashed_password="hashed_password",
        first_name="Admin",
        last_name="User",
        role=Role.ADMIN,
    )
    assert user.role == Role.ADMIN
