"""
LangGraph ReAct agent for the CV chatbot.
"""

import logging
from typing import AsyncGenerator

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from core.config import settings
from core.prompts import SYSTEM_PROMPT
from core.tools import get_tools

logger = logging.getLogger("cv_chatbot.agent")


def _create_model() -> ChatGoogleGenerativeAI:
    """Instantiate the Gemini model from config."""
    if not settings.google_api_key:
        raise ValueError(
            "GOOGLE_API_KEY is not set. "
            "Set it as an environment variable or in .env file."
        )

    return ChatGoogleGenerativeAI(
        model=settings.model_name,
        google_api_key=settings.google_api_key,
        temperature=0.3,
        convert_system_message_to_human=False,
    )


def _trim_messages(state):
    """
    Trims the conversation history to save tokens while retaining recent context.
    Prepends the system prompt to ensure it's always available to the model.
    """
    messages = state.get("messages", []) if isinstance(state, dict) else state
    # Keep only the last 5 messages to limit token consumption growth
    trimmed_messages = messages[-5:] if len(messages) > 5 else messages
    return [SystemMessage(content=SYSTEM_PROMPT)] + trimmed_messages


def create_agent_graph():
    """
    Create the LangGraph ReAct agent with document tools.

    Returns:
        A compiled LangGraph graph ready for invocation.
    """
    model = _create_model()
    tools = get_tools()
    memory = MemorySaver()

    graph = create_react_agent(
        model=model,
        tools=tools,
        prompt=_trim_messages,
        checkpointer=memory,
    )

    logger.info(
        "Agent graph created | model=%s | tools=%d",
        settings.model_name,
        len(tools),
    )
    return graph


async def invoke_agent(graph, message: str, session_id: str) -> dict:
    """
    Invoke the agent with a user message and return the full response.

    Args:
        graph: Compiled LangGraph agent.
        message: User's question.
        session_id: Session identifier for conversation context.

    Returns:
        Dict with 'response' text and 'usage' token info.
    """
    inputs = {"messages": [("user", message)]}

    config = {"configurable": {"thread_id": session_id}}

    result = await graph.ainvoke(inputs, config=config)

    # Extract the final AI message
    ai_messages = [
        m for m in result["messages"]
        if hasattr(m, "type") and m.type == "ai" and m.content
    ]

    response_text = ai_messages[-1].content if ai_messages else "No se pudo generar una respuesta."

    # Accumulate token usage across all AI messages in the run
    total_input = 0
    total_output = 0
    for m in ai_messages:
        um = getattr(m, "usage_metadata", None)
        if um:
            total_input += um.get("input_tokens", 0)
            total_output += um.get("output_tokens", 0)

    usage = {
        "input_tokens": total_input,
        "output_tokens": total_output,
        "total_tokens": total_input + total_output,
    }

    return {
        "response": response_text,
        "usage": usage,
    }


async def stream_agent(graph, message: str, session_id: str) -> AsyncGenerator[dict, None]:
    """
    Stream the agent response token by token via SSE-compatible events.

    Yields dicts with structure:
        {"type": "token", "content": "..."}
        {"type": "tool_call", "tool": "...", "args": {...}}
        {"type": "tool_result", "tool": "...", "status": "ok"}
        {"type": "done", "usage": {...}}

    Args:
        graph: Compiled LangGraph agent.
        message: User's question.
        session_id: Session identifier.
    """
    inputs = {"messages": [("user", message)]}
    config = {"configurable": {"thread_id": session_id}}

    total_input_tokens = 0
    total_output_tokens = 0

    async for stream_mode, chunk in graph.astream(
        inputs, config=config, stream_mode=["messages", "updates"]
    ):
        if stream_mode == "messages":
            message_chunk, metadata = chunk

            # Stream AI content tokens
            if hasattr(message_chunk, "content") and message_chunk.content:
                if metadata.get("langgraph_node") == "agent":
                    yield {"type": "token", "content": message_chunk.content}

        elif stream_mode == "updates":
            if "agent" in chunk:
                messages = chunk["agent"].get("messages", [])
                if not isinstance(messages, list):
                    messages = [messages]
                for m in messages:
                    usage = _extract_usage(m)
                    total_input_tokens += usage["input_tokens"]
                    total_output_tokens += usage["output_tokens"]

            # Detect tool calls and results
            if "tools" in chunk:
                tool_messages = chunk["tools"].get("messages", [])
                if not isinstance(tool_messages, list):
                    tool_messages = [tool_messages]
                for tm in tool_messages:
                    if hasattr(tm, "name"):
                        yield {
                            "type": "tool_result",
                            "tool": tm.name,
                            "status": "ok",
                        }

    # Final event with accumulated usage data
    usage = {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
    }
    yield {"type": "done", "usage": usage}


def _extract_usage(message) -> dict:
    """Extract token usage information from a LangChain AI message."""
    if message is None:
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    usage_meta = getattr(message, "usage_metadata", None)
    if usage_meta:
        input_tokens = getattr(usage_meta, "input_tokens", 0) or usage_meta.get("input_tokens", 0) if isinstance(usage_meta, dict) else getattr(usage_meta, "input_tokens", 0)
        output_tokens = getattr(usage_meta, "output_tokens", 0) or usage_meta.get("output_tokens", 0) if isinstance(usage_meta, dict) else getattr(usage_meta, "output_tokens", 0)
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }

    # Fallback: try response_metadata
    resp_meta = getattr(message, "response_metadata", {})
    if resp_meta and "usage_metadata" in resp_meta:
        um = resp_meta["usage_metadata"]
        return {
            "input_tokens": um.get("prompt_token_count", 0),
            "output_tokens": um.get("candidates_token_count", 0),
            "total_tokens": um.get("total_token_count", 0),
        }

    return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
