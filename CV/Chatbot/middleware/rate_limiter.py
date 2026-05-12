"""
Rate limiting middleware using slowapi.

Uses in-memory storage — sufficient for 2-3 concurrent users on Vercel.
For production with higher traffic, upgrade to Upstash Redis backend.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.config import settings


# Create the limiter instance with IP-based key function
limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Demasiadas peticiones. Por favor, espera antes de intentarlo de nuevo.",
            "detail": str(exc.detail),
        },
    )


def get_rate_limit_string() -> str:
    """Build the rate limit string from config."""
    return f"{settings.rate_limit_per_minute}/minute;{settings.rate_limit_per_hour}/hour"
