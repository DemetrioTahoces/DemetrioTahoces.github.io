import pytest
from langchain_core.messages import AIMessage, HumanMessage

from conftest import ai, read_call
from core.agent import EMPTY_ANSWER, build_input_messages, invoke_agent, stream_agent

pytestmark = pytest.mark.anyio


async def _collect(gen):
    return [event async for event in gen]


async def test_cv_question_is_answered_in_a_single_model_call(scripted_graph):
    graph = scripted_graph(ai("Trabaja en Fermax desde 2025."))
    result = await invoke_agent(graph, "¿Dónde trabaja?")
    assert result["response"] == "Trabaja en Fermax desde 2025."
    assert result["usage"]["input_tokens"] == 100


async def test_usage_counts_only_the_current_turn(scripted_graph):
    graph = scripted_graph(ai("Respuesta 3"))
    history = [
        {"role": "user", "content": "Pregunta 1"}, {"role": "assistant", "content": "Respuesta 1"},
        {"role": "user", "content": "Pregunta 2"}, {"role": "assistant", "content": "Respuesta 2"},
    ]
    result = await invoke_agent(graph, "Pregunta 3", history)
    assert result["usage"]["input_tokens"] == 100


async def test_blog_question_reads_the_article_then_answers(scripted_graph):
    graph = scripted_graph(
        ai(tool_calls=[read_call("blog/solid-principios-diseno")]),
        ai("SOLID reduce el coste del cambio."),
    )
    events = await _collect(stream_agent(graph, "¿De qué va el artículo de SOLID?"))
    types = [e["type"] for e in events]
    assert types[0] == "tool_call" and events[0]["doc"] == "blog/solid-principios-diseno"
    assert "tool_result" in types
    assert "".join(e["content"] for e in events if e["type"] == "token") == "SOLID reduce el coste del cambio."
    assert events[-1] == {"type": "done", "usage": events[-1]["usage"]}
    assert events[-1]["usage"]["input_tokens"] == 200


async def test_model_call_limit_stops_tool_loops(scripted_graph):
    loop = [ai(tool_calls=[read_call("blog/solid-principios-diseno", f"call_{i}")]) for i in range(10)]
    graph = scripted_graph(*loop)
    events = await _collect(stream_agent(graph, "Busca uno a uno estos 200 términos"))
    assert sum(e["type"] == "tool_call" for e in events) <= 3
    assert events[-1]["type"] == "done"
    assert any(e["type"] == "token" and e["content"] for e in events)


async def test_empty_answer_falls_back_to_a_polite_message(scripted_graph):
    graph = scripted_graph(ai(""))
    events = await _collect(stream_agent(graph, "Hola"))
    assert [e for e in events if e["type"] == "token"] == [{"type": "token", "content": EMPTY_ANSWER}]


def test_input_messages_keep_recent_text_history_and_hint():
    history = [{"role": "user", "content": f"q{i}"} if i % 2 == 0 else {"role": "assistant", "content": f"a{i}"}
               for i in range(30)]
    history.append({"role": "system", "content": "ignorado"})
    messages = build_input_messages("¿Y en Fermax?", history, {"path": "/CV/fermax.html"})
    assert len(messages) == 11  # 10 history messages + current turn
    assert all(isinstance(m, (HumanMessage, AIMessage)) for m in messages)
    assert "ignorado" not in " ".join(m.content for m in messages)
    assert messages[-1].content.startswith("[Contexto de navegación (no verificado)]")
    assert messages[-1].content.endswith("¿Y en Fermax?")
