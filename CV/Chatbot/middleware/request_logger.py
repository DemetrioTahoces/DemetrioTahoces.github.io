"""
Structured JSON logging compatible with Vercel Function Logs.

Privacy: user messages are never logged (only their length) and client IPs
are logged as a keyed HMAC, not a plain hash, so they cannot be brute-forced.
"""

import hashlib
import hmac
import json
import logging
from typing import Any

from core.config import settings

_EXTRA_FIELDS = (
    "request_id", "ip_hash", "endpoint", "status_code", "duration_ms",
    "message_chars", "history_messages", "page_route",
    "input_tokens", "cached_tokens", "output_tokens", "reasoning_tokens", "total_tokens",
    "error_type", "rating", "has_comment",
    "abuse_category", "abuse_mode", "strikes", "blocked_seconds",
)


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in _EXTRA_FIELDS:
            if hasattr(record, key):
                entry[key] = getattr(record, key)
        return json.dumps(entry, ensure_ascii=False)


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("cv_chatbot")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    # Avoid duplicate handlers on warm instances
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
    return logger


def hash_ip(ip: str) -> str:
    key = (settings.api_key or "cv-chatbot").encode()
    return hmac.new(key, ip.encode(), hashlib.sha256).hexdigest()[:12]


def log_request(logger: logging.Logger, *, request_id: str, ip: str, endpoint: str,
                message_chars: int, history_messages: int, page_route: str | None) -> None:
    logger.info("Request received", extra={
        "request_id": request_id,
        "ip_hash": hash_ip(ip),
        "endpoint": endpoint,
        "message_chars": message_chars,
        "history_messages": history_messages,
        "page_route": page_route,
    })


def log_response(logger: logging.Logger, *, request_id: str, status_code: int,
                 duration_ms: float, usage: dict[str, Any] | None = None) -> None:
    extra: dict[str, Any] = {
        "request_id": request_id,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    for key in ("input_tokens", "cached_tokens", "output_tokens", "reasoning_tokens", "total_tokens"):
        if usage and key in usage:
            extra[key] = usage[key]
    logger.info("Response sent", extra=extra)


def log_error(logger: logging.Logger, *, request_id: str, error: Exception, duration_ms: float) -> None:
    logger.error(
        f"Request failed: {str(error)[:200]}",
        extra={
            "request_id": request_id,
            "status_code": 500,
            "duration_ms": round(duration_ms, 2),
            "error_type": type(error).__name__,
        },
    )
