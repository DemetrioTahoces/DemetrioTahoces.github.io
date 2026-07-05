"""
Document retrieval tools for the LangGraph agent.

Provides tools that allow the agent to discover, read, and search
the markdown documents stored in the docs/ directory.
"""

import ast
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from langchain_core.tools import tool

from core.config import settings

PAGE_CONTEXT_MAX_LENGTH = 220


def _get_docs_dir() -> Path:
    """Resolve the absolute path to the docs directory."""
    # On Vercel, the working directory is the project root (CV/Chatbot/).
    # Locally, it depends on where uvicorn is started from.
    base = Path(__file__).parent.parent
    return base / settings.docs_path


def _load_all_documents() -> dict[str, str]:
    """
    Load all .md files from the docs directory recursively.

    Documents in subfolders use POSIX-style relative keys without extension.
    Example: docs/blog/rag-basico.md becomes blog/rag-basico.

    Root-level document keys stay backward compatible with the previous format
    (CV, FERMAX, RESUMEN_PROFESIONAL, etc.).
    """
    docs: dict[str, str] = {}
    docs_dir = _get_docs_dir()
    if not docs_dir.exists():
        return docs

    for md_file in sorted(docs_dir.rglob("*.md")):
        rel_path = md_file.relative_to(docs_dir).with_suffix("")
        doc_name = rel_path.as_posix()
        docs[doc_name] = md_file.read_text(encoding="utf-8")

    return docs


def _split_frontmatter(content: str) -> tuple[dict[str, object], str]:
    """Parse a minimal frontmatter block without adding YAML dependencies."""
    if not content.startswith("---"):
        return {}, content

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, content

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break

    if end_idx is None:
        return {}, content

    metadata: dict[str, object] = {}
    for line in lines[1:end_idx]:
        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        value = raw_value.strip('"').strip("'")

        if not key:
            continue

        if raw_value.startswith("[") and raw_value.endswith("]"):
            try:
                parsed = ast.literal_eval(raw_value)
                if isinstance(parsed, list):
                    metadata[key] = [str(item) for item in parsed]
                    continue
            except (SyntaxError, ValueError):
                pass

        metadata[key] = value

    body = "\n".join(lines[end_idx + 1:]).lstrip()
    return metadata, body


def _document_metadata(doc_name: str, content: str) -> dict[str, object]:
    """Return normalized metadata for a markdown document."""
    metadata, body = _split_frontmatter(content)
    title = str(metadata.get("title") or _extract_title(body) or "").strip()
    doc_type = str(metadata.get("type") or ("blog_post" if doc_name.startswith("blog/") else "cv")).strip()
    route = str(metadata.get("route") or "").strip()
    tags = metadata.get("tags") if isinstance(metadata.get("tags"), list) else []

    return {
        "name": doc_name,
        "title": title,
        "type": doc_type,
        "route": route,
        "tags": tags,
        "body": body,
    }


# Brief descriptions for known root documents. Dynamic blog articles are
# described from their Markdown heading.
_DOC_DESCRIPTIONS = {
    "CV": "Currículum completo — resumen, experiencia, formación, competencias técnicas e idiomas",
    "RESUMEN_PROFESIONAL": "Resumen extendido — pilares de valor, evolución técnica, filosofía de trabajo",
    "FERMAX": "Experiencia ACTUAL en Fermax — Software Engineer, IoT, DDD, Kubernetes (01/2025-Presente). Trabajo actual.",
    "OPENDIT": "Experiencia en Opendit — Backend Engineer, DAPR, BFF, CQRS (2022-2024)",
    "INDITEX": "Experiencia en Inditex (Nunegal) — Ingeniero de Datos, Kafka, Snowflake (2021-2022)",
    "SECURITAS_DIRECT": "Experiencia en Securitas Direct (Vector ITC) — Procesado de señales (2021)",
    "ALISYS": "Experiencia en Alisys — Robótica, IA, Android, VoIP (2019-2021)",
    "IMAGINE800": "Experiencia en Imagine800 (Incluye TFM) — Apps Android, VoIP, Asterisk (2019)",
    "GRADO_TELECOMUNICACION": "Grado en Ingeniería de Telecomunicación — Universidad de Oviedo (2012-2017)",
    "MASTER_TELECOMUNICACION": "Máster en Ingeniería de Telecomunicación — VoIP, Android (2017-2019)",
    "MASTER_IA_APLICADA": "Máster en IA Aplicada y Optimización de Procesos — RAG, Agentes (2026)",
    "TFG": "Trabajo de Final de Grado (TFG) — Redes neuronales para procesado de arrays de antenas",
}


