"""
Usage metrics of the site for its owner: web visits (GoatCounter API), questions to
the assistant and connections to the MCP server (own counters in Upstash Redis).

They are read per month with `GET /api/stats` (Authorization: Bearer STATS_KEY) or
with the private MCP tool `usage_stats` (core/mcp_server.py, same key), which only
exists because the job-search dashboard reads live data through connectors. Only aggregated counters are
kept: no IP, no question text, no session. The MCP client name is whatever the
client declares (clientInfo.name), so the owner's own use (claude.ai, the dashboard)
counts too.

Keys (prefix cvbot:stats), one hash per UTC month kept RETENTION_DAYS:
    cvbot:stats:<YYYY-MM>  questions, conversations, mcp_connections, mcp_calls, client:<name>

Everything is fail-open: without Redis nothing is counted and the Redis columns come
back as null; without GOATCOUNTER_API_TOKEN, web visits are null. Nothing here ever
breaks a chat or an MCP request.

Print the last months (needs the Redis / GoatCounter variables in .env):
    uv run python -m core.usage_stats [--months 6]
"""

import asyncio
import hmac
import json
import logging
import re
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from core.config import settings
from core.redis_rest import UpstashRedis, create_redis

logger = logging.getLogger("cv_chatbot.usage")

KEY_PREFIX = "cvbot:stats"
RETENTION_DAYS = 400  # a year back plus the current month
MAX_MONTHS = 12
# First month with assistant and MCP counters: earlier months are null, not 0.
COUNTING_SINCE = "2026-11"
STATS_TOOL = "usage_stats"
UNKNOWN_CLIENT = "desconocido"
TOP_CLIENTS = 6
# MCP methods that open a connection (legacy handshake / 2026-07-28 discovery) or query the CV.
CONNECTION_METHODS = {"initialize", "server/discover"}
QUERY_METHODS = {"tools/call", "resources/read", "prompts/get"}
CLIENT_INFO_META_KEY = "io.modelcontextprotocol/clientInfo"  # 2026-07-28 request envelope
MAX_BODY_TO_PARSE = 64 * 1024
_CLIENT_CHARS = re.compile(r"[^a-z0-9._ -]+")


def month_of(ts: float) -> str:
    return datetime.fromtimestamp(ts, UTC).strftime("%Y-%m")


def last_months(ts: float, count: int) -> list[str]:
    """The `count` UTC months up to the one containing `ts`, oldest first."""
    year, month = (int(x) for x in month_of(ts).split("-"))
    months = []
    for _ in range(count):
        months.append(f"{year:04d}-{month:02d}")
        year, month = (year, month - 1) if month > 1 else (year - 1, 12)
    return months[::-1]


def client_label(name: object) -> str:
    """Normalised, bounded client name: a client cannot create arbitrary hash fields."""
    if not isinstance(name, str):
        return UNKNOWN_CLIENT
    return _CLIENT_CHARS.sub("", name.strip().lower())[:40].strip() or UNKNOWN_CLIENT


def mcp_events(body: bytes) -> list[tuple[str, str | None, str | None]]:
    """(method, declared client name, tool name) of each JSON-RPC request in an MCP POST body."""
    if not body or len(body) > MAX_BODY_TO_PARSE:
        return []
    try:
        payload = json.loads(body)
    except ValueError:
        return []
    events = []
    for item in (payload if isinstance(payload, list) else [payload])[:10]:
        if not isinstance(item, dict) or not isinstance(item.get("method"), str):
            continue
        params = item.get("params") if isinstance(item.get("params"), dict) else {}
        meta = params.get("_meta") if isinstance(params.get("_meta"), dict) else {}
        info = params.get("clientInfo") or meta.get(CLIENT_INFO_META_KEY)
        client = info.get("name") if isinstance(info, dict) else None
        tool = params.get("name") if item["method"] == "tools/call" else None
        events.append((item["method"], client, tool if isinstance(tool, str) else None))
    return events


def _next_month(start: datetime) -> datetime:
    return start.replace(year=start.year + 1, month=1) if start.month == 12 else start.replace(month=start.month + 1)


class GoatCounter:
    """Monthly totals from the GoatCounter API (https://www.goatcounter.com/help/api)."""

    def __init__(self, site_url: str, token: str, timeout: float = 3.0, transport=None):
        self._url = site_url.rstrip("/") + "/api/v0/stats/total"
        self._headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        self._timeout = timeout
        self._transport = transport  # tests inject httpx.MockTransport

    async def monthly_visits(self, months: list[str], now: float) -> dict[str, int | None]:
        """Pageviews per month; a month that cannot be read is None (and so are the later ones)."""
        import httpx

        visits: dict[str, int | None] = dict.fromkeys(months)
        # The API wants hour-rounded bounds: the current month ends at the next full hour.
        next_hour = datetime.fromtimestamp(now, UTC).replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            for month in months:  # one by one: the API allows 4 requests per second
                start = datetime.strptime(month + "-01", "%Y-%m-%d").replace(tzinfo=UTC)
                end = min(_next_month(start), next_hour)
                try:
                    response = await client.get(self._url, headers=self._headers, params={
                        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"), "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    })
                    response.raise_for_status()
                    visits[month] = int(response.json()["total"])
                except Exception as e:
                    logger.warning(f"GoatCounter unavailable: {str(e)[:200]}", extra={"error_type": type(e).__name__})
                    break
        return visits


