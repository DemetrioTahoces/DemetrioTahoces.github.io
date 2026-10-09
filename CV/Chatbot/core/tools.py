"""
Agent tools. The knowledge base already travels with every request; the only
tool loads blog articles on demand, and only once the blog no longer fits in
the knowledge message (see KnowledgeBase.blog_inline).
"""

from langchain_core.tools import tool

from core.knowledge import get_knowledge_base


@tool
def read_blog_article(article: str) -> str | list[dict]:
    """Lee el contenido completo de un artículo del blog técnico de Demetrio.

    Úsala solo para artículos del blog, antes de responder sobre su contenido:
    el índice del blog en la base de conocimiento trae únicamente título, fecha,
    URL y resumen. No la uses para el CV, la experiencia ni la formación: esos
    documentos ya están completos en la base de conocimiento.

    Args:
        article: Nombre del artículo tal como aparece en el índice del blog,
            por ejemplo 'blog/solid-principios-diseno'.
    """
    kb = get_knowledge_base()
    doc = kb.get(article)
    if doc is not None and not doc.is_blog:
        return f"'{doc.name}' no es un artículo del blog: su contenido completo ya está en la base de conocimiento."
    if doc is None:
        available = ", ".join(d.name for d in kb.blog_documents) or "ninguno"
        return f"No existe el artículo '{article}'. Artículos disponibles: {available}"
    # One search_result per section, like the knowledge base, so the article is cited by section.
    return doc.search_results()


def get_tools() -> list:
    return [] if get_knowledge_base().blog_inline else [read_blog_article]
