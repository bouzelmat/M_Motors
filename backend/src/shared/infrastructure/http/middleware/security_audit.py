"""Security audit middleware."""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """Placeholder for future security telemetry hooks."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        return await call_next(request)
