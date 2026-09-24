"""
Temporary block for clients that repeatedly send malicious messages.

Flow per chat request:
    1. retry_after(ip): if the HMAC(ip) has an active block, the endpoint answers 403.
    2. inspect(ip, message): runs the classifier in parallel with the agent; a
       malicious verdict adds a strike, and ABUSE_MAX_STRIKES strikes within
       ABUSE_STRIKE_WINDOW_HOURS block that IP for ABUSE_BLOCK_MINUTES.

State lives in a shared store (Upstash Redis over REST) so every Vercel
instance sees the same strikes and blocks. Any store or classifier failure is
fail-open: it is logged and the request goes on as if there were no guard.

This is a deterrent, not a security boundary: an IP is easy to change and a
shared NAT can penalise legitimate users. Hence ABUSE_MODE=log-only first.
"""

import logging
import os
import time
from collections.abc import Awaitable, Callable
from typing import Protocol

from starlette.requests import Request
from starlette.responses import JSONResponse

from core.abuse_classifier import AbuseClassifier, AbuseVerdict
from core.config import settings
from middleware.request_logger import hash_ip

logger = logging.getLogger("cv_chatbot.abuse")

KEY_PREFIX = "cvbot:abuse"


def client_ip(request: Request) -> str:
    """Client IP. On Vercel the edge overwrites these headers, so they cannot be spoofed."""
    if os.environ.get("VERCEL"):
        forwarded = request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip()
        if ip:
            return ip
    return request.client.host if request.client else "unknown"


class AbuseStore(Protocol):
    async def block_ttl(self, key: str) -> int:
        """Seconds left of the block (<= 0 when not blocked)."""

    async def add_strike(self, key: str, member: str, now: float, window_seconds: int) -> int:
        """Record a strike and return the strikes within the window."""

    async def block(self, key: str, seconds: int) -> None:
        """Block the key for `seconds` and clear its strikes."""


class UpstashRedisStore:
    """Upstash Redis REST API (a single HTTP call per operation, no connection pool)."""

    def __init__(self, url: str, token: str, timeout: float = 2.0, transport=None):
        self._url = url.rstrip("/") + "/pipeline"
        self._headers = {"Authorization": f"Bearer {token}"}
        self._timeout = timeout
        self._transport = transport  # tests inject httpx.MockTransport

    async def _pipeline(self, *commands: list) -> list:
        import httpx

        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(self._url, headers=self._headers, json=list(commands))
        response.raise_for_status()
        results = response.json()
        errors = [r["error"] for r in results if r.get("error")]
        if errors:
            raise RuntimeError(f"Redis error: {errors[0]}")
        return [r.get("result") for r in results]

    async def block_ttl(self, key: str) -> int:
        (ttl,) = await self._pipeline(["TTL", f"{KEY_PREFIX}:block:{key}"])
        return int(ttl)

    async def add_strike(self, key: str, member: str, now: float, window_seconds: int) -> int:
        strikes = f"{KEY_PREFIX}:strikes:{key}"
        # Sliding window: a sorted set scored by timestamp, pruned on every strike.
        results = await self._pipeline(
            ["ZADD", strikes, now, member],
            ["ZREMRANGEBYSCORE", strikes, "-inf", now - window_seconds],
            ["ZCARD", strikes],
            ["EXPIRE", strikes, window_seconds],
        )
        return int(results[2])

    async def block(self, key: str, seconds: int) -> None:
        await self._pipeline(
            ["SET", f"{KEY_PREFIX}:block:{key}", 1, "EX", seconds],
            ["DEL", f"{KEY_PREFIX}:strikes:{key}"],
        )


class AbuseGuard:
    def __init__(
        self,
        *,
        store: AbuseStore | None,
        classifier: Callable[[str], Awaitable[AbuseVerdict]],
        mode: str,
        max_strikes: int,
        block_seconds: int,
        window_seconds: int,
        clock: Callable[[], float] = time.time,
    ):
        self.store = store
        self.classifier = classifier
        self.mode = mode
        self.max_strikes = max_strikes
        self.block_seconds = block_seconds
        self.window_seconds = window_seconds
        self.clock = clock

    async def retry_after(self, ip: str) -> int | None:
        """Seconds until the IP may ask again, or None if it is not blocked."""
        if self.mode != "block" or self.store is None:
            return None
        try:
            ttl = await self.store.block_ttl(hash_ip(ip))
        except Exception as e:
            _log_store_error("block check", e)
            return None
        return ttl if ttl > 0 else None

    async def inspect(self, ip: str, message: str, request_id: str) -> AbuseVerdict | None:
        """Classify the message and apply strikes. Never raises."""
        if self.mode == "off":
            return None
        try:
            verdict = await self.classifier(message)
        except Exception as e:
            logger.warning(
                f"Abuse classifier failed: {str(e)[:200]}",
                extra={"request_id": request_id, "error_type": type(e).__name__},
            )
            return None
        if not verdict.malicious:
            return verdict

        ip_hash = hash_ip(ip)
        extra = {"request_id": request_id, "ip_hash": ip_hash, "abuse_category": verdict.category, "abuse_mode": self.mode}
        if self.store is None:
            logger.warning("Abuse strike (no store configured: not counted)", extra=extra)
            return verdict
        try:
            strikes = await self.store.add_strike(ip_hash, request_id, self.clock(), self.window_seconds)
        except Exception as e:
            _log_store_error("add strike", e)
            return verdict
        logger.warning("Abuse strike", extra={**extra, "strikes": strikes})

        if strikes >= self.max_strikes:
            if self.mode != "block":
                logger.warning("Abuse block skipped (log-only)", extra={**extra, "strikes": strikes})
                return verdict
            try:
                await self.store.block(ip_hash, self.block_seconds)
            except Exception as e:
                _log_store_error("block", e)
                return verdict
            logger.warning("Abuse block", extra={**extra, "strikes": strikes, "blocked_seconds": self.block_seconds})
        return verdict


def _log_store_error(operation: str, error: Exception) -> None:
    logger.warning(f"Abuse store unavailable ({operation}), failing open: {str(error)[:200]}",
                   extra={"error_type": type(error).__name__})


def blocked_response(retry_after: int) -> JSONResponse:
    minutes = max(1, -(-retry_after // 60))
    return JSONResponse(
        status_code=403,
        headers={"Retry-After": str(retry_after)},
        content={
            "error": "temporarily_blocked",
            "message": (
                "Acceso bloqueado temporalmente por reiteradas consultas inapropiadas. "
                f"Podrás volver a preguntar en {minutes} min."
            ),
            "retry_after": retry_after,
        },
    )


def create_abuse_guard() -> AbuseGuard:
    store = None
    if settings.redis_rest_url and settings.redis_rest_token:
        store = UpstashRedisStore(settings.redis_rest_url, settings.redis_rest_token)
    elif settings.abuse_mode != "off":
        logger.warning("Abuse store not configured: strikes are only logged, nobody is blocked")
    return AbuseGuard(
        store=store,
        classifier=AbuseClassifier(),
        mode=settings.abuse_mode,
        max_strikes=settings.abuse_max_strikes,
        block_seconds=settings.abuse_block_minutes * 60,
        window_seconds=settings.abuse_strike_window_hours * 3600,
    )
