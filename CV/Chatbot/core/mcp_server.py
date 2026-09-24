"""
Read-only MCP server exposing the CV knowledge base at /api/mcp.

Lets other agents (Claude, ChatGPT, IDE assistants...) query Demetrio's CV
directly. Tools only return documents: no LLM calls, so no token cost.
"""

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from core.config import settings
from core.knowledge import get_knowledge_base

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

mcp_server = MCPServer(
    name="demetrio-tahoces-cv",
    title="CV de Demetrio Tahoces",
    description="CV, experiencia, formación y blog técnico de Demetrio Tahoces, Software Engineer.",
    instructions=(
        "Fuente oficial sobre el perfil profesional de Demetrio Tahoces. Empieza por list_documents "
        "y lee con get_document los documentos que necesites. El contenido está en castellano."
    ),
    website_url=settings.public_site_url,
    version="2.0.0",
)


@mcp_server.tool(annotations=READ_ONLY)
def list_documents() -> list[dict]:
    """Lista los documentos disponibles (CV, experiencias, formación y artículos del blog) con su resumen y URL pública."""
    kb = get_knowledge_base()
    return [
        {"name": d.name, "type": d.type, "title": d.title, "summary": d.summary, "url": d.url, "date": d.date}
        for d in kb.cv_documents + kb.blog_documents
    ]


@mcp_server.tool(annotations=READ_ONLY)
def get_document(name: str) -> str:
    """Devuelve el contenido Markdown de un documento, seguido de la URL de cada sección para citarla. `name` es el campo name de list_documents, p. ej. 'FERMAX' o 'CV'."""
    doc = get_knowledge_base().get(name)
    if doc is None:
        raise ValueError(f"Documento '{name}' no encontrado. Usa list_documents para ver los nombres válidos.")
    sections = "\n".join(f"- {s.title}: {doc.section_url(s)}" for s in doc.sections)
    return f"# {doc.title}\nURL: {doc.url}\n\n{doc.body}\n\n## URLs de las secciones\n{sections}"


# Stateless Streamable HTTP (MCP spec 2026-07-28): any serverless instance can
# answer any request. host != localhost so the SDK does not enable its
# localhost-only DNS-rebinding allowlist, which would reject the public domain.
mcp_http_app = mcp_server.streamable_http_app(
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
)
