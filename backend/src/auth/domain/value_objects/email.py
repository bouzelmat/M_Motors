"""Email value object with validation."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Immutable email value object with format validation."""

    value: str

    def __post_init__(self) -> None:
        """Validate email format on construction."""
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        """Check if email format is valid."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
