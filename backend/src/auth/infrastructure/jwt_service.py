"""JWT token service for authentication."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from src.config import get_settings


class JWTService:
    """Service for generating and verifying JWT tokens."""

    def __init__(self) -> None:
        """Initialize JWT service with settings."""
        settings = get_settings()
        self._secret_key = settings.secret_key if hasattr(settings, "secret_key") else "default-secret-key-change-in-production"
        self._algorithm = "HS256"
        self._access_token_expire_minutes = 30

    def create_access_token(self, data: dict[str, Any]) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._access_token_expire_minutes
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and verify a JWT token."""
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except JWTError as e:
            raise ValueError("Invalid token") from e
