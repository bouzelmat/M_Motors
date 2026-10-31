"""HTTPS redirect middleware."""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.infrastructure.config import get_settings


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect HTTP requests to HTTPS outside development."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()

        # CORRECTION : Ne pas rediriger les health checks
        if request.url.path == "/health":
            return await call_next(request)

        scheme = (
            request.headers.get("X-Forwarded-Proto", request.url.scheme)
            if settings.environment != "development"
            else request.url.scheme
        )
        if scheme == "http" and settings.environment != "development":
            https_url = request.url.replace(scheme="https")
            return Response(
                status_code=301,
                headers={"Location": str(https_url)},
            )
        return await call_next(request)
