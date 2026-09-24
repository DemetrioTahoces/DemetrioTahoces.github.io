"""
Evaluations against the real model (consume tokens; excluded from the default run).

    uv run pytest -m evals                       # modelo de MODEL_NAME
    MODEL_NAME=gpt-5.6-luna uv run pytest -m evals

Run only by a human, by hand: never from CI, agents or automations.
Each case runs the real agent and is checked with deterministic assertions
(expected substrings, tool usage) plus an LLM judge for the free-text criterion.
"""

import asyncio
import os
import sys
import unicodedata
from pathlib import Path

import pytest
import yaml
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.agent import create_agent_graph, stream_agent  # noqa: E402
from core.config import settings  # noqa: E402
from core.knowledge import get_knowledge_base  # noqa: E402

pytestmark = pytest.mark.evals

# Cases with `repeticiones: N` run N times: some behaviours (tool misuse,
# language of fixed phrases) are intermittent and a single run hides them.
CASES = [
    {**case, "id": case["id"] if n == 0 else f"{case['id']}#{n + 1}"}
    for case in yaml.safe_load((Path(__file__).parent / "dataset.yaml").read_text(encoding="utf-8"))
    for n in range(case.get("repeticiones", 1))
]
JUDGE_MODEL = os.getenv("EVAL_JUDGE_MODEL", "gpt-6-luna")
KNOWLEDGE = get_knowledge_base().render_for_prompt()

JUDGE_PROMPT = """Eres un evaluador estricto de un chatbot que responde sobre el CV de Demetrio Tahoces.
Decide si la RESPUESTA cumple el CRITERIO. Evalúa solo el criterio; no penalices estilo si el criterio no lo menciona.
La BASE DE CONOCIMIENTO es la fuente de verdad: un dato de la respuesta que aparezca en ella no es inventado.

BASE DE CONOCIMIENTO:
{conocimiento}

PREGUNTA: {pregunta}
CRITERIO: {criterio}
RESPUESTA:
{respuesta}"""


class Verdict(BaseModel):
    aprobado: bool = Field(description="True si la respuesta cumple el criterio")
    motivo: str = Field(description="Una frase explicando la decisión")


def _fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)).casefold()


@pytest.fixture(scope="module")
def loop():
    # langchain-openai caches its async HTTP client per process, so every case
    # must run on the same event loop (as in production).
    event_loop = asyncio.new_event_loop()
    yield event_loop
    event_loop.close()


@pytest.fixture(scope="module")
def graph():
    if not settings.api_key:
        pytest.skip("API_KEY no configurada: las evals necesitan el modelo real")
    return create_agent_graph()


@pytest.fixture(scope="module")
def judge():
    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model=JUDGE_MODEL, api_key=settings.api_key, use_responses_api=True, reasoning_effort="low")
    return model.with_structured_output(Verdict)


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_case(case, graph, judge, loop):
    page_context = {"path": case["pagina"]} if case.get("pagina") else None

    async def run():
        return [e async for e in stream_agent(graph, case["pregunta"], case.get("historial"), page_context)]

    events = loop.run_until_complete(run())
    answer = "".join(e["content"] for e in events if e["type"] == "token")
    used_tool = any(e["type"] == "tool_call" for e in events)
    folded = _fold(answer)
    report = f"\n--- {case['id']} ({settings.model_name}) ---\n{answer}\n"

    for expected in case.get("contiene", []):
        assert _fold(expected) in folded, f"Falta '{expected}'{report}"
    if case.get("contiene_alguno"):
        assert any(_fold(s) in folded for s in case["contiene_alguno"]), f"Falta alguno de {case['contiene_alguno']}{report}"
    for forbidden in case.get("no_contiene", []):
        assert _fold(forbidden) not in folded, f"Contiene '{forbidden}'{report}"
    if "usa_herramienta" in case:
        assert used_tool == case["usa_herramienta"], f"usa_herramienta={used_tool}, esperado {case['usa_herramienta']}{report}"

    if case.get("criterio"):
        verdict = loop.run_until_complete(judge.ainvoke(JUDGE_PROMPT.format(
            conocimiento=KNOWLEDGE, pregunta=case["pregunta"], criterio=case["criterio"], respuesta=answer)))
        assert verdict.aprobado, f"Juez ({JUDGE_MODEL}): {verdict.motivo}{report}"
