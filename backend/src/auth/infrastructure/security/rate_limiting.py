"""In-memory rate limiting helpers for authentication requests."""

import time

from fastapi import Request

from src.shared.infrastructure.config import get_settings


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
