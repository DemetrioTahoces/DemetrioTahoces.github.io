"""
Document retrieval tools for the LangGraph agent.

Provides three tools that allow the agent to discover and read
the CV markdown documents stored in the docs/ directory.
"""

import os
import re
from pathlib import Path
from functools import lru_cache

from langchain_core.tools import tool

from core.config import settings


def _get_docs_dir() -> Path:
    """Resolve the absolute path to the docs directory."""
    # On Vercel, the working directory is the project root (CV/Chatbot/)
    # Locally, it depends on where uvicorn is started from
    base = Path(__file__).parent.parent
    return base / settings.docs_path


@lru_cache(maxsize=1)
def _load_all_documents() -> dict[str, str]:
    """
    Load all .md files from the docs directory into memory.
    Cached at module level — persists between Vercel invocations on warm starts.

    Returns:
        Dict mapping document name (without extension) to file content.
    """
    docs = {}
    docs_dir = _get_docs_dir()
    if not docs_dir.exists():
        return docs

    for md_file in sorted(docs_dir.glob("*.md")):
        doc_name = md_file.stem
        docs[doc_name] = md_file.read_text(encoding="utf-8")

    return docs


# Brief descriptions for each known document (helps the agent decide which to read)
_DOC_DESCRIPTIONS = {
    "CV": "Currículum completo — resumen, experiencia, formación, competencias técnicas e idiomas",
    "RESUMEN_PROFESIONAL": "Resumen extendido — pilares de valor, evolución técnica, filosofía de trabajo",
    "FERMAX": "Experiencia ACTUAL en Fermax — Software Engineer, IoT, DDD, Kubernetes (01/2025-Presente). Trabajo actual.",
    "OPENDIT": "Experiencia en Opendit — Backend Engineer, DAPR, BFF, CQRS (2022-2024)",
    "INDITEX": "Experiencia en Inditex (Nunegal) — Ingeniero de Datos, Kafka, Snowflake (2021-2022)",
    "SECURITAS_DIRECT": "Experiencia en Securitas Direct (Vector ITC) — Procesado de señales (2021)",
    "ALISYS": "Experiencia en Alisys — Robótica, IA, Android, VoIP (2019-2021)",
    "IMAGINE800": "Experiencia en Imagine800 — Apps Android, VoIP, Asterisk (2019)",
    "GRADO_TELECOMUNICACION": "Grado en Ingeniería de Telecomunicación — Universidad de Oviedo (2012-2017)",
    "MASTER_TELECOMUNICACION": "Máster en Ingeniería de Telecomunicación — VoIP, Android (2017-2019)",
    "MASTER_IA_APLICADA": "Máster en IA Aplicada y Optimización de Procesos — RAG, Agentes (2026)",
}


@tool
def list_documents() -> str:
    """List all available CV documents with brief descriptions.
    Use this tool to discover what information is available before reading specific documents.

    Returns:
        A formatted list of document names and their descriptions.
    """
    docs = _load_all_documents()
    lines = []
    for doc_name in sorted(docs.keys()):
        description = _DOC_DESCRIPTIONS.get(doc_name, "Documento del CV")
        lines.append(f"- **{doc_name}**: {description}")

    return f"Documentos disponibles ({len(docs)}):\n" + "\n".join(lines)


@tool
def read_document(doc_name: str) -> str:
    """Read the full content of a specific CV document.
    Use this tool when you need detailed information about a specific experience,
    education, or section of the CV.

    Args:
        doc_name: Name of the document to read (e.g., 'FERMAX', 'CV', 'RESUMEN_PROFESIONAL').
                  Use list_documents to see available names.

    Returns:
        The full markdown content of the document, or an error message if not found.
    """
    docs = _load_all_documents()

    # Try exact match first
    if doc_name in docs:
        content = docs[doc_name]
        return f"[Documento: {doc_name}]\n\n{content}"

    # Try case-insensitive match
    doc_name_upper = doc_name.upper().replace(" ", "_")
    if doc_name_upper in docs:
        content = docs[doc_name_upper]
        return f"[Documento: {doc_name_upper}]\n\n{content}"

    available = ", ".join(sorted(docs.keys()))
    return f"Documento '{doc_name}' no encontrado. Documentos disponibles: {available}"


@tool
def search_documents(query: str) -> str:
    """Search for relevant information across all CV documents.
    Use this tool for general questions that might span multiple documents.
    Searches by keyword matching (case-insensitive) across both document content
    and document metadata/descriptions.

    IMPORTANT: The documents are written in SPANISH. Always search using Spanish
    keywords even if the user's question is in another language.
    For example, if asked about 'current job', search for 'actual presente Fermax'.

    Args:
        query: Search query in SPANISH — keywords or phrases to look for.
               Use company names, technologies, or Spanish terms.

    Returns:
        Relevant sections from documents that match the query, with document attribution.
    """
    docs = _load_all_documents()
    if not docs:
        return "No hay documentos disponibles."

    # Split query into individual search terms
    terms = [t.strip().lower() for t in re.split(r"[\s,;]+", query) if len(t.strip()) > 2]
    if not terms:
        return "Proporciona términos de búsqueda más específicos (mínimo 3 caracteres)."

    results = []

    for doc_name, content in docs.items():
        content_lower = content.lower()
        # Also search in document descriptions for better metadata matching
        description = _DOC_DESCRIPTIONS.get(doc_name, "").lower()
        searchable = content_lower + " " + description + " " + doc_name.lower()

        # Check which terms match this document (content + metadata)
        matching_terms = [t for t in terms if t in searchable]
        if not matching_terms:
            continue

        # Extract relevant sections (paragraphs containing the terms)
        sections = content.split("\n\n")
        relevant_sections = []

        for section in sections:
            section_lower = section.lower()
            if any(term in section_lower for term in matching_terms):
                # Clean up the section
                cleaned = section.strip()
                if cleaned and len(cleaned) > 10:
                    relevant_sections.append(cleaned)

        if relevant_sections:
            # Limit sections per document to avoid overwhelming the context
            truncated = relevant_sections[:5]
            result_text = f"\n📄 **{doc_name}** (matched: {', '.join(matching_terms)}):\n"
            result_text += "\n---\n".join(truncated)
            if len(relevant_sections) > 5:
                result_text += f"\n... (+{len(relevant_sections) - 5} secciones más. Usa read_document para ver todo.)"
            results.append((len(matching_terms), result_text))

    if not results:
        return f"No se encontraron resultados para: '{query}'. Intenta con otros términos o usa list_documents para ver los documentos disponibles."

    # Sort by relevance (number of matching terms)
    results.sort(key=lambda x: x[0], reverse=True)
    output = f"Resultados para '{query}':\n"
    output += "\n".join(r[1] for r in results)

    # Add hints about potentially relevant documents not yet in results
    found_docs = {r[1].split("**")[1] for r in results if "**" in r[1]}
    hints = []
    for doc_name, description in _DOC_DESCRIPTIONS.items():
        if doc_name not in found_docs:
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
