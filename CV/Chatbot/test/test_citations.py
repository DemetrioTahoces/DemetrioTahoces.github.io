"""Section anchors (Markdown <-> HTML) and validation of the links the model writes."""

import random
import re
from pathlib import Path

import pytest

from conftest import ai, read_call
from core.citations import StreamingLinkSanitizer, canonical_url, sanitize_links
from core.knowledge import EXTRA_PAGES, _parse_sections, get_knowledge_base
from core.tools import read_blog_article

SITE_ROOT = Path(__file__).resolve().parents[3]
SITE = "https://demetriotahoces.github.io"


def _html_file(route: str) -> Path:
    path = route.split("#", 1)[0]
    if path.endswith("/"):
        path += "index.html"
    return SITE_ROOT / path.lstrip("/")


def _html_ids(route: str) -> set[str]:
    ids = re.findall(r'\bid="([^"]+)"', _html_file(route).read_text(encoding="utf-8"))
    duplicated = {i for i in ids if ids.count(i) > 1}
    assert not duplicated, f"ids duplicados en {_html_file(route).name}: {duplicated}"
    return set(ids)


# --- Parser -------------------------------------------------------------------


def test_sections_inherit_anchors_and_fold_grouping_headings():
    body, sections, anchors = _parse_sections(
        "# Título\nIntro\n\n## Contexto {#contexto}\nTexto\n\n## Contribuciones {#contribuciones}\n\n"
        "### Una {#una}\n- a\n\n### Dos\n- b\n\n## Stack\n- c"
    )
    assert "{#" not in body and "## Contexto\n" in body
    assert [(s.title, s.anchor) for s in sections] == [
        ("Título", ""), ("Contexto", "contexto"), ("Una", "una"), ("Dos", "contribuciones"), ("Stack", ""),
    ]
    # The grouping heading has no text of its own: it travels with its first child.
    assert sections[2].content.startswith("## Contribuciones\n\n### Una")
    assert anchors == ("contexto", "contribuciones", "una")


# --- Markdown <-> HTML consistency --------------------------------------------


def test_every_declared_anchor_exists_in_its_html_page():
    for doc in get_knowledge_base().documents.values():
        ids = _html_ids(doc.route)
        fragment = doc.route.partition("#")[2]
        missing = [a for a in (*doc.anchors, *([fragment] if fragment else [])) if a not in ids]
        assert not missing, f"{doc.name}: anclas sin id en {_html_file(doc.route).name}: {missing}"


def test_every_section_is_cited_with_an_anchor():
    for doc in get_knowledge_base().documents.values():
        for section in doc.sections[1:]:  # the first one is the page header (H1)
            assert "#" in doc.section_url(section), f"{doc.name}: '{section.title}' sin ancla"


def test_link_targets_are_real_pages():
    kb = get_knowledge_base()
    for route in ("/", *EXTRA_PAGES, *(d.route for d in kb.documents.values())):
        assert _html_file(route).exists() or (SITE_ROOT / route.lstrip("/")).exists(), route


def test_every_citation_url_is_canonical():
    kb = get_knowledge_base()
    assert len(kb.citation_urls) > 80
    for url in kb.citation_urls:
        assert url.startswith(SITE + "/")
        assert canonical_url(url) == url


# --- Link validation ----------------------------------------------------------

