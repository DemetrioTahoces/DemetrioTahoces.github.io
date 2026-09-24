"""
Agent tools. The CV corpus already lives in the system prompt; the only tool
loads blog articles on demand.
"""

from langchain_core.tools import tool

from core.knowledge import get_knowledge_base


@tool
def read_blog_article(article: str) -> str:
    """Lee el contenido completo de un artículo del blog técnico de Demetrio.

    Úsala solo para artículos del blog, antes de responder sobre su contenido:
    el índice del blog en tus instrucciones trae únicamente título, fecha, URL
    y resumen. No la uses para el CV, la experiencia ni la formación: esos
    documentos ya están completos en tus instrucciones.

    Args:
        article: Nombre del artículo tal como aparece en el índice del blog,
            por ejemplo 'blog/solid-principios-diseno'.
    """
    kb = get_knowledge_base()
    doc = kb.get(article)
    if doc is not None and not doc.is_blog:
        return f"'{doc.name}' no es un artículo del blog: su contenido completo ya está en tus instrucciones."
    if doc is None:
        available = ", ".join(d.name for d in kb.blog_documents) or "ninguno"
        return f"No existe el artículo '{article}'. Artículos disponibles: {available}"
    # Sectioned like the CV in the system prompt, so blog content can be cited by section.
    return f'<articulo nombre="{doc.name}" titulo="{doc.title}" url="{doc.url}">\n{doc.render_sections()}\n</articulo>'


def get_tools() -> list:
    return [read_blog_article]