class UsageStats:
    def __init__(
        self,
        redis: UpstashRedis | None,
        *,
        goatcounter: GoatCounter | None = None,
        clock: Callable[[], float] = time.time,
    ):
        self.redis = redis
        self.goatcounter = goatcounter
        self.clock = clock

    async def _increment(self, fields: list[str]) -> None:
        if self.redis is None or not fields:
            return
        key = f"{KEY_PREFIX}:{month_of(self.clock())}"
        try:
            await self.redis.pipeline(*[["HINCRBY", key, field, 1] for field in fields],
                                      ["EXPIRE", key, RETENTION_DAYS * 86400])
        except Exception as e:
            logger.warning(f"Usage stats unavailable (count): {str(e)[:200]}", extra={"error_type": type(e).__name__})

    async def record_question(self, new_conversation: bool) -> None:
        """One answered question; a question without history opens a conversation. Never raises."""
        await self._increment(["questions", "conversations"] if new_conversation else ["questions"])

    async def record_mcp(self, events: list[tuple[str, str | None, str | None]]) -> None:
        """Connections (per declared client) and queries; reading these stats does not count. Never raises."""
        fields = []
        for method, client, tool in events:
            if method in CONNECTION_METHODS:
                fields += ["mcp_connections", f"client:{client_label(client)}"]
            elif method in QUERY_METHODS and tool != STATS_TOOL:
                fields.append("mcp_calls")
        await self._increment(fields)

    async def _counters(self, months: list[str]) -> dict[str, dict[str, int]]:
        if self.redis is None:
            return {}
        try:
            results = await self.redis.pipeline(*[["HGETALL", f"{KEY_PREFIX}:{m}"] for m in months])
        except Exception as e:
            logger.warning(f"Usage stats unavailable (read): {str(e)[:200]}", extra={"error_type": type(e).__name__})
            return {}
        counters = {}
        for month, flat in zip(months, results):
            flat = flat or []  # Upstash REST returns HGETALL as [field, value, field, value...]
            counters[month] = {flat[i]: int(flat[i + 1]) for i in range(0, len(flat) - 1, 2)}
        return counters

    async def monthly(self, months: int = 6) -> list[dict]:
        """One row per month, oldest first. null = no data (store not configured or month not counted)."""
        labels = last_months(self.clock(), max(1, min(int(months), MAX_MONTHS)))
        counters = await self._counters(labels)
        visits = await self.goatcounter.monthly_visits(labels, self.clock()) if self.goatcounter else {}
        rows = []
        for month in labels:
            counted = counters.get(month) if month >= COUNTING_SINCE else None

            def value(field: str) -> int | None:
                return None if counted is None else counted.get(field, 0)

            rows.append({
                "mes": month,
                "visitas_web": visits.get(month),
                "preguntas_asistente": value("questions"),
                "conversaciones_asistente": value("conversations"),
                "conexiones_mcp": value("mcp_connections"),
                "consultas_mcp": value("mcp_calls"),
                "clientes_mcp": _clients(counted),
            })
        return rows


def _clients(counted: dict[str, int] | None) -> str | None:
    """'claude-ai 5 · cursor 2': connections per declared client, most frequent first."""
    if counted is None:
        return None
    clients = sorted(((k[7:], v) for k, v in counted.items() if k.startswith("client:")), key=lambda kv: (-kv[1], kv[0]))
    return " · ".join(f"{name} {count}" for name, count in clients[:TOP_CLIENTS])


def stats_key_matches(candidate: object) -> bool:
    """Constant-time check against STATS_KEY; always False while it is unset."""
    expected = settings.stats_key
    return bool(expected) and isinstance(candidate, str) and hmac.compare_digest(candidate.encode(), expected.encode())


def create_usage_stats() -> UsageStats:
    goatcounter = (
        GoatCounter(settings.goatcounter_url, settings.goatcounter_api_token)
        if settings.goatcounter_api_token else None
    )
    return UsageStats(create_redis(), goatcounter=goatcounter)


# Shared by the API (questions), the MCP wrapper below (connections) and the usage_stats tool.
site_stats = create_usage_stats()


class McpUsageCounter:
    """
    ASGI wrapper for the MCP app: counts connections and queries per month without
    touching the protocol. It reads a copy of each POST body, replays it to the MCP
    app and finishes counting before the response ends (Vercel may freeze the
    instance once it is sent).
    """

    def __init__(self, app, stats: UsageStats | None = None):
        self.app = app
        self.stats = stats  # None = the shared site_stats (looked up per request, so tests can swap it)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method") != "POST":
            await self.app(scope, receive, send)
            return

        messages, body = [], b""
        while True:
            message = await receive()
            messages.append(message)
            if message["type"] != "http.request":
                break
            if len(body) <= MAX_BODY_TO_PARSE:
                body += message.get("body", b"")
            if not message.get("more_body", False):
                break

        stats = self.stats or site_stats
        counting = asyncio.create_task(stats.record_mcp(mcp_events(body)))

        async def replay():
            return messages.pop(0) if messages else await receive()

        async def send_after_counting(message):
            if message["type"] == "http.response.body" and not message.get("more_body", False):
                await counting
            await send(message)

        try:
            await self.app(scope, replay, send_after_counting)
        finally:
            if not counting.done():
                await counting


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Usage per month, oldest first (JSON lines).")
    parser.add_argument("--months", type=int, default=6)
    args = parser.parse_args()
    for row in asyncio.run(site_stats.monthly(args.months)):
        print(json.dumps(row, ensure_ascii=False))
