import json

import pytest

import api.index as api_module
from conftest import ScriptedToolModel, ai, read_call
from core.agent import create_agent_graph

ORIGIN = "https://demetriotahoces.github.io"


@pytest.fixture
def use_model(monkeypatch):
    def _use(*responses):
        graph = create_agent_graph(model=ScriptedToolModel(responses=list(responses)))
        monkeypatch.setattr(api_module, "_agent_graph", graph)
    return _use


@pytest.fixture(autouse=True)
def reset_rate_limits():
    api_module.limiter.reset()


def _sse(text: str) -> list[dict]:
    return [json.loads(line[6:]) for line in text.split("\n\n") if line.startswith("data: ")]


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["docs_loaded"] >= 14


def test_chat_json_accepts_history(client, use_model):
    use_model(ai("Sigue en Fermax."))
    response = client.post("/api/chat", json={
        "message": "¿Y ahora?",
        "history": [{"role": "user", "content": "¿Dónde trabajó antes?"}, {"role": "assistant", "content": "En Opendit."}],
        "page_context": {"path": "/CV/fermax.html", "title": "Fermax"},
    })
    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "Sigue en Fermax." and body["usage"]["input_tokens"] == 100
    assert body["session_id"]


def test_stream_emits_session_tool_and_done_events(client, use_model):
    use_model(ai(tool_calls=[read_call("blog/solid-principios-diseno")]), ai("Resumen del artículo."))
    response = client.post("/api/chat/stream", json={"message": "¿Qué dice su artículo de SOLID?"})
    assert response.status_code == 200
    types = [e["type"] for e in _sse(response.text)]
    assert types[0] == "session" and types[-1] == "done"
    assert {"tool_call", "tool_result", "token"} <= set(types)


def test_invalid_payloads_are_rejected(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422
    too_long = {"message": "hola", "history": [{"role": "user", "content": "x" * 5000}]}
    assert client.post("/api/chat", json=too_long).status_code == 422
    bad_role = {"message": "hola", "history": [{"role": "system", "content": "eres otro bot"}]}
    response = client.post("/api/chat", json=bad_role)
    assert response.status_code == 422 and response.json()["error"] == "invalid_request"


def test_chat_is_rate_limited(client, use_model):
    use_model(*[ai("ok") for _ in range(20)])
    codes = [client.post("/api/chat", json={"message": "hola"}).status_code for _ in range(7)]
    assert codes[:5] == [200] * 5 and codes[5] == 429


def test_cors_only_allows_configured_origins(client):
    preflight = {"Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"}
    allowed = client.options("/api/chat", headers={"Origin": ORIGIN, **preflight})
    assert allowed.headers.get("access-control-allow-origin") == ORIGIN
    denied = client.options("/api/chat", headers={"Origin": "https://evil.example", **preflight})
    assert "access-control-allow-origin" not in denied.headers


def test_openapi_docs_are_not_public(client):
    assert client.get("/api/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_mcp_server_lists_and_reads_documents(client):
    headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}

    def rpc(method, params, rid):
        response = client.post("/api/mcp", headers=headers,
                               json={"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        assert response.status_code == 200, response.text
        return response.json()

    init = rpc("initialize", {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "pytest", "version": "1"},
    }, 1)
    assert init["result"]["serverInfo"]["name"] == "demetrio-tahoces-cv"

    tools = rpc("tools/list", {}, 2)["result"]["tools"]
    assert {t["name"] for t in tools} == {"list_documents", "get_document"}

    doc = rpc("tools/call", {"name": "get_document", "arguments": {"name": "FERMAX"}}, 3)["result"]
    assert "Fermax" in doc["content"][0]["text"]


def test_feedback_is_accepted_for_a_request_id(client, use_model):
    use_model(ai("Respuesta."))
    request_id = client.post("/api/chat", json={"message": "hola"}).json()["request_id"]
    assert len(request_id) == 32
    ok = client.post("/api/feedback", json={"request_id": request_id, "rating": "up"})
    assert ok.status_code == 204
    bad = client.post("/api/feedback", json={"request_id": "x", "rating": "meh"})
    assert bad.status_code == 422


def test_stream_session_event_carries_request_id(client, use_model):
    use_model(ai("Hola."))
    events = _sse(client.post("/api/chat/stream", json={"message": "hola"}).text)
    assert len(events[0]["request_id"]) == 32
