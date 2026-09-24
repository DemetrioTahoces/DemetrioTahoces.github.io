"""
FastAPI application — Vercel entry point.

Endpoints:
    POST /api/chat        — Full response (JSON)
    POST /api/chat/stream — Streaming response (SSE)
    POST /api/feedback    — Thumbs up/down for an answer
    GET  /api/health      — Health check
    POST /api/mcp         — Read-only MCP server (Streamable HTTP, stateless)
"""

import asyncio
import json
import sys
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, Field
from slowapi.errors import RateLimitExceeded

# Ensure project root is in sys.path for imports on Vercel
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.agent import create_agent_graph, invoke_agent, stream_agent
from core.config import settings
from core.knowledge import get_knowledge_base, normalize_route_path
from core.mcp_server import mcp_http_app, mcp_server
from core.tracing import configure_tracing, run_config, send_feedback
from middleware.abuse_guard import blocked_response, client_ip, create_abuse_guard
from middleware.rate_limiter import get_rate_limit_string, limiter, rate_limit_exceeded_handler
from middleware.request_logger import log_error, log_request, log_response, setup_logging

logger = setup_logging()
configure_tracing()
abuse_guard = create_abuse_guard()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # The MCP transport needs its session manager task group running.
    async with mcp_server.session_manager.run():
        yield


app = FastAPI(
    title="CV Chatbot API — Demetrio Tahoces",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "invalid_request", "message": "La petición no es válida."},
    )


# Agent graph (lazy init — created on first request, reused on warm instances)
_agent_graph = None


def _get_agent():
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = create_agent_graph()
    return _agent_graph


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class PageContext(BaseModel):
    path: str | None = Field(default=None, max_length=220)
    # Accepted for backwards compatibility; never forwarded to the model.
    title: str | None = Field(default=None, max_length=220)


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=40)
    # Only used to correlate logs; conversation state travels in `history`.
    session_id: str | None = Field(default=None, max_length=64)
    page_context: PageContext | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    request_id: str
    usage: dict[str, int]
    duration_ms: float


class FeedbackRequest(BaseModel):
    request_id: str = Field(..., pattern=r"^[0-9a-f]{32}$")
    rating: Literal["up", "down"]
    comment: str | None = Field(default=None, max_length=500)


def _prepare(request: Request, body: ChatRequest, endpoint: str) -> tuple[str, str, list[dict], dict | None]:
    request_id = uuid.uuid4().hex
    session_id = body.session_id or uuid.uuid4().hex[:12]
    history = [turn.model_dump() for turn in body.history]
    page_context = body.page_context.model_dump(exclude_none=True) if body.page_context else None
    log_request(
        logger,
        request_id=request_id,
        ip=client_ip(request),
        endpoint=endpoint,
        message_chars=len(body.message),
        history_messages=len(history),
        page_route=normalize_route_path(page_context.get("path")) if page_context else None,
    )
    return request_id, session_id, history, page_context


def _internal_error(request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Ha ocurrido un error procesando tu pregunta. Inténtalo de nuevo.",
            "request_id": request_id,
        },
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "model": settings.model_name,
        "docs_loaded": len(get_knowledge_base().documents),
    }


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit(get_rate_limit_string())
async def chat(request: Request, body: ChatRequest):
    start = time.perf_counter()
    ip = client_ip(request)
    if retry_after := await abuse_guard.retry_after(ip):
        return blocked_response(retry_after)
    request_id, session_id, history, page_context = _prepare(request, body, "/api/chat")
    # The classifier runs alongside the agent; awaited before returning because
    # Vercel may freeze the instance once the response is sent.
    inspection = asyncio.create_task(abuse_guard.inspect(ip, body.message, request_id))
    try:
        result = await invoke_agent(
            _get_agent(), body.message, history, page_context, config=run_config(request_id, "/api/chat")
        )
    except Exception as e:
        log_error(logger, request_id=request_id, error=e, duration_ms=(time.perf_counter() - start) * 1000)
        return _internal_error(request_id)
    finally:
        await inspection

    duration_ms = (time.perf_counter() - start) * 1000
    log_response(logger, request_id=request_id, status_code=200, duration_ms=duration_ms, usage=result["usage"])
    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        request_id=request_id,
        usage=result["usage"],
        duration_ms=round(duration_ms, 2),
    )


@app.post("/api/chat/stream")
@limiter.limit(get_rate_limit_string())
async def chat_stream(request: Request, body: ChatRequest):
    start = time.perf_counter()
    ip = client_ip(request)
    if retry_after := await abuse_guard.retry_after(ip):
        return blocked_response(retry_after)
    request_id, session_id, history, page_context = _prepare(request, body, "/api/chat/stream")

    async def event_generator():
        inspection = asyncio.create_task(abuse_guard.inspect(ip, body.message, request_id))
        try:
            yield _sse_event({"type": "session", "session_id": session_id, "request_id": request_id})
            config = run_config(request_id, "/api/chat/stream")
            async for event in stream_agent(_get_agent(), body.message, history, page_context, config=config):
                yield _sse_event(event)
                if event["type"] == "done":
                    log_response(
                        logger,
                        request_id=request_id,
                        status_code=200,
                        duration_ms=(time.perf_counter() - start) * 1000,
                        usage=event.get("usage"),
                    )
        except Exception as e:
            log_error(logger, request_id=request_id, error=e, duration_ms=(time.perf_counter() - start) * 1000)
            yield _sse_event({"type": "error", "message": "Ha ocurrido un error procesando tu pregunta."})
        finally:
            await inspection

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Request-ID": request_id,
        },
    )


@app.post("/api/feedback", status_code=204)
@limiter.limit(get_rate_limit_string())
async def feedback(request: Request, body: FeedbackRequest):
    """Thumbs up/down: always logged; also sent to LangSmith when tracing is on."""
    logger.info(
        "Feedback received",
        extra={"request_id": body.request_id, "rating": body.rating, "has_comment": bool(body.comment)},
    )
    await run_in_threadpool(send_feedback, body.request_id, 1 if body.rating == "up" else 0, body.comment)
    return Response(status_code=204)


def _sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# Read-only MCP server at /api/mcp. Mounted last so the API routes above win.
app.mount("/api", mcp_http_app)