def _extract_title(content: str) -> str | None:
    """Extract the first Markdown heading from a document."""
    for line in content.splitlines():
        clean = line.strip()
        if clean.startswith("#"):
            title = clean.lstrip("#").strip()
            return title or None
    return None


def _describe_document(doc_name: str, content: str) -> str:
    """Return a short description for a document key."""
    if doc_name in _DOC_DESCRIPTIONS:
        return _DOC_DESCRIPTIONS[doc_name]

    metadata = _document_metadata(doc_name, content)
    title = str(metadata.get("title") or "")
    if doc_name.startswith("blog/"):
        if title:
            return f"Artículo del blog técnico — {title}"
        return "Artículo del blog técnico"

    if title:
        return f"Documento markdown — {title}"
    return "Documento markdown"


def _find_document_key(doc_name: str, docs: dict[str, str]) -> str | None:
    """Resolve a user-provided document name to an available document key."""
    requested = doc_name.strip().replace("\\", "/").removesuffix(".md").strip("/")
    if requested in docs:
        return requested

    # Preserve compatibility with previous root-level calls such as "fermax".
    legacy_root_key = requested.upper().replace(" ", "_")
    if legacy_root_key in docs:
        return legacy_root_key

    normalized_path = requested.lower().replace(" ", "-")
    for available in docs:
        if available.lower() == normalized_path:
            return available

    normalized_underscore = requested.upper().replace(" ", "_")
    for available in docs:
        if available.upper() == normalized_underscore:
            return available

    return None


def _normalize_route_path(value: object) -> str:
    """Normalize public portfolio paths for route matching."""
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
        path = path[:-10] or "/"

    if not path.startswith("/"):
        path = "/" + path

    while "//" in path:
        path = path.replace("//", "/")

    return path[:PAGE_CONTEXT_MAX_LENGTH]


def _normalize_page_context(page_context: dict | None) -> dict[str, str] | None:
    """Validate and normalize browser-provided page context."""
    if not isinstance(page_context, dict):
        return None

    path = _normalize_route_path(page_context.get("path"))
    title = page_context.get("title")
    title = title.strip()[:PAGE_CONTEXT_MAX_LENGTH] if isinstance(title, str) else ""

    if not path and not title:
        return None

    return {"path": path or "/", "title": title}


def _find_document_by_route(path: str) -> tuple[str, dict[str, object]] | None:
    """Find a document whose frontmatter route matches the provided path."""
    normalized_path = _normalize_route_path(path)
    if not normalized_path:
        return None

    docs = _load_all_documents()
    for doc_name, content in docs.items():
        metadata = _document_metadata(doc_name, content)
        route = _normalize_route_path(metadata.get("route"))
        if route and route == normalized_path:
            return doc_name, metadata

    return None


def build_page_context_hint(page_context: dict | None) -> str | None:
    """Build a backend-controlled context hint for the agent."""
    normalized = _normalize_page_context(page_context)
    if not normalized:
        return None

    route_match = _find_document_by_route(normalized["path"])
    lines = [
        "[Contexto de pagina validado por backend]",
        f"Ruta vista por el usuario: {normalized['path']}",
    ]

    if normalized["title"]:
        lines.append(f"Titulo de la pagina: {normalized['title']}")

    if route_match:
        doc_name, metadata = route_match
        lines.append(f"Documento RAG asociado por ruta: {doc_name}")
        if metadata.get("title"):
            lines.append(f"Titulo del documento asociado: {metadata['title']}")
        lines.append("Usa esta pista para priorizar herramientas/documentos, pero verifica la respuesta con RAG.")
    else:
        lines.append("No hay documento RAG asociado por ruta; trata esta pagina solo como contexto debil de navegacion.")

    return "\n".join(lines)


