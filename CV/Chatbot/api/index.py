"""
FastAPI application — Vercel serverless entry point.

Endpoints:
    POST /api/chat        — Full response (JSON)
    POST /api/chat/stream — Streaming response (SSE)
    GET  /api/health      — Health check
"""

import json
import time
import uuid
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Ensure project root is in sys.path for imports on Vercel
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.config import settings
from core.agent import create_agent_graph, invoke_agent, stream_agent
from core.tools import get_document_count
from middleware.rate_limiter import limiter, rate_limit_exceeded_handler, get_rate_limit_string
from middleware.request_logger import (
    setup_logging,
    log_request,
    log_response,
    log_error,
)

# ---------------------------------------------------------------------------
# App initialization
# ---------------------------------------------------------------------------

app = FastAPI(
    title="CV Chatbot API — Demetrio Tahoces",
    description="Asistente virtual del CV profesional de Demetrio Tahoces.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Logging
logger = setup_logging()

# Agent graph (lazy init — created on first request, reused on warm instances)
_agent_graph = None


def _get_agent():
    """Get or create the agent graph (singleton per Vercel instance)."""
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = create_agent_graph()
    return _agent_graph


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question about the CV.",
    )
    session_id: str | None = Field(
        default=None,
        description="Optional session ID for conversation continuity.",
    )


class ChatResponse(BaseModel):
    response: str
    session_id: str
    usage: dict
    duration_ms: float


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health")
@limiter.limit(get_rate_limit_string())
async def health_check(request: Request):
    """Health check endpoint — verifies the service is running."""
    return {
        "status": "ok",
        "model": settings.model_name,
        "docs_loaded": get_document_count(),
    }


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit(get_rate_limit_string())
async def chat(request: Request, body: ChatRequest):
    """
    Process a chat message and return the full response.
    Rate limited to prevent abuse.
    """
    request_id = str(uuid.uuid4())[:8]
    session_id = body.session_id or str(uuid.uuid4())[:12]
    start_time = time.time()

    # Log incoming request
    client_ip = request.client.host if request.client else "unknown"
    log_request(
        logger,
        request_id=request_id,
        ip=client_ip,
        endpoint="/api/chat",
        method="POST",
        session_id=session_id,
        user_message=body.message,
    )

    try:
        graph = _get_agent()
        result = await invoke_agent(graph, body.message, session_id)
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        log_response(
            logger,
            request_id=request_id,
            status_code=200,
            duration_ms=duration_ms,
            usage=result.get("usage"),
        )

        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            usage=result.get("usage", {}),
            duration_ms=round(duration_ms, 2),
        )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_error(logger, request_id=request_id, error=e, duration_ms=duration_ms)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "Ha ocurrido un error procesando tu pregunta. Inténtalo de nuevo.",
                "request_id": request_id,
            },
        )


@app.post("/api/chat/stream")
@limiter.limit(get_rate_limit_string())
async def chat_stream(request: Request, body: ChatRequest):
    """
    Process a chat message and stream the response token by token via SSE.
    """
    request_id = str(uuid.uuid4())[:8]
    session_id = body.session_id or str(uuid.uuid4())[:12]
    start_time = time.time()

    # Log incoming request
    client_ip = request.client.host if request.client else "unknown"
    log_request(
        logger,
        request_id=request_id,
        ip=client_ip,
        endpoint="/api/chat/stream",
        method="POST",
        session_id=session_id,
        user_message=body.message,
    )

    async def event_generator():
        try:
            graph = _get_agent()

            # Send session_id as first event
            yield _sse_event({"type": "session", "session_id": session_id})

            async for event in stream_agent(graph, body.message, session_id):
                yield _sse_event(event)

                # Log final usage on completion
                if event.get("type") == "done":
                    duration_ms = (time.time() - start_time) * 1000
                    log_response(
                        logger,
                        request_id=request_id,
                        status_code=200,
                        duration_ms=duration_ms,
                        usage=event.get("usage"),
                    )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_error(logger, request_id=request_id, error=e, duration_ms=duration_ms)
            yield _sse_event({
                "type": "error",
                "message": "Ha ocurrido un error procesando tu pregunta.",
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Request-ID": request_id,
        },
    )


def _sse_event(data: dict) -> str:
    """Format a dict as an SSE event string."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
