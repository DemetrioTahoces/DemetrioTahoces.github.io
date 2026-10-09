"""
Knowledge base built from the Markdown documents in docs/.

The corpus is small (~24k tokens), so it is sent whole with every request (and
cached by the provider) as Claude `search_result` blocks, one per section of the
public site: Claude then cites them natively and the citations carry the exact
section URL. While the blog fits under BLOG_IN_PROMPT_MAX_CHARS its articles go
in too; past that, only an index is sent and articles are loaded on demand
through the read_blog_article tool.

Headings may declare the anchor of the matching HTML section, e.g.
`## Contexto {#contexto}`. Documents are split into sections so every claim can
be cited with a URL that points to that exact section of the public site.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property, lru_cache
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

from core.config import PROJECT_ROOT, settings

BLOG_TYPE = "blog_post"
# About the site itself (the assistant, its MCP server): in the knowledge base, but not part
# of the CV in llms.txt nor a navigation hint (its route is the chat page itself).
SITE_TYPE = "sitio"
PAGE_CONTEXT_MAX_LENGTH = 220
# Public pages that exist but have no document behind them (valid link targets).
EXTRA_PAGES = ("/blog/", "/CV/chatbot.html", "/FundamentosIA/", "/llms.txt")

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)(?:\s*\{#([A-Za-z0-9_-]+)\})?\s*$")


@dataclass(frozen=True)
class Section:
    title: str
    anchor: str  # own or inherited from the parent heading; '' = the document URL
    content: str


def _parse_sections(body: str) -> tuple[str, tuple[Section, ...], tuple[str, ...]]:
    """Return (body without anchor markers, sections, every declared anchor).

    A section runs from a heading to the next one. Headings without an anchor
    inherit their parent's, and headings with no text of their own (e.g. a
    "## Contribuciones" that only groups "###" entries) are folded into the next
    section so no section is empty.
    """
    clean_lines: list[str] = []
    sections: list[Section] = []
    parents: list[tuple[int, str]] = []
    declared: list[str] = []
    title, anchor, lines, has_text = "", "", [], False
    in_code = False

    def close():
        if has_text:
            sections.append(Section(title=title, anchor=anchor, content="\n".join(lines).strip()))

    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        match = None if in_code else _HEADING_RE.match(line)
        if not match:
            clean_lines.append(line)
            lines.append(line)
            has_text = has_text or bool(line.strip())
            continue
        level, heading, own_anchor = len(match.group(1)), match.group(2).strip(), match.group(3) or ""
        clean = f"{match.group(1)} {heading}"
        clean_lines.append(clean)
        if own_anchor and own_anchor not in declared:
            declared.append(own_anchor)
        while parents and parents[-1][0] >= level:
            parents.pop()
        inherited = own_anchor or (parents[-1][1] if parents else "")
        parents.append((level, inherited))
        close()
        carried = lines if not has_text else []
        title, anchor, lines, has_text = heading, inherited, [*carried, clean], False
    close()
    return "\n".join(clean_lines).strip(), tuple(sections), tuple(declared)


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
    sections: tuple[Section, ...] = ()
    anchors: tuple[str, ...] = ()  # every {#anchor} declared, including grouping headings

    @property
    def url(self) -> str:
        return f"{settings.public_site_url}{self.route}" if self.route else ""

    @property
    def page_url(self) -> str:
        """Document URL without fragment."""
        return self.url.split("#", 1)[0]

    def section_url(self, section: Section) -> str:
        return f"{self.page_url}#{section.anchor}" if section.anchor and self.url else self.url

    @property
    def short_title(self) -> str:
        """'Software Engineer en Fermax' -> 'Fermax'; 'SOLID: principios...' -> 'SOLID'."""
        short = self.title.split(":", 1)[0].strip()
        if self.type == "cv" and " en " in short:
            short = short.rsplit(" en ", 1)[1]
        return short

    def citation_label(self, section: Section) -> str:
        """Label of the citation chip: the section, with its page when the title alone is ambiguous."""
        if section is self.sections[0] or self.short_title.lower() in section.title.lower():
            return section.title
        return f"{self.short_title} · {section.title}"

    def search_results(self) -> list[dict]:
        """One Claude search_result block per section, so answers cite the exact section URL."""
        return [
            {
                "type": "search_result",
                "source": self.section_url(s),
                "title": self.citation_label(s),
                "content": [{"type": "text", "text": s.content}],
                "citations": {"enabled": True},
            }
            for s in self.sections
        ]

    def render_sections(self) -> str:
        """Body as <seccion> blocks, each with the URL that supports it."""
        return "\n".join(
            f'<seccion url="{self.section_url(s)}">\n{s.content}\n</seccion>'
            for s in self.sections
        )

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
    body, sections, anchors = _parse_sections(body)
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
        sections=sections,
        anchors=anchors,
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
            if doc.type == SITE_TYPE:
                continue
            if doc.route and "#" not in doc.route and normalize_route_path(doc.route) == normalized:
                return doc
        return None

    @cached_property
    def link_targets(self) -> dict[str, tuple[str, frozenset[str]]]:
        """Normalized page path -> (canonical page URL, valid anchors on that page)."""
        pages: dict[str, tuple[str, set[str]]] = {}

        def add(route: str, anchors=()):
            path, _, fragment = route.partition("#")
            entry = pages.setdefault(normalize_route_path(path or "/"), (f"{settings.public_site_url}{path or '/'}", set()))
            entry[1].update(a for a in (fragment, *anchors) if a)

        add("/")
        for route in EXTRA_PAGES:
            add(route)
        for doc in self.documents.values():
            if doc.route:
                add(doc.route, doc.anchors)
        return {path: (url, frozenset(anchors)) for path, (url, anchors) in pages.items()}

    @property
    def citation_urls(self) -> set[str]:
        """Every page and page#anchor URL the assistant may link to."""
        return {url for url, _ in self.link_targets.values()} | {
            f"{url}#{anchor}" for url, anchors in self.link_targets.values() for anchor in anchors
        }

    @property
    def blog_inline(self) -> bool:
        """Whether the blog articles fit in the knowledge message (otherwise: index + tool)."""
        return sum(len(d.body) for d in self.blog_documents) <= settings.blog_in_prompt_max_chars

    def blog_index(self) -> str:
        lines = [f"- {d.name} | {d.title} | {d.date} | {d.url} | {d.summary}" for d in self.blog_documents]
        return "\n".join(lines) or "(todavía no hay artículos publicados)"

    def knowledge_blocks(self, closing: str = "") -> list[dict]:
        """
        Content of the first user message: every section as a search_result block
        (CV, then blog articles or the blog index) and `closing` last. Identical
        across requests; the cache breakpoint on its last block keeps it cached
        even when the conversation that follows changes.
        """
        blog_inline = self.blog_inline
        blocks: list[dict] = [{
            "type": "text",
            "text": "<base_de_conocimiento>\nCV completo de Demetrio"
            + (" y artículos de su blog" if blog_inline else "")
            + ": cada resultado es una sección de su web, con su URL como fuente.",
        }]
        for doc in self.cv_documents + (self.blog_documents if blog_inline else []):
            blocks.extend(doc.search_results())
        if not blog_inline:
            blocks.append({"type": "text", "text": f"<indice_blog>\n{self.blog_index()}\n</indice_blog>"})
        blocks.append({"type": "text", "text": "</base_de_conocimiento>" + (f"\n\n{closing}" if closing else "")})
        blocks[-1]["cache_control"] = {"type": "ephemeral", "ttl": "1h"}
        return blocks

    def render_for_prompt(self) -> str:
        """Plain-text corpus (CV sections + blog index), for the evals judge."""
        parts = ["<documentos_cv>"]
        for doc in self.cv_documents:
            parts.append(f'<documento nombre="{doc.name}" titulo="{doc.title}" url="{doc.url}">\n{doc.render_sections()}\n</documento>')
        parts.append("</documentos_cv>")

        parts.append(f"<articulos_blog>\n{self.blog_index()}\n</articulos_blog>")
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
