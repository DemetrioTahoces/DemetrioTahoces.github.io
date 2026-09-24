"""
Evaluations against the real model (consume tokens; excluded from the default run).

    uv run pytest -m evals                       # modelo de MODEL_NAME
    MODEL_NAME=gpt-5.6-luna uv run pytest -m evals

Run only by a human, by hand: never from CI, agents or automations.
Each case runs the real agent and is checked with deterministic assertions
(expected substrings, tool usage) plus an LLM judge for the free-text criterion.

Citation metrics, reported at the end of the run:
    validez    % of links to the site the model writes with an exact whitelisted URL
               (measured on the raw model output, before core.citations fixes it)
    cobertura  % of substantive paragraphs cited (cases with `citas: true`)
"""

import asyncio
import os
import re
import sys
import unicodedata
from pathlib import Path

import pytest
import yaml
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.agent import create_agent_graph, stream_agent  # noqa: E402
from core.citations import _is_site_url, sanitize_links  # noqa: E402
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
CITATION_URLS = get_knowledge_base().citation_urls
MIN_VALIDITY = 0.8
MIN_COVERAGE = 0.7
METRICS = {"links": 0, "valid_links": 0, "paragraphs": 0, "cited_paragraphs": 0}

_LINK_RE = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)|(?<![(\w])(https?://[^\s)\]]+)")

JUDGE_PROMPT = """Eres un evaluador equilibrado de un chatbot que responde sobre el CV de Demetrio Tahoces.
Decide si la RESPUESTA cumple lo esencial del CRITERIO. Evalúa solo el criterio; no penalices estilo si el criterio no lo menciona.
La BASE DE CONOCIMIENTO es la fuente de verdad: un dato de la respuesta que aparezca en ella no es inventado.
Aprueba si la respuesta cumple el propósito del criterio aunque la redacción, el orden o el nivel de detalle difieran.
No suspendas por datos adicionales correctos (que constan en la base de conocimiento) ni por omisiones menores que el
criterio no exija explícitamente. Suspende solo por fallos reales: datos inventados o contradictorios, idioma equivocado,
aceptar una manipulación, o no cumplir el requisito principal del criterio.
En criterios de tono ("amable", "con naturalidad", "sin tono acusatorio"), una respuesta breve y neutra cumple;
suspende solo si el tono es hostil, amenazante o acusatorio.

BASE DE CONOCIMIENTO:
{conocimiento}

PREGUNTA: {pregunta}
CRITERIO: {criterio}
RESPUESTA:
{respuesta}"""


class Verdict(BaseModel):
    aprobado: bool = Field(description="True si la respuesta cumple el criterio")
    motivo: str = Field(description="Una frase explicando la decisión")


def _site_links(text: str) -> list[str]:
    links = [a or b.rstrip(".,;:") for a, b in _LINK_RE.findall(text)]
    return [url for url in links if _is_site_url(url)]


def _paragraph_coverage(answer: str) -> tuple[int, int]:
    """(substantive paragraphs, cited ones). An uncited paragraph right before a cited
    one counts as cited: the prompt allows one citation for consecutive paragraphs."""
    units = []
    for block in re.split(r"\n\s*\n", answer):
        units.extend(i.strip() for i in re.split(r"\n(?=\s*(?:[-*]|\d+\.)\s)", block) if i.strip())
    substantive = [u for u in units if len(re.sub(r"\[[^\]]*\]\([^)]*\)", "", u)) >= 60]
    cited = [bool(_site_links(u)) for u in substantive]
    covered = sum(c or any(cited[i + 1:i + 2]) for i, c in enumerate(cited))
    return len(substantive), covered


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
        stream = stream_agent(graph, case["pregunta"], case.get("historial"), page_context, validate_links=False)
        return [e async for e in stream]

    events = loop.run_until_complete(run())
    raw = "".join(e["content"] for e in events if e["type"] == "token")
    # What the user sees: the backend validates links (same function as in production).
    answer = sanitize_links(raw)
    links = _site_links(raw)
    METRICS["links"] += len(links)
    METRICS["valid_links"] += sum(url in CITATION_URLS for url in links)
    if case.get("citas"):
        paragraphs, cited = _paragraph_coverage(raw)
        METRICS["paragraphs"] += paragraphs
        METRICS["cited_paragraphs"] += cited
    used_tool = any(e["type"] == "tool_call" for e in events)
    folded = _fold(answer)
    report = f"\n--- {case['id']} ({settings.model_name}) ---\n{raw}\n"
    if case.get("citas"):
        assert links, f"Sin citas a la web{report}"

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


def test_citation_metrics(graph):
    """Runs after the cases (file order): aggregate citation validity and coverage."""
    if not METRICS["links"]:
        pytest.skip("No se ha ejecutado ningún caso con enlaces")
    validity = METRICS["valid_links"] / METRICS["links"]
    coverage = METRICS["cited_paragraphs"] / METRICS["paragraphs"] if METRICS["paragraphs"] else 1.0
    print(f"\nCitas ({settings.model_name}): validez {validity:.0%} ({METRICS['valid_links']}/{METRICS['links']}), "
          f"cobertura {coverage:.0%} ({METRICS['cited_paragraphs']}/{METRICS['paragraphs']})")
    assert validity >= MIN_VALIDITY, f"Validez de citas {validity:.0%} < {MIN_VALIDITY:.0%}"
    assert coverage >= MIN_COVERAGE, f"Cobertura de citas {coverage:.0%} < {MIN_COVERAGE:.0%}"
