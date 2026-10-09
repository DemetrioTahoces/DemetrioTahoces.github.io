"""
Rate limiting middleware using slowapi.

Uses in-memory storage — sufficient for 2-3 concurrent users on Vercel.
For production with higher traffic, upgrade to Upstash Redis backend.
"""

from limits import parse_many
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.config import settings
from middleware.abuse_guard import client_ip


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


def get_mcp_rate_limit_string() -> str:
    return f"{settings.mcp_rate_limit_per_minute}/minute;{settings.mcp_rate_limit_per_hour}/hour"


class MountedAppRateLimit:
    """
    Per-IP rate limit for an ASGI app mounted outside the FastAPI routes (the MCP
    server), which slowapi's per-route decorators do not reach. Only POST counts:
    that is every MCP request. In memory and per instance, like the API limits.
    """

    def __init__(self, app, limit_string: str, scope_name: str):
        self.app = app
        self.items = parse_many(limit_string)
        self.scope_name = scope_name
        self.storage = MemoryStorage()
        self.limiter = FixedWindowRateLimiter(self.storage)

    def reset(self) -> None:
        self.storage.reset()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("method") == "POST":
            key = client_ip(Request(scope))
            if not all(self.limiter.hit(item, self.scope_name, key) for item in self.items):
                response = JSONResponse(
                    status_code=429,
                    headers={"Retry-After": "60"},
                    content={"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": "Rate limit exceeded"}},
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)
