"""
Optional LangSmith tracing and user feedback.

Disabled unless LANGSMITH_TRACING=true and LANGSMITH_API_KEY are set. Each chat
request uses its request_id as the LangSmith run_id, so logs, traces and
thumbs up/down feedback share one identifier.
"""

import logging
import os
import uuid

from core.config import settings

logger = logging.getLogger("cv_chatbot.tracing")


def tracing_enabled() -> bool:
    return settings.langsmith_tracing and bool(settings.langsmith_api_key)


def configure_tracing() -> None:
    """Export LangSmith settings for LangChain (which reads them from os.environ)."""
    if not tracing_enabled():
        return
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    # Serverless: send traces before the response finishes instead of in a
    # background thread that may be frozen once the function returns.
    os.environ["LANGCHAIN_CALLBACKS_BACKGROUND"] = "false"


def run_config(request_id: str, endpoint: str) -> dict:
    return {
        "run_id": uuid.UUID(request_id),
        "run_name": "cv-chat",
        "tags": [endpoint],
        "metadata": {"model": settings.model_name},
    }


def send_feedback(request_id: str, score: int, comment: str | None) -> None:
    """Attach thumbs up/down to the LangSmith run (no-op when tracing is off)."""
    if not tracing_enabled():
        return
    try:
        from langsmith import Client

        Client(api_key=settings.langsmith_api_key).create_feedback(
            run_id=request_id, key="user_rating", score=score, comment=comment
        )
    except Exception as e:  # feedback must never break the endpoint
        logger.warning("LangSmith feedback failed: %s", type(e).__name__)
