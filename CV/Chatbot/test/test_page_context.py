from unittest.mock import patch

from core.tools import build_page_context_hint, list_documents, read_document, search_documents


BLOG_DOCS = {
    "blog/arquitectura-hexagonal": """---
type: blog_post
title: "Arquitectura Hexagonal pragmatica"
route: "/blog/posts/arquitectura-hexagonal.html"
tags: ["backend", "arquitectura"]
---

# Arquitectura Hexagonal pragmatica

Articulo sobre puertos, adaptadores y tradeoffs en backend.
""",
}


def test_page_context_matches_dynamic_blog_route():
    with patch("core.tools._load_all_documents", return_value=BLOG_DOCS):
        hint = build_page_context_hint({
            "path": "https://demetriotahoces.github.io/blog/posts/arquitectura-hexagonal.html?utm=test",
            "title": "Arquitectura Hexagonal pragmatica",
        })

    assert hint is not None
    assert "Documento RAG asociado por ruta: blog/arquitectura-hexagonal" in hint


def test_page_context_unknown_route_is_weak_context():
    with patch("core.tools._load_all_documents", return_value=BLOG_DOCS):
        hint = build_page_context_hint({
            "path": "/blog/posts/no-existe.html",
            "title": "Ruta desconocida",
        })

    assert hint is not None
    assert "No hay documento RAG asociado por ruta" in hint


def test_tools_work_with_blog_markdown_metadata():
    with patch("core.tools._load_all_documents", return_value=BLOG_DOCS):
        listed = list_documents.invoke({})
        read = read_document.invoke({"doc_name": "blog/arquitectura-hexagonal"})
        searched = search_documents.invoke({"query": "arquitectura backend"})

    assert "blog/arquitectura-hexagonal" in listed
    assert "/blog/posts/arquitectura-hexagonal.html" in listed
    assert "puertos, adaptadores" in read
    assert "blog/arquitectura-hexagonal" in searched
