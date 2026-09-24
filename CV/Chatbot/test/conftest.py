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


@pytest.fixture
def anyio_backend():
    return "asyncio"
