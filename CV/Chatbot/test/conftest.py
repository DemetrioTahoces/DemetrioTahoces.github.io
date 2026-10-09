"""
Shared fixtures. Unit tests never call the real model: they use a scripted fake
chat model, so they run offline and without API_KEY.
"""

import sys
from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

USAGE = {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110}


class ScriptedToolModel(FakeMessagesListChatModel):
    """Fake chat model that returns scripted messages and accepts bind_tools()."""

    def bind_tools(self, tools, **kwargs):
        return self


def ai(content: str = "", tool_calls: list[dict] | None = None) -> AIMessage:
    return AIMessage(content=content, tool_calls=tool_calls or [], usage_metadata=dict(USAGE))


def read_call(article: str, call_id: str = "call_1") -> dict:
    return {"name": "read_blog_article", "args": {"article": article}, "id": call_id, "type": "tool_call"}


@pytest.fixture
def blog_tool_mode(monkeypatch):
    """Blog too big for the context: only its index is sent and articles are read with the tool."""
    from core.config import settings

    monkeypatch.setattr(settings, "blog_in_prompt_max_chars", 0)


@pytest.fixture
def scripted_graph():
    """Build an agent graph whose model replies with the given messages, in order."""
    from core.agent import create_agent_graph

    def _build(*responses: AIMessage):
        return create_agent_graph(model=ScriptedToolModel(responses=list(responses)))

    return _build


@pytest.fixture(scope="session")
def client():
    # One lifespan per process: the MCP session manager can only run once.
    from fastapi.testclient import TestClient

    import api.index as api_module

    with TestClient(api_module.app) as test_client:
        yield test_client


@pytest.fixture
def anyio_backend():
    return "asyncio"


class FakeAbuseStore:
    """In-memory AbuseStore with an injectable clock (the real one is Upstash Redis)."""

    def __init__(self, clock):
        self.clock = clock
        self.strikes: dict[str, list[float]] = {}
        self.blocked_until: dict[str, float] = {}

    async def block_ttl(self, key):
        return int(self.blocked_until.get(key, 0) - self.clock())

    async def add_strike(self, key, member, now, window_seconds):
        recent = [t for t in self.strikes.get(key, []) if t > now - window_seconds]
        self.strikes[key] = recent + [now]
        return len(self.strikes[key])

    async def block(self, key, seconds):
        self.blocked_until[key] = self.clock() + seconds
        self.strikes.pop(key, None)


def keyword_classifier(*malicious_markers: str):
    """Fake classifier: prompt_injection if the message contains any marker."""
    from core.abuse_classifier import AbuseVerdict

    async def classify(message: str) -> AbuseVerdict:
        hit = any(marker in message.lower() for marker in malicious_markers)
        return AbuseVerdict(category="prompt_injection" if hit else "none")

    return classify


@pytest.fixture(autouse=True)
def offline_abuse_guard(monkeypatch):
    """Tests never reach the real classifier or store, even with API_KEY in .env."""
    import api.index as api_module
    from middleware.abuse_guard import AbuseGuard

    guard = AbuseGuard(store=None, classifier=keyword_classifier(), mode="off",
                       max_strikes=3, block_seconds=3600, window_seconds=86400)
    monkeypatch.setattr(api_module, "abuse_guard", guard)
    return guard


class FakeRedis:
    """In-memory stand-in for core.redis_rest.UpstashRedis (only the commands in use)."""

    def __init__(self, clock=lambda: 0.0):
        self.clock = clock
        self.values: dict[str, tuple[str, float | None]] = {}
        self.zsets: dict[str, dict[str, float]] = {}
        self.fail = False

    def _get(self, key):
        value, expires_at = self.values.get(key, (None, None))
        return None if expires_at is not None and expires_at <= self.clock() else value

    async def pipeline(self, *commands):
        if self.fail:
            raise RuntimeError("Redis down")
        results = []
        for name, key, *args in commands:
            if name == "SET":
                ttl = args[2] if len(args) > 2 and args[1] == "EX" else None
                self.values[key] = (args[0], self.clock() + ttl if ttl else None)
                results.append("OK")
            elif name == "GET":
                results.append(self._get(key))
            elif name == "MGET":
                results.append([self._get(k) for k in [key, *args]])
            elif name == "ZADD":
                self.zsets.setdefault(key, {})[args[1]] = args[0]
                results.append(1)
            elif name == "ZREMRANGEBYSCORE":
                zset = self.zsets.get(key, {})
                old = [m for m, score in zset.items() if score <= args[1]]
                for member in old:
                    del zset[member]
                results.append(len(old))
            elif name == "ZREVRANGE":
                ranked = sorted(self.zsets.get(key, {}).items(), key=lambda item: -item[1])
                results.append([m for m, _ in ranked][args[0]:args[1] + 1])
            else:
                raise NotImplementedError(name)
        return results


@pytest.fixture(autouse=True)
def offline_feedback_store(monkeypatch):
    """Tests never reach the real Redis, even with its credentials in .env."""
    import api.index as api_module
    from core.feedback_store import FeedbackStore

    store = FeedbackStore(None, turn_ttl_seconds=3600, retention_seconds=86400)
    monkeypatch.setattr(api_module, "feedback_store", store)
    return store
