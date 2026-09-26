"""Unit tests for Email value object."""

from dataclasses import FrozenInstanceError

import pytest

from src.auth.domain.value_objects import Email


def test_valid_email() -> None:
    """Should create Email with valid format."""
    email = Email("test@example.com")
    assert email.value == "test@example.com"


def test_invalid_email_format() -> None:
    """Should raise ValueError for invalid email format."""
    with pytest.raises(ValueError, match="Invalid email format"):
        Email("invalid-email")


def test_email_without_at_sign() -> None:
    """Should raise ValueError for email without @ sign."""
    with pytest.raises(ValueError, match="Invalid email format"):
        Email("testexample.com")


def test_email_without_domain() -> None:
    """Should raise ValueError for email without domain."""
    with pytest.raises(ValueError, match="Invalid email format"):
        Email("test@")


def test_email_equality() -> None:
    """Should consider two emails with same value as equal."""
    email1 = Email("test@example.com")
    email2 = Email("test@example.com")
    assert email1 == email2


def test_email_inequality() -> None:
    """Should consider two emails with different values as not equal."""
    email1 = Email("test@example.com")
    email2 = Email("other@example.com")
    assert email1 != email2


def test_email_immutability() -> None:
    """Should be immutable (frozen dataclass)."""
    email = Email("test@example.com")
    with pytest.raises(FrozenInstanceError):
        email.value = "other@example.com"
