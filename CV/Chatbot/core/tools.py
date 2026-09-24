"""
Agent tools. The CV corpus already lives in the system prompt; the only tool
loads blog articles (or any document) on demand.
"""

from langchain_core.tools import tool

from core.knowledge import get_knowledge_base


@tool
def read_document(doc_name: str) -> str:
    """Lee la ficha completa de un artículo del blog técnico de Demetrio.

    Úsala antes de responder sobre el contenido de un artículo: el índice del
    blog en tus instrucciones solo trae título, fecha, URL y resumen.

    Args:
        doc_name: Nombre del artículo tal como aparece en el índice del blog,
            por ejemplo 'blog/solid-principios-diseno'.
    """
    kb = get_knowledge_base()
    doc = kb.get(doc_name)
    if doc is None:
        available = ", ".join(d.name for d in kb.blog_documents) or "ninguno"
        return f"No existe el documento '{doc_name}'. Artículos disponibles: {available}"
    return f"[Documento: {doc.name} | {doc.title} | {doc.url}]\n\n{doc.body}"


def get_tools() -> list:
    return [read_document]