@tool
def list_documents() -> str:
    """List all available CV and blog documents with brief descriptions.
    Use this tool to discover what information is available before reading specific documents.

    Returns:
        A formatted list of document names and their descriptions.
    """
    docs = _load_all_documents()
    lines = []
    for doc_name, content in sorted(docs.items()):
        description = _describe_document(doc_name, content)
        metadata = _document_metadata(doc_name, content)
        route = metadata.get("route")
        route_suffix = f" | ruta: {route}" if route else ""
        lines.append(f"- **{doc_name}**: {description}{route_suffix}")

    return f"Documentos disponibles ({len(docs)}):\n" + "\n".join(lines)


@tool
def read_document(doc_name: str) -> str:
    """Read the full content of a specific CV or blog document.
    Use this tool when you need detailed information about a specific experience,
    education, section of the CV, or blog article.

    Args:
        doc_name: Name of the document to read (e.g., 'FERMAX', 'CV',
                  'RESUMEN_PROFESIONAL', or 'blog/nombre-del-articulo').
                  Use list_documents to see available names.

    Returns:
        The full markdown content of the document, or an error message if not found.
    """
    docs = _load_all_documents()
    resolved_key = _find_document_key(doc_name, docs)
    if resolved_key:
        content = docs[resolved_key]
        return f"[Documento: {resolved_key}]\n\n{content}"

    available = ", ".join(sorted(docs.keys()))
    return f"Documento '{doc_name}' no encontrado. Documentos disponibles: {available}"


@tool
def search_documents(query: str) -> str:
    """Search for relevant information across all CV and blog documents.
    Use this tool for general questions that might span multiple documents.
    Searches by keyword matching (case-insensitive) across both document content
    and document metadata/descriptions.

    IMPORTANT: The documents are written in SPANISH. Always search using Spanish
    keywords even if the user's question is in another language.
    For example, if asked about 'current job', search for 'actual presente Fermax'.

    Args:
        query: Search query in SPANISH — keywords or phrases to look for.
               Use company names, technologies, Spanish terms, or blog topics.

    Returns:
        Relevant sections from documents that match the query, with document attribution.
    """
    docs = _load_all_documents()
    if not docs:
        return "No hay documentos disponibles."

    terms = [t.strip().lower() for t in re.split(r"[\s,;]+", query) if len(t.strip()) > 2]
    if not terms:
        return "Proporciona términos de búsqueda más específicos (mínimo 3 caracteres)."

    results = []

    for doc_name, content in docs.items():
        metadata = _document_metadata(doc_name, content)
        searchable_parts = [
            content,
            _describe_document(doc_name, content),
            doc_name,
            str(metadata.get("title") or ""),
            str(metadata.get("route") or ""),
            " ".join(metadata.get("tags") or []),
        ]
        searchable = " ".join(searchable_parts).lower()

        matching_terms = [t for t in terms if t in searchable]
        if not matching_terms:
            continue

        sections = content.split("\n\n")
        relevant_sections = []

        for section in sections:
            section_lower = section.lower()
            if any(term in section_lower for term in matching_terms):
                cleaned = section.strip()
                if cleaned and len(cleaned) > 10:
                    relevant_sections.append(cleaned)

        if relevant_sections:
            truncated = relevant_sections[:5]
            result_text = f"\n📄 **{doc_name}** (matched: {', '.join(matching_terms)}):\n"
            result_text += "\n---\n".join(truncated)
            if len(relevant_sections) > 5:
                result_text += f"\n... (+{len(relevant_sections) - 5} secciones más. Usa read_document para ver todo.)"
            results.append((len(matching_terms), result_text))

    if not results:
        return f"No se encontraron resultados para: '{query}'. Intenta con otros términos o usa list_documents para ver los documentos disponibles."

    results.sort(key=lambda x: x[0], reverse=True)
    output = f"Resultados para '{query}':\n"
    output += "\n".join(r[1] for r in results)

    found_docs = {r[1].split("**")[1] for r in results if "**" in r[1]}
    hints = []
    for doc_name, content in docs.items():
        if doc_name not in found_docs:
            description = _describe_document(doc_name, content)
            desc_lower = description.lower()
            if any(term in desc_lower for term in terms):
                hints.append(f"  - {doc_name}: {description}")

    if hints:
        output += "\n\n💡 Otros documentos potencialmente relevantes (usa read_document para consultarlos):\n"
        output += "\n".join(hints)

    return output


def get_tools() -> list:
    """Return the list of tools available to the agent."""
    return [list_documents, read_document, search_documents]


def get_document_count() -> int:
    """Return the number of loaded documents."""
    return len(_load_all_documents())
