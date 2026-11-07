"""
Request budget of the chat shared by every Vercel instance (Upstash Redis).

The slowapi limits (middleware/rate_limiter.py) live in each instance's memory:
Vercel runs several instances and recycles them, so they only stop bursts. This
budget is shared:

- per IP (keyed HMAC, never the IP): RATE_LIMIT_PER_HOUR questions per clock hour;
- global: CHAT_DAILY_LIMIT questions per UTC day, a ceiling on what the model can
  cost in a day however many IPs are used. 0 = no global ceiling.

Only requests that pass the per-IP check count toward the global ceiling, so one
client over its limit cannot use up everybody's budget. Fail-open like the rest
of the Redis features: without a store, or if it fails, nothing is limited here.

Keys (prefix cvbot:budget):
    ip:<ip_hash>:<YYYYMMDDHH>  INCR, TTL 1 h
    day:<YYYY-MM-DD>           INCR, TTL 2 days
"""

import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime

from starlette.responses import JSONResponse

from core.config import settings
from core.redis_rest import UpstashRedis, create_redis
from middleware.request_logger import hash_ip

logger = logging.getLogger("cv_chatbot.budget")

KEY_PREFIX = "cvbot:budget"


class ChatBudget:
    def __init__(
        self,
        redis: UpstashRedis | None,
        *,
        ip_hourly_limit: int,
        daily_limit: int,
        clock: Callable[[], float] = time.time,
    ):
        self.redis = redis
        self.ip_hourly_limit = ip_hourly_limit
        self.daily_limit = daily_limit
        self.clock = clock

    async def _hit(self, key: str, ttl: int) -> int:
        count, _ = await self.redis.pipeline(["INCR", key], ["EXPIRE", key, ttl])
        return int(count)

    async def check(self, ip: str, request_id: str | None = None) -> JSONResponse | None:
        """A 429 response when the IP or the day is over budget, else None (counted). Never raises."""
        if self.redis is None:
            return None
        now = self.clock()
        stamp = datetime.fromtimestamp(now, UTC)
        try:
            if self.ip_hourly_limit > 0:
                ip_hash = hash_ip(ip)
                count = await self._hit(f"{KEY_PREFIX}:ip:{ip_hash}:{stamp:%Y%m%d%H}", 3600)
                if count > self.ip_hourly_limit:
                    logger.warning("Hourly chat budget exceeded", extra={"request_id": request_id, "ip_hash": ip_hash})
                    return _too_many("rate_limit_exceeded", 3600 - int(now % 3600),
                                     "Has alcanzado el límite de preguntas por hora. Vuelve a intentarlo en un rato.")
            if self.daily_limit > 0:
                count = await self._hit(f"{KEY_PREFIX}:day:{stamp:%Y-%m-%d}", 2 * 86400)
                if count > self.daily_limit:
                    logger.warning("Daily chat budget exhausted", extra={"request_id": request_id})
                    return _too_many("daily_budget_exhausted", 86400 - int(now % 86400),
                                     "El asistente ha alcanzado su límite de preguntas de hoy. Vuelve a intentarlo mañana.")
        except Exception as e:
            logger.warning(f"Chat budget unavailable, failing open: {str(e)[:200]}",
                           extra={"request_id": request_id, "error_type": type(e).__name__})
        return None


def _too_many(error: str, retry_after: int, message: str) -> JSONResponse:
    retry_after = max(1, retry_after)
    return JSONResponse(
        status_code=429,
        headers={"Retry-After": str(retry_after)},
        content={"error": error, "message": message, "retry_after": retry_after},
    )


def create_chat_budget() -> ChatBudget:
    return ChatBudget(
        create_redis(),
        ip_hourly_limit=settings.rate_limit_per_hour,
        daily_limit=settings.chat_daily_limit,
    )
