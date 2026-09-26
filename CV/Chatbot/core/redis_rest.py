"""
Minimal Upstash Redis REST client shared by the abuse guard and the feedback store.

A single HTTP call per pipeline and no connection pool, which suits serverless.
Callers decide how to fail: both current users are fail-open.
"""

from core.config import settings


class UpstashRedis:
    def __init__(self, url: str, token: str, timeout: float = 2.0, transport=None):
        self._url = url.rstrip("/") + "/pipeline"
        self._headers = {"Authorization": f"Bearer {token}"}
        self._timeout = timeout
        self._transport = transport  # tests inject httpx.MockTransport

    async def pipeline(self, *commands: list) -> list:
        import httpx

        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(self._url, headers=self._headers, json=list(commands))
        response.raise_for_status()
        results = response.json()
        errors = [r["error"] for r in results if r.get("error")]
        if errors:
            raise RuntimeError(f"Redis error: {errors[0]}")
        return [r.get("result") for r in results]


def create_redis() -> UpstashRedis | None:
    """The configured store, or None when UPSTASH_REDIS_REST_* / KV_REST_API_* are unset."""
    if settings.redis_rest_url and settings.redis_rest_token:
        return UpstashRedis(settings.redis_rest_url, settings.redis_rest_token)
    return None
