"""
Structured request/response logging middleware.

Logs each request with timing, token usage, and status in JSON format
compatible with Vercel Function Logs.
"""

import hashlib
import json
import logging
import time
from typing import Any

from core.config import settings


def setup_logging() -> logging.Logger:
    """Configure structured JSON logging for the application."""
    logger = logging.getLogger("cv_chatbot")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Avoid duplicate handlers on warm Vercel instances
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

    return logger


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging output."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach extra fields if present
        for key in ("request_id", "ip_hash", "endpoint", "method",
                     "status_code", "duration_ms", "session_id",
                     "input_tokens", "output_tokens", "total_tokens",
                     "error_type", "user_message_preview"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        return json.dumps(log_entry, ensure_ascii=False)


def hash_ip(ip: str) -> str:
    """Hash an IP address for privacy-preserving logging."""
    return hashlib.sha256(ip.encode()).hexdigest()[:12]


def log_request(
    logger: logging.Logger,
    *,
    request_id: str,
    ip: str,
    endpoint: str,
    method: str,
    session_id: str,
    user_message: str,
) -> None:
    """Log an incoming request."""
    logger.info(
        "Request received",
        extra={
            "request_id": request_id,
            "ip_hash": hash_ip(ip),
            "endpoint": endpoint,
            "method": method,
            "session_id": session_id,
            "user_message_preview": user_message[:80] + ("..." if len(user_message) > 80 else ""),
        },
    )


def log_response(
    logger: logging.Logger,
    *,
    request_id: str,
    status_code: int,
    duration_ms: float,
    usage: dict[str, Any] | None = None,
) -> None:
    """Log a completed response with timing and token usage."""
    extra: dict[str, Any] = {
        "request_id": request_id,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }

    if usage:
        extra["input_tokens"] = usage.get("input_tokens", 0)
        extra["output_tokens"] = usage.get("output_tokens", 0)
        extra["total_tokens"] = usage.get("total_tokens", 0)

    logger.info("Response sent", extra=extra)


def log_error(
    logger: logging.Logger,
    *,
    request_id: str,
    error: Exception,
    duration_ms: float,
) -> None:
    """Log an error during request processing."""
    logger.error(
        f"Request failed: {str(error)[:200]}",
        extra={
            "request_id": request_id,
            "status_code": 500,
            "duration_ms": round(duration_ms, 2),
            "error_type": type(error).__name__,
        },
    )
