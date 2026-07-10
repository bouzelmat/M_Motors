"""User role enumeration."""

from enum import Enum


class Role(str, Enum):
    """User roles in the system."""

    CLIENT = "CLIENT"
    ADMIN = "ADMIN"
