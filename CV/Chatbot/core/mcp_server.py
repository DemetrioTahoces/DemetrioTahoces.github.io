"""
Read-only MCP server exposing the CV knowledge base at /api/mcp.

Lets other agents (Claude, ChatGPT, IDE assistants...) query Demetrio's CV
directly. Tools only return documents: no LLM calls, so no token cost.
"""

from mcp.server import MCPServer
from mcp.server.caching import CacheHint
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import Icon, ToolAnnotations

from core.config import settings
from core.knowledge import Document, get_knowledge_base
from core.search import get_section_index, tokenize

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
SEARCH_MAX_RESULTS = 10
# Same "DT" badge as the site favicon.
ICON = Icon(
    src=(
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' "
        "height='32' rx='6' fill='%231e40af'/%3E%3Ctext x='16' y='22' text-anchor='middle' fill='white' "
        "font-family='Inter,sans-serif' font-weight='700' font-size='13'%3EDT%3C/text%3E%3C/svg%3E"
    ),
    mime_type="image/svg+xml",
    sizes=["any"],
)
# The content only changes with a deploy: clients and shared caches may reuse
# lists, discovery and resources for an hour instead of re-fetching them.
CACHE_HINT = CacheHint(ttl_ms=3_600_000, scope="public")

mcp_server = MCPServer(
    name="demetrio-tahoces-cv",
    title="CV de Demetrio Tahoces",
    description="CV, experiencia, formación y blog técnico de Demetrio Tahoces, Software Engineer.",
    instructions=(
        "Fuente oficial sobre el perfil profesional de Demetrio Tahoces. Para preguntas concretas usa search, "
        "que devuelve las secciones relevantes con su URL; para leer un documento entero o una sección, "
        "get_document; list_documents da el índice. Cita las URLs de las secciones. El contenido está en castellano."
    ),
    website_url=settings.public_site_url,
    icons=[ICON],
    version="2.1.0",
    cache_hints={
        method: CACHE_HINT
        for method in (
            "server/discover", "tools/list", "prompts/list",
            "resources/list", "resources/templates/list", "resources/read",
        )
    },
)

# The SDK always serves `subscriptions/listen` (2026-07-28): its response is a
# stream left open for list-changed events. The tools are static and the
# in-memory bus does not span serverless instances, so no event ever arrives
# and on Vercel each listen hangs until the 300 s timeout, then the client
# re-listens. Without the handler the server stops advertising listChanged and
# clients do not open it. There is no public API to unregister a handler.
mcp_server._lowlevel_server._request_handlers.pop("subscriptions/listen", None)


def _render(doc: Document) -> str:
    sections = "\n".join(f"- {s.title}: {doc.section_url(s)}" for s in doc.sections)
    return f"# {doc.title}\nURL: {doc.url}\n\n{doc.body}\n\n## URLs de las secciones\n{sections}"


def _find_section(doc: Document, requested: str):
    """Match a section by anchor or by title, ignoring case and accents."""
    wanted = tokenize(requested)
    for section in doc.sections:
        if requested.strip().lstrip("#").lower() == section.anchor.lower() or tokenize(section.title) == wanted:
            return section
    return None


@mcp_server.tool(annotations=READ_ONLY)
def search(query: str, limit: int = 5) -> list[dict]:
    """Busca en el CV, la experiencia, la formación y el blog de Demetrio y devuelve las secciones más relevantes
    (documento, sección, URL para citar y extracto). Úsala primero para preguntas concretas. Es una búsqueda por
    palabras clave sobre texto en castellano: usa términos en castellano o nombres de tecnologías, p. ej. 'Kafka',
    'IoT sensores' o 'máster IA'. Si un extracto viene truncado, lee la sección con get_document."""
    hits = get_section_index().search(query, max(1, min(limit, SEARCH_MAX_RESULTS)))
    return [hit.as_dict() for hit in hits]


