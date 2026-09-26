"""Feedback persisted with the answer it rates (fake Redis, fake model)."""

import pytest

import api.index as api_module
from conftest import FakeRedis, ScriptedToolModel, ai
from core.agent import create_agent_graph
from core.feedback_store import FeedbackStore


class Clock:
    def __init__(self):
        self.now = 1_000_000.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def redis(clock):
    return FakeRedis(clock)


@pytest.fixture
def store(monkeypatch, redis, clock):
    feedback_store = FeedbackStore(redis, turn_ttl_seconds=3600, retention_seconds=86400, clock=clock)
    monkeypatch.setattr(api_module, "feedback_store", feedback_store)
    return feedback_store


@pytest.fixture
def use_model(monkeypatch):
    def _use(*responses):
        graph = create_agent_graph(model=ScriptedToolModel(responses=list(responses)))
        monkeypatch.setattr(api_module, "_agent_graph", graph)
    return _use


@pytest.fixture(autouse=True)
def reset_rate_limits():
    api_module.limiter.reset()


def _stream_request_id(text: str) -> str:
    import json

    first = next(line for line in text.splitlines() if line.startswith("data: "))
    return json.loads(first[6:])["request_id"]


@pytest.mark.anyio
async def test_feedback_is_saved_with_question_and_answer(client, use_model, store):
    use_model(ai("Trabaja en Fermax."))
    request_id = client.post("/api/chat", json={
        "message": "¿Dónde trabaja?", "page_context": {"path": "/CV/fermax.html"},
    }).json()["request_id"]

    response = client.post("/api/feedback", json={"request_id": request_id, "rating": "down", "comment": "Corta"})
    assert response.status_code == 204

    (record,) = await store.recent()
    assert record["request_id"] == request_id and record["rating"] == "down" and record["comment"] == "Corta"
    assert record["question"] == "¿Dónde trabaja?" and record["answer"] == "Trabaja en Fermax."
    assert record["route"] == "/cv/fermax.html" and record["model"]


@pytest.mark.anyio
async def test_stream_answer_is_kept_for_feedback(client, use_model, store):
    use_model(ai("Hola, soy el asistente."))
    request_id = _stream_request_id(client.post("/api/chat/stream", json={"message": "hola"}).text)

    assert client.post("/api/feedback", json={"request_id": request_id, "rating": "up"}).status_code == 204
    (record,) = await store.recent()
    assert record["answer"] == "Hola, soy el asistente." and record["question"] == "hola"


@pytest.mark.anyio
async def test_feedback_without_kept_turn_is_saved_without_context(store, clock):
    await store.remember_turn("a" * 32, "pregunta", "respuesta", None)
    clock.now += 3600  # the turn expired
    assert await store.save("a" * 32, "up", None)
    assert await store.save("b" * 32, "down", None)

    records = await store.recent()
    assert {r["request_id"] for r in records} == {"a" * 32, "b" * 32}
    assert all(r["question"] is None and r["answer"] is None for r in records)


@pytest.mark.anyio
async def test_recent_is_newest_first_and_drops_expired(store, clock):
    for n in range(3):
        assert await store.save(f"{n:032x}", "up", None)
        clock.now += 10
    assert [r["request_id"] for r in await store.recent(limit=2)] == [f"{2:032x}", f"{1:032x}"]

    clock.now += 86400  # past retention: the next save prunes the index
    await store.save("f" * 32, "down", None)
    assert [r["request_id"] for r in await store.recent()] == ["f" * 32]


@pytest.mark.anyio
async def test_turn_ttl_zero_keeps_no_answers(redis, clock):
    store = FeedbackStore(redis, turn_ttl_seconds=0, retention_seconds=86400, clock=clock)
    await store.remember_turn("a" * 32, "pregunta", "respuesta", None)
    assert redis.values == {}


def test_store_failure_is_fail_open(client, use_model, store, redis):
    redis.fail = True
    use_model(ai("Respuesta."))
    chat = client.post("/api/chat", json={"message": "hola"})
    assert chat.status_code == 200
    assert client.post("/api/feedback", json={"request_id": chat.json()["request_id"], "rating": "up"}).status_code == 204


@pytest.mark.anyio
async def test_without_redis_nothing_is_saved():
    store = FeedbackStore(None, turn_ttl_seconds=3600, retention_seconds=86400)
    await store.remember_turn("a" * 32, "q", "a", None)
    assert await store.save("a" * 32, "up", None) is False
    assert await store.recent() == []
