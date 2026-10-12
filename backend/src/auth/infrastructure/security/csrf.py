"""CSRF token helpers and authentication middleware."""

import hashlib
import hmac
import secrets
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.infrastructure.config import get_settings


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def sign_csrf_token(token: str) -> str:
    secret = get_settings().secret_key.encode()
    digest = hmac.new(secret, token.encode(), hashlib.sha256).hexdigest()
    return f"{token}.{digest}"


def verify_csrf_token(cookie_token: str | None, header_token: str | None) -> bool:
    if not cookie_token or not header_token:
        return False
    try:
        token, signature = cookie_token.split(".", 1)
    except ValueError:
        return False
    if not hmac.compare_digest(
        signature,
        hmac.new(
            get_settings().secret_key.encode(), token.encode(), hashlib.sha256
        ).hexdigest(),
    ):
        return False
    return hmac.compare_digest(token, header_token)


class CSRFMiddleware(BaseHTTPMiddleware):
    """Require a CSRF header and cookie on state-changing requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return await call_next(request)
        if request.url.path.startswith("/api/"):
            return await call_next(request)
        cookie_value = request.cookies.get(get_settings().csrf_cookie_name)
        header_value = request.headers.get(get_settings().csrf_header_name)
        if not verify_csrf_token(cookie_value, header_value):
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token is missing or invalid"},
            )
        return await call_next(request)
