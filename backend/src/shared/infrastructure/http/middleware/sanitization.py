"""Request logging middleware with sensitive-path redaction."""

import logging
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitize authentication paths in request logs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        path = request.url.path
        method = request.method
        path_log = (
            "[REDACTED]"
            if path
            in [
                "/api/v1/auth/login",
                "/api/v1/auth/register",
            ]
            else path
        )

        try:
            response = await call_next(request)
            log_method = (
                logger.error
                if response.status_code >= 500
                else logger.warning if response.status_code >= 400 else logger.info
            )
            log_method(
                "request_completed method=%s path=%s status_code=%s request_id=%s",
                method,
                path_log,
                response.status_code,
                request_id,
            )
        except Exception:
            logger.exception(
                "request_failed method=%s path=%s request_id=%s",
                method,
                path_log,
                request_id,
            )
            raise

        response.headers["X-Request-ID"] = request_id
        return response
