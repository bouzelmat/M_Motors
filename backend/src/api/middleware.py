"""Middleware for request/response logging with sensitive data sanitization."""

import logging
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


class SanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware to sanitize sensitive data in logs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and sanitize sensitive data in logs."""
        # Log request without sensitive data
        path = request.url.path
        method = request.method

        # Don't log auth endpoints with sensitive data
        if path in ["/api/v1/auth/login", "/api/v1/auth/register"]:
            logger.info(f"{method} {path} - [REDACTED]")
        else:
            logger.info(f"{method} {path}")

        response = await call_next(request)

        return response


def get_middleware() -> list[tuple[type, dict]]:
    """Get list of middleware for the application."""
    return [
        (
            CORSMiddleware,
            {"allow_origins": ["*"], "allow_methods": ["*"], "allow_headers": ["*"]},
        ),
        (SanitizationMiddleware, {}),
    ]
