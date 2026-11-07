from datetime import UTC, datetime

import pytest

import api.index as api_module
from conftest import FakeRedis, ScriptedToolModel, ai
from core.agent import create_agent_graph
from middleware.chat_budget import ChatBudget

NOON = datetime(2026, 11, 8, 12, 30, tzinfo=UTC).timestamp()


class Clock:
    now = NOON

    def __call__(self):
        return self.now


@pytest.fixture(autouse=True)
def reset_rate_limits():
    api_module.limiter.reset()


@pytest.mark.anyio
async def test_ip_over_its_hourly_budget_gets_429_until_the_next_hour():
    clock = Clock()
    budget = ChatBudget(FakeRedis(clock), ip_hourly_limit=2, daily_limit=0, clock=clock)
    assert await budget.check("1.1.1.1") is None
    assert await budget.check("1.1.1.1") is None
    blocked = await budget.check("1.1.1.1")
    assert blocked.status_code == 429 and blocked.headers["Retry-After"] == str(30 * 60)
    assert await budget.check("2.2.2.2") is None  # other IPs are not affected
    clock.now += 3600
    assert await budget.check("1.1.1.1") is None


@pytest.mark.anyio
async def test_daily_ceiling_is_global_and_ignores_requests_over_the_ip_limit():
    clock = Clock()
    budget = ChatBudget(FakeRedis(clock), ip_hourly_limit=1, daily_limit=3, clock=clock)
    assert await budget.check("1.1.1.1") is None
    for _ in range(5):  # rejected per IP: they do not use up the day
        assert (await budget.check("1.1.1.1")).status_code == 429
    assert await budget.check("2.2.2.2") is None
    assert await budget.check("3.3.3.3") is None
    over = await budget.check("4.4.4.4")
    assert over.status_code == 429 and b"daily_budget_exhausted" in over.body


@pytest.mark.anyio
async def test_budget_fails_open_without_or_with_a_broken_store():
    assert await ChatBudget(None, ip_hourly_limit=1, daily_limit=1).check("1.1.1.1") is None
    redis = FakeRedis()
    redis.fail = True
    assert await ChatBudget(redis, ip_hourly_limit=1, daily_limit=1).check("1.1.1.1") is None


def test_chat_endpoints_answer_429_over_budget(client, monkeypatch):
    graph = create_agent_graph(model=ScriptedToolModel(responses=[ai("ok"), ai("ok")]))
    monkeypatch.setattr(api_module, "_agent_graph", graph)
    monkeypatch.setattr(api_module, "chat_budget", ChatBudget(FakeRedis(Clock()), ip_hourly_limit=1, daily_limit=0, clock=Clock()))
    assert client.post("/api/chat", json={"message": "hola"}).status_code == 200
    assert client.post("/api/chat", json={"message": "hola"}).status_code == 429
    response = client.post("/api/chat/stream", json={"message": "hola"})
    assert response.status_code == 429 and response.json()["error"] == "rate_limit_exceeded"


def test_rate_limit_is_keyed_by_the_real_client_ip_on_vercel(client, monkeypatch):
    graph = create_agent_graph(model=ScriptedToolModel(responses=[ai("ok") for _ in range(20)]))
    monkeypatch.setattr(api_module, "_agent_graph", graph)
    monkeypatch.setenv("VERCEL", "1")
    first = {"x-forwarded-for": "203.0.113.1"}
    codes = [client.post("/api/chat", json={"message": "hola"}, headers=first).status_code for _ in range(6)]
    assert codes[-1] == 429
    # Another visitor behind the same runtime address keeps its own limit.
    other = client.post("/api/chat", json={"message": "hola"}, headers={"x-forwarded-for": "203.0.113.2"})
    assert other.status_code == 200
