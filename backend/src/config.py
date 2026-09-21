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

    # ---- Database ----
    database_url: str

    # ---- Security ----
    secret_key: str = "default-secret-key-change-in-production"

    # ---- AWS / S3 Storage ----
    s3_bucket_name: str = "m-motors-photos"
    s3_documents_bucket_name: str = "m-motors-documents"
    aws_region: str = "eu-west-3"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_endpoint_url: str | None = None

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "database_url must start with 'postgresql+asyncpg://' (asyncpg dialect)"
            )
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
