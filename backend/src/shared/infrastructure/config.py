"""Application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
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
    database_url: str = Field(
        ..., validation_alias=AliasChoices("database_url", "DATABASE_URL")
    )

    # ---- Security ----
    secret_key: str = Field(
        ...,
        min_length=32,
        validation_alias=AliasChoices("secret_key", "SECRET_KEY", "JWT_SECRET_KEY"),
    )
    allowed_cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        validation_alias=AliasChoices("allowed_cors_origins", "CORS_ALLOWED_ORIGINS"),
    )
    trusted_proxy_ips: list[str] = Field(
        default_factory=lambda: ["127.0.0.1", "::1", "testclient"],
        validation_alias=AliasChoices("trusted_proxy_ips", "TRUSTED_PROXY_IPS"),
    )
    rate_limit_window_seconds: int = 60
    rate_limit_max_failures: int = 5
    csrf_cookie_name: str = "csrf_token"
    csrf_header_name: str = "X-CSRF-Token"
    csrf_token_ttl_seconds: int = 3600

    # ---- AWS / S3 Storage ----
    s3_bucket_name: str = "m-motors-photos"
    s3_documents_bucket_name: str = "m-motors-documents"
    aws_region: str = "eu-west-3"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_endpoint_url: str | None = None
    aws_public_endpoint_url: str | None = None

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "database_url must start with 'postgresql+asyncpg://' (asyncpg dialect)"
            )
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        insecure_values = {
            "default-secret-key-change-in-production",
            "change-me-in-production",
            "development-secret-key",
            "secret",
        }
        if not v or v in insecure_values:
            raise ValueError(
                "secret_key must be set to a non-default value from the environment"
            )
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