@mcp_server.tool(annotations=READ_ONLY)
def list_documents() -> list[dict]:
    """Lista los documentos disponibles (CV, experiencias, formación y artículos del blog) con su resumen y URL pública."""
    kb = get_knowledge_base()
    return [
        {"name": d.name, "type": d.type, "title": d.title, "summary": d.summary, "url": d.url, "date": d.date}
        for d in kb.cv_documents + kb.blog_documents
    ]


@mcp_server.tool(annotations=READ_ONLY)
def get_document(name: str, section: str | None = None) -> str:
    """Devuelve el contenido Markdown de un documento, seguido de la URL de cada sección para citarla. `name` es el
    campo name de list_documents o el campo document de search, p. ej. 'FERMAX' o 'CV'. Con `section` (título o
    ancla de una sección, p. ej. 'contexto') devuelve solo esa sección."""
    doc = get_knowledge_base().get(name)
    if doc is None:
        raise ToolError(f"Documento '{name}' no encontrado. Usa list_documents o search para ver los nombres válidos.")
    if not section:
        return _render(doc)
    match = _find_section(doc, section)
    if match is None:
        valid = ", ".join(f"'{s.title}'" for s in doc.sections)
        raise ToolError(f"'{doc.name}' no tiene la sección '{section}'. Secciones: {valid}")
    return f"# {doc.title}: {match.title}\nURL: {doc.section_url(match)}\n\n{match.content}"


def _reader(doc: Document):
    def read() -> str:
        return _render(doc)

    return read


def _register_resources() -> None:
    """Every document as a Markdown resource (cv://documents/<name>), to attach it from the client."""
    kb = get_knowledge_base()
    for doc in kb.cv_documents + kb.blog_documents:
        mcp_server.resource(
            f"cv://documents/{doc.name}",
            name=doc.name,
            title=doc.title,
            description=doc.summary or None,
            mime_type="text/markdown",
        )(_reader(doc))


_register_resources()


@mcp_server.prompt(
    title="Evaluar encaje con una oferta",
    description="Contrasta una oferta o descripción de puesto con el perfil documentado de Demetrio, citando evidencias.",
)
def evaluar_encaje(oferta: str) -> str:
    return (
        "Evalúa el encaje de Demetrio Tahoces con la oferta de abajo usando solo el servidor MCP "
        "demetrio-tahoces-cv (search y get_document); no uses conocimiento general sobre él.\n"
        "- Para cada requisito relevante, busca evidencias y di si se cumple, se cumple en parte o no consta.\n"
        "- Atribuye cada tecnología o logro a la empresa, proyecto o formación donde aparece y cita la URL "
        "de la sección que lo respalda.\n"
        "- Señala los huecos con honestidad y la experiencia transferible; no exageres ni extrapoles.\n"
        "- Termina con una valoración breve. Responde en el idioma de la oferta.\n\n"
        f"Oferta:\n{oferta}"
    )


@mcp_server.prompt(
    title="Presentar el perfil",
    description="Resumen breve del perfil de Demetrio, opcionalmente orientado a un rol.",
)
def presentar_perfil(rol: str = "") -> str:
    focus = f" orientado al rol «{rol}»" if rol.strip() else ""
    return (
        f"Presenta en 5-8 frases el perfil profesional de Demetrio Tahoces{focus}, usando solo el servidor MCP "
        "demetrio-tahoces-cv (empieza por get_document con name 'CV' y usa search para concretar). "
        "Incluye puesto actual, años de experiencia, tecnologías principales y uno o dos logros concretos, "
        "cada dato con la URL de la sección que lo respalda. No inventes nada que no conste."
    )


# Stateless Streamable HTTP (MCP spec 2026-07-28): any serverless instance can
# answer any request. host != localhost so the SDK does not enable its
# localhost-only DNS-rebinding allowlist, which would reject the public domain.
mcp_http_app = mcp_server.streamable_http_app(
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
)
