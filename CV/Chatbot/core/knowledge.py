"""
Knowledge base built from the Markdown documents in docs/.

The CV corpus is small (~7k tokens), so it is injected whole into the system
prompt (and cached by the provider). Blog articles are only listed in the
prompt; their content is loaded on demand through the read_blog_article tool.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

from core.config import PROJECT_ROOT, settings

BLOG_TYPE = "blog_post"
PAGE_CONTEXT_MAX_LENGTH = 220


@dataclass(frozen=True)
class Document:
    name: str
    type: str
    title: str
    summary: str
    route: str
    tags: tuple[str, ...]
    date: str
    order: int
    body: str

    @property
    def url(self) -> str:
        return f"{settings.public_site_url}{self.route}" if self.route else ""

    @property
    def is_blog(self) -> bool:
        return self.type == BLOG_TYPE


def _split_frontmatter(content: str) -> tuple[dict, str]:
    """Return (metadata, body) for a Markdown file with optional YAML frontmatter."""
    if not content.startswith("---"):
        return {}, content
    lines = content.splitlines()
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            metadata = yaml.safe_load("\n".join(lines[1:idx])) or {}
            body = "\n".join(lines[idx + 1:]).strip()
            return (metadata if isinstance(metadata, dict) else {}), body
    return {}, content


def _parse_document(name: str, content: str) -> Document:
    metadata, body = _split_frontmatter(content)
    title = str(metadata.get("title") or "").strip()
    if not title:
        heading = next((line.lstrip("#").strip() for line in body.splitlines() if line.startswith("#")), "")
        title = heading or name
    tags = metadata.get("tags") or []
    return Document(
        name=name,
        type=str(metadata.get("type") or (BLOG_TYPE if name.startswith("blog/") else "cv")).strip(),
        title=title,
        summary=str(metadata.get("summary") or "").strip(),
        route=str(metadata.get("route") or "").strip(),
        tags=tuple(str(tag) for tag in tags) if isinstance(tags, list) else (),
        date=str(metadata.get("date") or "").strip(),
        order=int(metadata.get("order") or 999),
        body=body,
    )


def normalize_route_path(value: object) -> str:
    """Normalize a public site path or URL for route matching ('' if unusable)."""
    if not isinstance(value, str):
        return ""
    raw = value.strip()[:PAGE_CONTEXT_MAX_LENGTH]
    if not raw:
        return ""

    parsed = urlsplit(raw)
    path = parsed.path if parsed.scheme or parsed.netloc else raw.split("?", 1)[0].split("#", 1)[0]
    path = unquote(path).replace("\\", "/").strip()

    lower = path.lower()
    for marker in ("/cv/", "/blog/", "/fundamentosia/"):
        marker_idx = lower.find(marker)
        if marker_idx != -1:
            path = path[marker_idx:]
            break

    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    if not path.startswith("/"):
        path = "/" + path
    while "//" in path:
        path = path.replace("//", "/")
    return path.lower()


class KnowledgeBase:
    def __init__(self, documents: list[Document]):
        self.documents = {doc.name: doc for doc in documents}

    @classmethod
    def from_directory(cls, docs_dir: Path) -> "KnowledgeBase":
        documents = []
        if docs_dir.exists():
            for md_file in sorted(docs_dir.rglob("*.md")):
                name = md_file.relative_to(docs_dir).with_suffix("").as_posix()
                documents.append(_parse_document(name, md_file.read_text(encoding="utf-8")))
        return cls(documents)

    @property
    def cv_documents(self) -> list[Document]:
        return sorted((d for d in self.documents.values() if not d.is_blog), key=lambda d: (d.order, d.name))

    @property
    def blog_documents(self) -> list[Document]:
        return sorted((d for d in self.documents.values() if d.is_blog), key=lambda d: (d.date, d.name), reverse=True)

    def get(self, requested: str) -> Document | None:
        """Resolve a user/model supplied name ('FERMAX', 'fermax', 'blog/solid-principios-diseno.md')."""
        key = requested.strip().replace("\\", "/").removesuffix(".md").strip("/")
        if key in self.documents:
            return self.documents[key]
        for candidate in (key.upper().replace(" ", "_"), key.lower().replace(" ", "-"), f"blog/{key.lower()}"):
            for name, doc in self.documents.items():
                if name.lower() == candidate.lower():
                    return doc
        return None

    def find_by_route(self, path: object) -> Document | None:
        """Match a browser path against the documents' public routes (fragments excluded)."""
        normalized = normalize_route_path(path)
        if not normalized:
            return None
        for doc in self.documents.values():
            if doc.route and "#" not in doc.route and normalize_route_path(doc.route) == normalized:
                return doc
        return None

    def render_for_prompt(self) -> str:
        """Stable text block with the full CV corpus and the blog index."""
        parts = ["<documentos_cv>"]
        for doc in self.cv_documents:
            parts.append(f'<documento nombre="{doc.name}" titulo="{doc.title}" url="{doc.url}">\n{doc.body}\n</documento>')
        parts.append("</documentos_cv>")

        parts.append("<articulos_blog>")
        if self.blog_documents:
            for doc in self.blog_documents:
                parts.append(f"- {doc.name} | {doc.title} | {doc.date} | {doc.url} | {doc.summary}")
        else:
            parts.append("(todavía no hay artículos publicados)")
        parts.append("</articulos_blog>")
        return "\n".join(parts)


@lru_cache(maxsize=1)
def get_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase.from_directory(PROJECT_ROOT / settings.docs_path)


def build_page_context_hint(page_context: dict | None, kb: KnowledgeBase | None = None) -> str | None:
    """
    Weak navigation hint for the current turn.

    Only the path is used, and only when it matches a known document route, so
    client-controlled text (page titles, arbitrary paths) never reaches the model.
    """
    if not isinstance(page_context, dict):
        return None
    doc = (kb or get_knowledge_base()).find_by_route(page_context.get("path"))
    if doc is None:
        return None
    return (
        "[Contexto de navegación (no verificado)]\n"
        f"La persona está viendo la página «{doc.title}» ({doc.url}), "
        f"asociada al documento {doc.name}."
    )
