"""
Generates /llms.txt (https://llmstxt.org) for the static site from the same
documents the chatbot uses, so both stay in sync.

    uv run python -m core.llms_txt      # rewrites ../../llms.txt
"""

from core.config import PROJECT_ROOT, settings
from core.knowledge import KnowledgeBase, get_knowledge_base

LLMS_TXT_PATH = PROJECT_ROOT.parent.parent / "llms.txt"
API_URL = "https://demetrio-tahoces-cv-chatbot.vercel.app"


def render_llms_txt(kb: KnowledgeBase | None = None) -> str:
    kb = kb or get_knowledge_base()
    site = settings.public_site_url

    def entries(docs):
        return [f"- [{d.title}]({d.url}): {d.summary}" for d in docs]

    experience = [d for d in kb.cv_documents if d.type == "cv"]
    education = [d for d in kb.cv_documents if d.type == "formacion"]
    lines = [
        "# Demetrio Tahoces",
        "",
        "> Software Engineer (backend, sistemas distribuidos, IoT e IA agéntica). CV, experiencia, "
        "formación y blog técnico. Contenido en castellano.",
        "",
        f"- Asistente conversacional del CV: {site}/CV/chatbot.html",
        f"- Servidor MCP de solo lectura (Streamable HTTP, sin autenticación): {API_URL}/api/mcp",
        "",
        "## CV y experiencia",
        *entries(experience),
        "",
        "## Formación",
        *entries(education),
        "",
        "## Blog técnico",
        *entries(kb.blog_documents),
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    LLMS_TXT_PATH.write_text(render_llms_txt(), encoding="utf-8")
    print(f"Escrito {LLMS_TXT_PATH}")
