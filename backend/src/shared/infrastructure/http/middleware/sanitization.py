"""Request logging middleware with sensitive-path redaction."""

import logging
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitize authentication paths in request logs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method
        if path in ["/api/v1/auth/login", "/api/v1/auth/register"]:
            logger.info(f"{method} {path} [REDACTED]")
        else:
            logger.info(f"{method} {path}")
        return await call_next(request)