VALID = f"{SITE}/CV/fermax.html#desarrollo-agentico"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (f"Lidera IA. [↗ Desarrollo agéntico]({VALID})", f"Lidera IA. [↗ Desarrollo agéntico]({VALID})"),
        # Invented anchor on a real page: keep the page.
        (f"A [↗ Fermax]({SITE}/CV/fermax.html#inventada) b", f"A [↗ Fermax]({SITE}/CV/fermax.html) b"),
        # Invented page: the citation disappears, a plain link keeps its text.
        (f"A [↗ Google]({SITE}/CV/google.html). Fin", "A. Fin"),
        (f"Ver [su web]({SITE}/nope.html).", "Ver su web."),
        # Wrong scheme, case, domain or relative paths: rewritten to the canonical URL.
        ("[x](http://DemetrioTahoces.GitHub.io/cv/Fermax.html#Contexto)", f"[x]({SITE}/CV/fermax.html#contexto)"),
        ("[x](https://demetriotahoces.com/CV/opendit)", f"[x]({SITE}/CV/opendit.html)"),
        ("[x](demetriotahoces.github.io/CV/inditex.html#snowflake)", f"[x]({SITE}/CV/inditex.html#snowflake)"),
        ("[x](/CV/tfg.html) [y](fermax.html)", f"[x]({SITE}/CV/tfg.html) [y]({SITE}/CV/fermax.html)"),
        (f"[x]({SITE}) [y]({SITE}/blog)", f"[x]({SITE}/) [y]({SITE}/blog/)"),
        ("[↗ Formación](https://demetriotahoces.github.io/#formacion)", f"[↗ Formación]({SITE}/#formacion)"),
        ("[↗ Contexto](#contexto) y [texto](#otra)", " y texto"),
        # External links are not touched.
        ("[LinkedIn](https://www.linkedin.com/in/x) · [mail](mailto:a@b.c) · https://www.uniovi.es/",
         "[LinkedIn](https://www.linkedin.com/in/x) · [mail](mailto:a@b.c) · https://www.uniovi.es/"),
        # Bare URLs to the site.
        (f"En {SITE}/CV/inditex.html#snowflake. Y {SITE}/nope.html",
         f"En {SITE}/CV/inditex.html#snowflake. Y {SITE}/"),
        ("Texto [sin enlace] y [corchetes]", "Texto [sin enlace] y [corchetes]"),
    ],
)
def test_sanitize_links(text, expected):
    assert sanitize_links(text) == expected


def test_streaming_sanitizer_matches_the_full_text_for_any_chunking():
    text = (
        f"Párrafo uno. [↗ Desarrollo agéntico]({VALID})\n\n"
        f"- Kafka [↗ Pipelines]({SITE}/CV/inditex.html#inventada)\n"
        f"- Algo [↗ Nada]({SITE}/CV/nada.html)\n\n"
        f"Lista [no enlace] y [a]\nBare {SITE}/CV/tfg.html#objetivos-principales. Fin [x](http://demetriotahoces.github.io/cv/opendit.html)"
    )
    rng = random.Random(7)
    for _ in range(300):
        stream, out, i = StreamingLinkSanitizer(), "", 0
        while i < len(text):
            size = rng.randint(1, 9)
            out += stream.feed(text[i:i + size])
            i += size
        assert out + stream.flush() == sanitize_links(text)


def test_streaming_sanitizer_releases_plain_text_promptly():
    stream = StreamingLinkSanitizer()
    assert stream.feed("Trabaja en Fermax desde ") == "Trabaja en Fermax desde"
    assert stream.feed("2025. Ver [↗ Fer") == " 2025. Ver"
    assert stream.feed(f"max]({SITE}/CV/fermax.html#nope) ") == f" [↗ Fermax]({SITE}/CV/fermax.html)"
    assert stream.flush() == " "


def test_streaming_sanitizer_never_stalls_on_an_unclosed_bracket():
    stream = StreamingLinkSanitizer()
    out = stream.feed("[" + "palabra " * 100)
    assert out.startswith("[palabra")


# --- Integration --------------------------------------------------------------


@pytest.mark.anyio
async def test_stream_and_invoke_never_return_invalid_site_links(scripted_graph):
    from core.agent import invoke_agent, stream_agent

    answer = f"Lidera IA [↗ Fermax]({SITE}/CV/fermax.html#inventada).\n\nOtro [↗ X]({SITE}/CV/x.html)"
    expected = f"Lidera IA [↗ Fermax]({SITE}/CV/fermax.html).\n\nOtro"

    events = [e async for e in stream_agent(scripted_graph(ai(answer)), "¿Qué hace en Fermax?")]
    assert "".join(e["content"] for e in events if e["type"] == "token") == expected
    assert events[-1]["type"] == "done"

    result = await invoke_agent(scripted_graph(ai(answer)), "¿Qué hace en Fermax?")
    assert result["response"] == expected


@pytest.mark.anyio
async def test_text_before_a_tool_call_keeps_its_order(scripted_graph):
    from core.agent import stream_agent

    graph = scripted_graph(ai("Lo miro en [el blog", tool_calls=[read_call("blog/solid-principios-diseno")]), ai("] listo."))
    events = [e async for e in stream_agent(graph, "SOLID")]
    types = [e["type"] for e in events]
    assert types.index("token") < types.index("tool_call")


def test_blog_tool_returns_sections_with_citable_urls():
    article = read_blog_article.invoke({"article": "blog/solid-principios-diseno"})
    assert article.startswith('<articulo nombre="blog/solid-principios-diseno"')
    assert f'<seccion url="{SITE}/blog/posts/solid-principios-diseno.html#o-open-closed-principle">' in article
    assert "{#" not in article
