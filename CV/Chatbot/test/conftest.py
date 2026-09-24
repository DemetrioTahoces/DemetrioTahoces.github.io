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
