"""Composition of application-wide HTTP middleware."""

from starlette.middleware.cors import CORSMiddleware

from src.auth.infrastructure.security.csrf import CSRFMiddleware
from src.shared.infrastructure.config import get_settings
from src.shared.infrastructure.http.middleware.https_redirect import (
    HTTPSRedirectMiddleware,
)
from src.shared.infrastructure.http.middleware.sanitization import (
    SanitizationMiddleware,
)
from src.shared.infrastructure.http.middleware.security_headers import (
    SecurityHeadersMiddleware,
)


def get_middleware() -> list[tuple[type, dict]]:
    """Return middleware in the registration order expected by Starlette."""
    settings = get_settings()
    allowed_origins = settings.allowed_cors_origins or [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    return [
        (HTTPSRedirectMiddleware, {}),
        (
            CORSMiddleware,
            {
                "allow_origins": allowed_origins,
                "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Authorization",
                    "Content-Type",
                    "Accept",
                    "Origin",
                    "X-CSRF-Token",
                ],
                "allow_credentials": True,
            },
        ),
        (SecurityHeadersMiddleware, {}),
        (CSRFMiddleware, {}),
        (SanitizationMiddleware, {}),
    ]
