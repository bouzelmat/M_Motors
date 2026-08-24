"""Application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = "M-Motors API"
    environment: Literal["development", "staging", "production"] = "development"

    # ---- Database (strictement nécessaire pour le health check et la session SQLAlchemy) ----
    database_url: str

    # ---- Security ----
    secret_key: str = "default-secret-key-change-in-production"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        Ensure the database URL uses the asyncpg dialect required for async SQLAlchemy.

        This validator enforces that the URL starts with 'postgresql+asyncpg://'.
        Using the synchronous dialect ('postgresql://') would cause runtime errors
        because the application uses async SQLAlchemy (create_async_engine).
        """
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "database_url must start with 'postgresql+asyncpg://' (asyncpg dialect)"
            )
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
