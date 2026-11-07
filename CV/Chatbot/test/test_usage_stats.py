"""Usage counters (fake Redis), GoatCounter visits (mocked HTTP) and the private usage_stats MCP tool."""

import asyncio
import json
from datetime import UTC, datetime

import httpx
import pytest

import api.index as api_module
from conftest import FakeRedis, ScriptedToolModel, ai
from core.agent import create_agent_graph
from core.config import settings
from core.usage_stats import GoatCounter, UsageStats, client_label, last_months, mcp_events

NOW = datetime(2026, 11, 7, 15, 30, tzinfo=UTC).timestamp()
KEY = "cvbot:stats:2026-11"
MCP_HEADERS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}


def clock():
    return NOW


@pytest.fixture
def redis():
    return FakeRedis(clock)


@pytest.fixture
def stats(monkeypatch, redis, offline_usage_stats):
    monkeypatch.setattr(offline_usage_stats, "redis", redis)
    monkeypatch.setattr(offline_usage_stats, "clock", clock)
    return offline_usage_stats


@pytest.fixture(autouse=True)
def reset_rate_limits():
    api_module.limiter.reset()
    api_module.mcp_app.reset()


@pytest.fixture
def use_model(monkeypatch):
    def _use(*responses):
        graph = create_agent_graph(model=ScriptedToolModel(responses=list(responses)))
        monkeypatch.setattr(api_module, "_agent_graph", graph)
    return _use


def _modern(client, method, params, client_name=None, name=None):
    meta = {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientCapabilities": {}}
    if client_name:
        meta["io.modelcontextprotocol/clientInfo"] = {"name": client_name, "version": "1"}
    headers = {**MCP_HEADERS, "MCP-Protocol-Version": "2026-07-28", "Mcp-Method": method}
    if name:
        headers["Mcp-Name"] = name
    response = client.post("/api/mcp", headers=headers,
                           json={"jsonrpc": "2.0", "id": 1, "method": method, "params": {"_meta": meta, **params}})
    assert response.status_code == 200, response.text
    return response.json()


def _stats_call(client, arguments):
    return _modern(client, "tools/call", {"name": "usage_stats", "arguments": arguments}, name="usage_stats")["result"]


def test_last_months_cross_the_year():
    assert last_months(datetime(2027, 2, 1, tzinfo=UTC).timestamp(), 4) == ["2026-11", "2026-12", "2027-01", "2027-02"]


def test_client_names_are_normalised_and_bounded():
    assert client_label("Claude-AI") == "claude-ai"
    assert len(client_label("x<script>" * 20)) <= 40 and "<" not in client_label("x<script>")
    assert client_label(None) == client_label("  ") == "desconocido"


def test_mcp_events_read_legacy_and_modern_client_info():
    legacy = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"clientInfo": {"name": "Cursor"}}}
    modern = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
        "name": "search", "_meta": {"io.modelcontextprotocol/clientInfo": {"name": "claude-ai"}}}}
    assert mcp_events(json.dumps([legacy, modern]).encode()) == [
        ("initialize", "Cursor", None), ("tools/call", "claude-ai", "search")]
    assert mcp_events(b"no es json") == [] and mcp_events(b"") == []


def test_questions_and_conversations_are_counted_per_month(client, use_model, stats, redis):
    use_model(ai("Uno."), ai("Dos."))
    assert client.post("/api/chat", json={"message": "hola"}).status_code == 200
    history = [{"role": "user", "content": "hola"}, {"role": "assistant", "content": "Uno."}]
    assert client.post("/api/chat/stream", json={"message": "¿y?", "history": history}).status_code == 200
    assert redis.hashes[KEY] == {"questions": 2, "conversations": 1}
    assert redis.ttls[KEY] > 365 * 86400


def test_mcp_connections_and_queries_are_counted_per_client(client, stats, redis):
    init = client.post("/api/mcp", headers=MCP_HEADERS, json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "Cursor", "version": "1"}}})
    assert init.status_code == 200
    _modern(client, "server/discover", {}, client_name="claude-ai")
    _modern(client, "tools/call", {"name": "search", "arguments": {"query": "Kafka"}}, client_name="claude-ai", name="search")
    _stats_call(client, {"key": "x"})  # reading the stats is not a query to the CV
    assert redis.hashes[KEY] == {"mcp_connections": 2, "client:cursor": 1, "client:claude-ai": 1, "mcp_calls": 1}


def test_usage_stats_tool_is_private(client, stats, redis, monkeypatch):
    assert _stats_call(client, {"key": ""})["isError"]  # no STATS_KEY configured: always refused
    monkeypatch.setattr(settings, "stats_key", "una-clave-larga-de-prueba")
    refused = _stats_call(client, {"key": "otra"})
    assert refused["isError"] and "privada" in refused["content"][0]["text"]

    redis.hashes[KEY] = {"questions": 7, "conversations": 3, "mcp_connections": 4, "mcp_calls": 9,
                         "client:claude-ai": 3, "client:cursor": 1}
    rows = _stats_call(client, {"key": "una-clave-larga-de-prueba", "months": 2})["structuredContent"]["result"]
    assert [r["mes"] for r in rows] == ["2026-10", "2026-11"]
    assert rows[0]["preguntas_asistente"] is None  # before the counters existed: null, not 0
    assert rows[1] == {"mes": "2026-11", "visitas_web": None, "preguntas_asistente": 7, "conversaciones_asistente": 3,
                       "conexiones_mcp": 4, "consultas_mcp": 9, "clientes_mcp": "claude-ai 3 · cursor 1"}


def test_counters_are_fail_open(redis):
    redis.fail = True
    stats = UsageStats(redis, clock=clock)
    asyncio.run(stats.record_question(True))
    asyncio.run(stats.record_mcp([("initialize", "x", None)]))
    (row,) = asyncio.run(stats.monthly(1))
    assert row["mes"] == "2026-11" and all(row[k] is None for k in row if k != "mes")
    assert asyncio.run(UsageStats(None, clock=clock).monthly(1))[0]["consultas_mcp"] is None


def test_goatcounter_visits_per_month():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"total": 120 if request.url.params["start"].startswith("2026-10") else 30})

    goatcounter = GoatCounter("https://demo.goatcounter.com", "tok", transport=httpx.MockTransport(handler))
    assert asyncio.run(goatcounter.monthly_visits(["2026-10", "2026-11"], NOW)) == {"2026-10": 120, "2026-11": 30}
    assert seen[0].headers["Authorization"] == "Bearer tok"
    assert seen[0].url.path == "/api/v0/stats/total"
    assert (seen[0].url.params["start"], seen[0].url.params["end"]) == ("2026-10-01T00:00:00Z", "2026-11-01T00:00:00Z")
    assert seen[1].url.params["end"] == "2026-11-07T16:00:00Z"  # current month: up to the next full hour


def test_goatcounter_errors_leave_visits_null():
    goatcounter = GoatCounter("https://demo.goatcounter.com", "tok", transport=httpx.MockTransport(lambda r: httpx.Response(403)))
    assert asyncio.run(goatcounter.monthly_visits(["2026-10", "2026-11"], NOW)) == {"2026-10": None, "2026-11": None}
