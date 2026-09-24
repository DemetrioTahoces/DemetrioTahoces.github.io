from datetime import date

from core.knowledge import BLOG_TYPE, get_knowledge_base
from core.prompts import build_static_prompt, build_system_prompt
from core.tools import read_blog_article


def test_every_document_has_complete_frontmatter():
    kb = get_knowledge_base()
    assert len(kb.documents) >= 14
    for doc in kb.documents.values():
        assert doc.type in {"cv", "formacion", BLOG_TYPE}, doc.name
        assert doc.title and doc.summary and doc.route.startswith("/"), doc.name
        assert not doc.body.startswith("---"), doc.name
        if doc.is_blog:
            assert doc.date, doc.name
            assert doc.route == f"/blog/posts/{doc.name.removeprefix('blog/')}.html"


def test_cv_documents_follow_explicit_order():
    names = [d.name for d in get_knowledge_base().cv_documents]
    assert names[:3] == ["CV", "RESUMEN_PROFESIONAL", "FERMAX"]


def test_system_prompt_contains_full_cv_and_blog_index_only():
    kb = get_knowledge_base()
    prompt = build_static_prompt()
    for doc in kb.cv_documents:
        assert doc.body[:200] in prompt, doc.name
    for doc in kb.blog_documents:
        assert doc.url in prompt and doc.summary in prompt
        # Blog bodies are loaded on demand through read_blog_article.
        assert doc.body[-300:] not in prompt


def test_date_goes_last_so_the_prefix_stays_cacheable():
    first = build_system_prompt(date(2026, 1, 1))
    second = build_system_prompt(date(2026, 9, 24))
    assert first.endswith("2026-01-01") and second.endswith("2026-09-24")
    assert first.removesuffix("2026-01-01") == second.removesuffix("2026-09-24")


def test_blog_tool_reads_articles_only():
    assert "SOLID" in read_blog_article.invoke({"article": "blog/solid-principios-diseno"})
    assert "SOLID" in read_blog_article.invoke({"article": "solid-principios-diseno"})
    cv_doc = read_blog_article.invoke({"article": "fermax"})
    assert "no es un artículo del blog" in cv_doc and "Fermax" not in cv_doc
    missing = read_blog_article.invoke({"article": "blog/no-existe"})
    assert "No existe" in missing and "blog/solid-principios-diseno" in missing


def test_llms_txt_is_up_to_date():
    from core.llms_txt import LLMS_TXT_PATH, render_llms_txt

    assert LLMS_TXT_PATH.read_text(encoding="utf-8") == render_llms_txt(), (
        "llms.txt desactualizado: ejecuta `uv run python -m core.llms_txt`"
    )
