"""Password hashing service.

Uses PBKDF2-SHA256 via passlib to avoid runtime dependency on the native
`bcrypt` package (which in some environments triggers import/version issues
and enforces a 72-byte limit). PBKDF2-SHA256 provides secure hashing and is
fully supported by passlib without external C extensions.
"""

from passlib.context import CryptContext


class PasswordService:
    """Service for hashing and verifying passwords using PBKDF2-SHA256."""

    def __init__(self) -> None:
        """Initialize password service with a safer, pure-python-friendly scheme."""
        # pbkdf2_sha256 does not have bcrypt's 72-byte truncation behaviour and
        # avoids depending on the `bcrypt` C-extension which caused import
        # problems in some CI/dev environments.
        self._pwd_context = CryptContext(
            schemes=["pbkdf2_sha256"],
            deprecated="auto",
        )

    def hash_password(self, password: str) -> str:
        """Hash a plain text password."""
        if not isinstance(password, str):
            password = str(password)
        return self._pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        if not isinstance(plain_password, str):
            plain_password = str(plain_password)
        return self._pwd_context.verify(plain_password, hashed_password)