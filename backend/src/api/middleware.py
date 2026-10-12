"""Middleware for request/response logging with sensitive data sanitization."""

import hashlib
import hmac
import logging
import secrets
import time
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from src.config import get_settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )
        response.headers.setdefault(
            "Permissions-Policy",
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()",
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; connect-src 'self' http://localhost:5173 http://127.0.0.1:5173 http://localhost:3000 http://127.0.0.1:3000",
        )
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")

        settings = get_settings()
        if settings.environment != "development":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=63072000; includeSubDomains; preload",
            )
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Redirige HTTP vers HTTPS en production (toléré en dev/local).
    🔴 CORRECTION: Lit X-Forwarded-Proto pour les reverse proxies (Problème 5).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
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


class SanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware to sanitize sensitive data in logs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method
        if path in ["/api/v1/auth/login", "/api/v1/auth/register"]:
            logger.info(f"{method} {path} [REDACTED]")
        else:
            logger.info(f"{method} {path}")
        response = await call_next(request)
        return response


class RateLimitStore:
    """Simple in-memory login throttling store for a single process."""

    def __init__(self) -> None:
        self._attempts: dict[str, list[float]] = {}

    def _prune(self, ip: str, now: float) -> None:
        window_seconds = get_settings().rate_limit_window_seconds
        self._attempts[ip] = [
            ts for ts in self._attempts.get(ip, []) if now - ts < window_seconds
        ]

    def check(self, ip: str) -> int | None:
        now = time.monotonic()
        self._prune(ip, now)
        attempts = self._attempts.get(ip, [])
        if len(attempts) >= get_settings().rate_limit_max_failures:
            retry_after = max(
                1,
                int(get_settings().rate_limit_window_seconds - (now - attempts[0])),
            )
            return retry_after
        return None

    def record_failure(self, ip: str) -> None:
        now = time.monotonic()
        self._attempts.setdefault(ip, [])
        self._attempts[ip].append(now)
        self._prune(ip, now)

    def record_success(self, ip: str) -> None:
        self._attempts.pop(ip, None)


_LOGIN_RATE_LIMIT_STORE = RateLimitStore()


def get_client_ip(request: Request) -> str:
    """Return the client IP while ignoring untrusted proxy headers."""
    settings = get_settings()
    peer_ip = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded and peer_ip in set(settings.trusted_proxy_ips):
        candidate_ips = [item.strip() for item in forwarded.split(",") if item.strip()]
        if candidate_ips:
            return candidate_ips[0]
    return peer_ip


def get_login_rate_limit_retry_after(ip: str) -> int:
    retry_after = _LOGIN_RATE_LIMIT_STORE.check(ip)
    return retry_after if retry_after is not None else 0


def record_login_failure(ip: str) -> None:
    _LOGIN_RATE_LIMIT_STORE.record_failure(ip)


def record_login_success(ip: str) -> None:
    _LOGIN_RATE_LIMIT_STORE.record_success(ip)


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


class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """Placeholder for future security telemetry hooks."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        return await call_next(request)


def get_middleware() -> list[tuple[type, dict]]:
    """Get list of middleware for the application.
    🔴 CORRECTION: Réordonné (Problème 4).
    """
    settings = get_settings()
    allowed_origins = settings.allowed_cors_origins or [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    return [
        (HTTPSRedirectMiddleware, {}),  # Premier (exécuté en dernier par Starlette)
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
