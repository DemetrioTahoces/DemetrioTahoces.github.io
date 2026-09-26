"""
Thumbs up/down feedback persisted in Upstash Redis, with the answer it rates.

The backend is stateless, so the rated answer is not known when feedback
arrives. Each chat turn is therefore kept for FEEDBACK_TURN_TTL_HOURS under its
request_id; a later feedback copies it into a record kept for
FEEDBACK_RETENTION_DAYS. Nothing identifies the user (no IP, no session).

Keys (prefix cvbot:feedback):
    turn:<request_id>  JSON {question, answer, route, model, ts}      TTL turn
    item:<request_id>  JSON turn + {request_id, rating, comment, ts}  TTL retention
    index              sorted set request_id -> feedback timestamp

Every operation is fail-open: a store error is logged and never breaks a chat
or the feedback endpoint. Without a store configured nothing is kept.

Read the latest feedback (needs UPSTASH_REDIS_REST_* or KV_REST_API_* in .env):
    uv run python -m core.feedback_store [--limit 20]
"""

import json
import logging
import time
from collections.abc import Callable

from core.config import settings
from core.redis_rest import UpstashRedis, create_redis

logger = logging.getLogger("cv_chatbot.feedback")

KEY_PREFIX = "cvbot:feedback"
INDEX_KEY = f"{KEY_PREFIX}:index"


def _turn_key(request_id: str) -> str:
    return f"{KEY_PREFIX}:turn:{request_id}"


def _item_key(request_id: str) -> str:
    return f"{KEY_PREFIX}:item:{request_id}"


class FeedbackStore:
    def __init__(
        self,
        redis: UpstashRedis | None,
        *,
        turn_ttl_seconds: int,
        retention_seconds: int,
        clock: Callable[[], float] = time.time,
    ):
        self.redis = redis
        self.turn_ttl_seconds = turn_ttl_seconds
        self.retention_seconds = retention_seconds
        self.clock = clock

    async def remember_turn(self, request_id: str, question: str, answer: str, route: str | None) -> None:
        """Keep the turn so a later feedback can be saved with it. Never raises."""
        if self.redis is None or self.turn_ttl_seconds <= 0:
            return
        turn = {"question": question, "answer": answer, "route": route, "model": settings.model_name, "ts": self.clock()}
        try:
            await self.redis.pipeline(
                ["SET", _turn_key(request_id), json.dumps(turn, ensure_ascii=False), "EX", self.turn_ttl_seconds]
            )
        except Exception as e:
            _log_store_error("remember turn", e, request_id)

    async def save(self, request_id: str, rating: str, comment: str | None) -> bool:
        """Persist the feedback with its turn (if still kept). Never raises."""
        if self.redis is None:
            return False
        now = self.clock()
        try:
            (raw_turn,) = await self.redis.pipeline(["GET", _turn_key(request_id)])
            turn = json.loads(raw_turn) if raw_turn else {}
            item = {
                "request_id": request_id,
                "rating": rating,
                "comment": comment,
                "ts": now,
                "question": turn.get("question"),
                "answer": turn.get("answer"),
                "route": turn.get("route"),
                "model": turn.get("model"),
                "answered_at": turn.get("ts"),
            }
            await self.redis.pipeline(
                ["SET", _item_key(request_id), json.dumps(item, ensure_ascii=False), "EX", self.retention_seconds],
                ["ZADD", INDEX_KEY, now, request_id],
                ["ZREMRANGEBYSCORE", INDEX_KEY, "-inf", now - self.retention_seconds],
            )
        except Exception as e:
            _log_store_error("save", e, request_id)
            return False
        return True

    async def recent(self, limit: int = 20) -> list[dict]:
        """Latest feedback first. Raises on store errors (only used offline)."""
        if self.redis is None:
            return []
        (ids,) = await self.redis.pipeline(["ZREVRANGE", INDEX_KEY, 0, limit - 1])
        if not ids:
            return []
        (raw_items,) = await self.redis.pipeline(["MGET", *[_item_key(i) for i in ids]])
        return [json.loads(raw) for raw in raw_items if raw]


def _log_store_error(operation: str, error: Exception, request_id: str) -> None:
    logger.warning(
        f"Feedback store unavailable ({operation}): {str(error)[:200]}",
        extra={"request_id": request_id, "error_type": type(error).__name__},
    )


def create_feedback_store() -> FeedbackStore:
    redis = create_redis()
    if redis is None:
        logger.warning("Feedback store not configured: feedback is only logged")
    return FeedbackStore(
        redis,
        turn_ttl_seconds=settings.feedback_turn_ttl_hours * 3600,
        retention_seconds=settings.feedback_retention_days * 86400,
    )


if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Latest chatbot feedback, newest first (JSON lines).")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    store = create_feedback_store()
    if store.redis is None:
        raise SystemExit("Redis not configured (UPSTASH_REDIS_REST_* or KV_REST_API_*).")
    for record in asyncio.run(store.recent(args.limit)):
        print(json.dumps(record, ensure_ascii=False))
