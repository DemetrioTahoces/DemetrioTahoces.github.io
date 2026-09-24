"""
CV assistant agent (LangChain create_agent on LangGraph).

Stateless by design: the client sends the recent conversation with every
request, so any Vercel instance can answer and nothing accumulates in memory.
"""

import logging
from collections.abc import AsyncGenerator, Sequence
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ModelRequest,
    ToolCallLimitMiddleware,
    dynamic_prompt,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage

from core.config import settings
from core.knowledge import build_page_context_hint, get_knowledge_base
from core.prompts import build_system_prompt
from core.tools import get_tools

logger = logging.getLogger("cv_chatbot.agent")

MODEL_NODE = "model"
TOOLS_NODE = "tools"
EMPTY_ANSWER = "Lo siento, no he podido generar una respuesta para esta consulta. ¿Puedes reformularla?"
# Replaces the technical English text that ModelCallLimitMiddleware injects.
LIMIT_ANSWER = "No he podido completar la respuesta dentro de los límites de esta consulta. ¿Puedes concretar un poco más la pregunta?"


def create_chat_model() -> BaseChatModel:
    """OpenAI model via the Responses API (required for gpt-5.x tools + reasoning)."""
    if not settings.api_key:
        raise ValueError("API_KEY is not set. Set it as an environment variable or in CV/Chatbot/.env.")

    from langchain_openai import ChatOpenAI

    kwargs: dict[str, Any] = {}
    if settings.reasoning_effort:
        kwargs["reasoning_effort"] = settings.reasoning_effort
    # Reasoning models reject temperature unless reasoning is disabled.
    if settings.reasoning_effort in (None, "none"):
        kwargs["temperature"] = 0.3

    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.api_key,
        use_responses_api=True,
        # Visitors' conversations are not retained by OpenAI (default is 30 days).
        # Encrypted reasoning keeps reasoning items replayable within a tool loop.
        store=False,
        include=["reasoning.encrypted_content"],
        stream_usage=True,
        max_tokens=settings.max_output_tokens,
        timeout=settings.request_timeout,
        max_retries=2,
        **kwargs,
    )


@dynamic_prompt
def _system_prompt(request: ModelRequest) -> str:
    return build_system_prompt()


def create_agent_graph(model: BaseChatModel | None = None):
    """Build the agent. `model` is injectable so tests can run without an API key."""
    graph = create_agent(
        model=model or create_chat_model(),
        tools=get_tools(),
        middleware=[
            _system_prompt,
            ModelCallLimitMiddleware(run_limit=settings.max_model_calls, exit_behavior="end"),
            ToolCallLimitMiddleware(run_limit=settings.max_tool_calls, exit_behavior="continue"),
        ],
    )
    logger.info(
        "Agent graph created | model=%s | docs=%d",
        settings.model_name,
        len(get_knowledge_base().documents),
    )
    return graph


def build_input_messages(
    message: str,
    history: Sequence[dict] | None = None,
    page_context: dict | None = None,
) -> list[AnyMessage]:
    """Recent history (user/assistant text only) + the current user turn."""
    messages: list[AnyMessage] = []
    for turn in history or []:
        content = str(turn.get("content") or "").strip()
        if not content:
            continue
        if turn.get("role") == "user":
            messages.append(HumanMessage(content=content))
        elif turn.get("role") == "assistant":
            messages.append(AIMessage(content=content))
    messages = messages[-settings.max_history_messages:]

    hint = build_page_context_hint(page_context)
    current = f"{hint}\n\nPregunta:\n{message}" if hint else message
    messages.append(HumanMessage(content=current))
    return messages


def _usage_of(messages: Sequence[AnyMessage]) -> dict[str, int]:
    usage = {"input_tokens": 0, "cached_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0}
    for m in messages:
        um = getattr(m, "usage_metadata", None) or {}
        usage["input_tokens"] += um.get("input_tokens", 0) or 0
        usage["output_tokens"] += um.get("output_tokens", 0) or 0
        usage["cached_tokens"] += (um.get("input_token_details") or {}).get("cache_read", 0) or 0
        usage["reasoning_tokens"] += (um.get("output_token_details") or {}).get("reasoning", 0) or 0
    usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
    return usage


def _final_text(messages: Sequence[AnyMessage]) -> str:
    for m in reversed(messages):
        if isinstance(m, AIMessage) and not m.tool_calls and m.text.strip():
            # Messages injected by middleware (call limit reached) carry no usage.
            return m.text if m.usage_metadata else LIMIT_ANSWER
    return ""


async def invoke_agent(graph, message: str, history=None, page_context=None, config: dict | None = None) -> dict:
    """Run the agent and return {'response', 'usage'} for this turn only."""
    inputs = build_input_messages(message, history, page_context)
    result = await graph.ainvoke({"messages": inputs}, config=config)
    new_messages = result["messages"][len(inputs):]
    return {
        "response": _final_text(new_messages) or EMPTY_ANSWER,
        "usage": _usage_of([m for m in new_messages if isinstance(m, AIMessage)]),
    }


async def stream_agent(
    graph, message: str, history=None, page_context=None, config: dict | None = None
) -> AsyncGenerator[dict, None]:
    """
    Stream SSE-ready events:
        {"type": "tool_call", "tool": str, "doc": str | None}
        {"type": "tool_result", "tool": str}
        {"type": "token", "content": str}
        {"type": "done", "usage": {...}}
    """
    inputs = build_input_messages(message, history, page_context)
    ai_messages: list[AIMessage] = []
    streamed_text = False
    fallback_text = ""

    async for mode, chunk in graph.astream({"messages": inputs}, config=config, stream_mode=["messages", "updates"]):
        if mode == "messages":
            message_chunk, metadata = chunk
            # Streaming models emit AIMessageChunk; non-streaming ones, the full AIMessage.
            if metadata.get("langgraph_node") == MODEL_NODE and isinstance(message_chunk, AIMessage):
                text = message_chunk.text
                if text:
                    streamed_text = True
                    yield {"type": "token", "content": text}
            continue

        for node, update in (chunk or {}).items():
            node_messages = (update or {}).get("messages", []) if isinstance(update, dict) else []
            if not isinstance(node_messages, list):
                node_messages = [node_messages]
            for m in node_messages:
                if isinstance(m, AIMessage):
                    if node == MODEL_NODE:
                        ai_messages.append(m)
                        for call in m.tool_calls:
                            yield {"type": "tool_call", "tool": call["name"], "doc": call["args"].get("article")}
                        if not m.tool_calls and m.text.strip():
                            fallback_text = m.text
                    elif not m.tool_calls and m.text.strip():
                        # Answer injected by middleware: the model call limit was reached.
                        fallback_text = LIMIT_ANSWER
                elif isinstance(m, ToolMessage) and node == TOOLS_NODE:
                    yield {"type": "tool_result", "tool": m.name}

    if not streamed_text:
        yield {"type": "token", "content": fallback_text or EMPTY_ANSWER}
    yield {"type": "done", "usage": _usage_of(ai_messages)}
