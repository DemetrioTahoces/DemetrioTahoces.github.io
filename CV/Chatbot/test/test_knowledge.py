import re
from datetime import date

from core.config import PROJECT_ROOT, settings
from core.knowledge import BLOG_TYPE, SITE_TYPE, get_knowledge_base
from core.prompts import build_static_prompt, build_system_prompt
from core.tools import read_blog_article


def test_every_document_has_complete_frontmatter():
    kb = get_knowledge_base()
    assert len(kb.documents) >= 14
    for doc in kb.documents.values():
        assert doc.type in {"cv", "formacion", SITE_TYPE, BLOG_TYPE}, doc.name
        assert doc.title and doc.summary and doc.route.startswith("/"), doc.name
        assert not doc.body.startswith("---"), doc.name
        if doc.is_blog:
            assert doc.date, doc.name
            assert doc.route == f"/blog/posts/{doc.name.removeprefix('blog/')}.html"


def test_cv_documents_follow_explicit_order():
    names = [d.name for d in get_knowledge_base().cv_documents]
    assert names[:3] == ["CV", "RESUMEN_PROFESIONAL", "FERMAX"]


def _results(blocks):
    # Two sections can share one URL (the two Alisys roles cite the same card), so keep a list.
    results: dict[str, list[dict]] = {}
    for b in blocks:
        if b["type"] == "search_result":
            results.setdefault(b["source"], []).append(b)
    return results


def test_knowledge_message_has_every_section_as_a_citable_search_result():
    kb = get_knowledge_base()
    blocks = kb.knowledge_blocks()
    results = _results(blocks)
    for doc in kb.cv_documents + kb.blog_documents:
        assert doc.sections, doc.name
        for section in doc.sections:
            blocks_for_url = results.get(doc.section_url(section))
            assert blocks_for_url and all(b["citations"] == {"enabled": True} for b in blocks_for_url), (doc.name, section.title)
            if section.anchor:
                assert any(b["content"][0]["text"] == section.content for b in blocks_for_url), (doc.name, section.title)
    # One cache breakpoint, on the last block: the knowledge message is identical across requests.
    assert [b for b in blocks if "cache_control" in b] == [blocks[-1]]
    assert kb.knowledge_blocks() == blocks


def test_blog_falls_back_to_an_index_when_it_does_not_fit(blog_tool_mode):
    kb = get_knowledge_base()
    blocks = kb.knowledge_blocks()
    sources = _results(blocks)
    assert not any("/blog/posts/" in url for url in sources)
    index = next(b["text"] for b in blocks if b["type"] == "text" and "<indice_blog>" in b["text"])
    for doc in kb.blog_documents:
        assert doc.url in index and doc.summary in index


def test_citation_labels_name_the_page_when_the_section_is_generic():
    kb = get_knowledge_base()
    fermax = kb.get("FERMAX")
    labels = [fermax.citation_label(s) for s in fermax.sections]
    assert labels[0] == fermax.sections[0].title
    assert "Fermax · Contexto" in labels
    solid = kb.get("blog/solid-principios-diseno")
    assert solid.citation_label(solid.sections[0]) == solid.sections[0].title
    assert solid.citation_label(solid.sections[1]).startswith("SOLID · ")


def test_date_goes_last_so_the_prefix_stays_cacheable():
    first = build_system_prompt(date(2026, 1, 1))
    second = build_system_prompt(date(2026, 9, 24))
    assert first.endswith("2026-01-01") and second.endswith("2026-09-24")
    assert first.removesuffix("2026-01-01") == second.removesuffix("2026-09-24")


def test_blog_tool_reads_articles_only():
    assert read_blog_article.invoke({"article": "blog/solid-principios-diseno"})[0]["type"] == "search_result"
    assert read_blog_article.invoke({"article": "solid-principios-diseno"})[0]["title"].startswith("Idea central")
    cv_doc = read_blog_article.invoke({"article": "fermax"})
    assert "no es un artículo del blog" in cv_doc and "Fermax" not in cv_doc
    missing = read_blog_article.invoke({"article": "blog/no-existe"})
    assert "No existe" in missing and "blog/solid-principios-diseno" in missing


def test_llms_txt_is_up_to_date():
    from core.llms_txt import LLMS_TXT_PATH, render_llms_txt

    assert LLMS_TXT_PATH.read_text(encoding="utf-8") == render_llms_txt(), (
        "llms.txt desactualizado: ejecuta `uv run python -m core.llms_txt`"
    )


def test_documents_and_llms_txt_have_no_emojis():
    # Emojis belong to the blog pages; in the model's context they are noise.
    # Same ranges as check_post.py in the manage-blog skill.
    from core.llms_txt import LLMS_TXT_PATH

    emoji = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2705]")
    for path in [*sorted((PROJECT_ROOT / settings.docs_path).rglob("*.md")), LLMS_TXT_PATH]:
        found = emoji.findall(path.read_text(encoding="utf-8"))
        assert not found, f"{path.name}: los docs del chatbot y llms.txt van sin emojis ({''.join(found)})"
