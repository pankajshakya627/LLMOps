"""Exercise the pinned SDK with synthetic providers and intercepted export queues."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any
from unittest.mock import patch

os.environ["DD_INSTRUMENTATION_TELEMETRY_ENABLED"] = "false"
os.environ["DD_TRACE_ENABLED"] = "false"

from app.core.config import Settings
from app.core.telemetry import configure_telemetry

capture = sys.argv[1] == "true"
settings = Settings(
    _env_file=None,
    mongodb_uri="mongodb://unused",
    institution="NexaBank",
    jurisdiction="IN",
    confidentiality_level="internal",
    dd_llmobs_enabled=True,
    dd_api_key="synthetic-key",
    dd_capture_content=capture,
)
configure_telemetry(settings)

import httpx2
import pytest
from ddtrace.llmobs import LLMObs
from fastapi import HTTPException
from fastapi.testclient import TestClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from starlette.responses import StreamingResponse

from app.api import answer as answer_api
from app.core.config import get_settings
from app.core.http_monitoring import CAPTURE_LIMIT
from app.core.observability import prompt_annotation_context
from app.core.telemetry import correlate_answer
from app.main import create_app
from app.models.answer import AnswerResponse
from app.models.retrieval import RetrieveTimings

spans: list[dict[str, Any]] = []
export_patch = patch.object(
    LLMObs._instance._llmobs_span_writer, "enqueue", side_effect=spans.append
)
export_patch.start()


def respond(request):
    return httpx2.Response(
        200,
        json={
            "id": "offline",
            "object": "chat.completion",
            "created": 0,
            "model": "offline-candidate",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Contact learner@example.com"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 8, "completion_tokens": 3, "total_tokens": 11},
        },
    )


async def generate(request, _settings):
    async with httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport:
        model = ChatOpenAI(
            model="offline-candidate",
            api_key="synthetic",
            base_url="http://provider.invalid/v1",
            use_responses_api=False,
            http_async_client=transport,
        )
        prompt = ChatPromptTemplate.from_messages([("human", "{query}")])
        with prompt_annotation_context(
            prompt, {"query": request.query}, prompt_id="answer", version="test-1"
        ):
            await (prompt | model).ainvoke({"query": request.query})
    answer = AnswerResponse(
        as_of=request.as_of,
        status="insufficient_evidence",
        answer="No evidence.",
        citations=[],
        generation_ms=1,
        retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
    )
    correlate_answer(answer)
    return answer


app = create_app()
app.dependency_overrides[get_settings] = lambda: settings


@app.post("/probe/{item_id}")
async def probe(item_id: str, payload: dict):
    return payload


@app.get("/unavailable")
async def unavailable():
    raise HTTPException(503, "Synthetic outage")


@app.get("/broken")
async def broken():
    raise ValueError("learner@example.com Bearer SYNTHETIC_SECRET")


@app.get("/large")
async def large():
    async def chunks():
        yield b'{"result":"'
        yield b"x" * (CAPTURE_LIMIT + 1)
        yield b'"}'

    return StreamingResponse(chunks(), media_type="application/json")


with (
    patch("app.main.get_settings", return_value=settings),
    patch("app.main.token_encoder"),
    patch.object(answer_api, "answer_policy", generate),
    TestClient(app, raise_server_exceptions=False) as client,
):
    assert client.get("/health").status_code == 200
    response = client.post(
        "/answer", json={"query": "SYNTHETIC-PRIVATE-MARKER", "as_of": "2026-10-01"}
    )
    assert response.status_code == 200, response.text
    assert client.post("/answer", json={}).status_code == 422
    payload = {"query": "Contact learner@example.com", "api_key": "sk-SYNTHETIC_SECRET"}
    probe_response = client.post(
        "/probe/one?token=SECRET_QUERY",
        json=payload,
        headers={"Authorization": "Bearer SECRET_HEADER"},
    )
    assert probe_response.json() == payload
    assert client.get("/unknown/one").status_code == client.get("/unknown/two").status_code == 404
    assert client.get("/unavailable").status_code == 503
    assert client.get("/broken").status_code == 500
    large_response = client.get("/large")
    assert len(large_response.json()["result"]) == CAPTURE_LIMIT + 1
    routes = client.get("/metrics/http").json()["routes"]

identity = {
    "trace_id": response.headers["x-datadog-trace-id"],
    "span_id": response.headers["x-datadog-span-id"],
}
assert response.json()["datadog_trace_id"] == identity["trace_id"]
assert response.json()["datadog_span_id"] == identity["span_id"]
root = next(s for s in spans if s["span_id"] == identity["span_id"])
llm = next(s for s in spans if s["meta"]["span"]["kind"] == "llm")
assert root["trace_id"] == llm["trace_id"] == identity["trace_id"]
assert llm["metrics"]["input_tokens"] == 8 and llm["metrics"]["output_tokens"] == 3
assert llm["meta"]["input"]["prompt"]["version"] == "test-1"
assert ("SYNTHETIC-PRIVATE-MARKER" in json.dumps(spans)) is capture
for marker in ("learner@example.com", "SYNTHETIC_SECRET", "SECRET_QUERY", "SECRET_HEADER"):
    assert marker not in json.dumps(spans), (marker, spans)
assert any(
    s["status"] == "error" and s["meta"].get("metadata", {}).get("error_type") for s in spans
)
if capture:
    probe_span = next(
        s for s in spans if s["span_id"] == probe_response.headers["x-datadog-span-id"]
    )
    assert "[REDACTED_EMAIL]" in json.dumps(probe_span)
    assert "[REDACTED_SECRET]" in json.dumps(probe_span)
    assert "[OMITTED" not in json.dumps(probe_span)
assert next(r for r in routes if r["route"] == "__unmatched__")["requests"] == 2
assert next(r for r in routes if r["route"] == "/unavailable")["server_errors"] == 1
if capture:
    large_span = next(
        s for s in spans if s["span_id"] == large_response.headers["x-datadog-span-id"]
    )
    assert "value" not in large_span["meta"].get("output", {})
    assert any("nexa_output_capture:omitted: exceeds 64 KiB" in tag for tag in large_span["tags"])


async def check_concurrent_contexts():
    async def scoped(version):
        with (
            LLMObs.workflow(name="concurrent-context"),
            prompt_annotation_context(
                ChatPromptTemplate.from_messages([("human", "{query}")]),
                {"query": "isolated runtime value"},
                prompt_id="answer",
                version=version,
            ),
            LLMObs.llm(name=f"context-{version}", model_name="synthetic", model_provider="custom"),
        ):
            await asyncio.sleep(0)

    await asyncio.gather(scoped("v1"), scoped("v2"))
    with (
        pytest.raises(RuntimeError),
        LLMObs.workflow(name="failed-context"),
        prompt_annotation_context(
            ChatPromptTemplate.from_messages([("human", "{query}")]),
            {"query": "private"},
            prompt_id="judge",
            version="failed-version",
        ),
    ):
        raise RuntimeError("Synthetic expected failure")
    assert not LLMObs._instance._annotations


asyncio.run(check_concurrent_contexts())
for version in ("v1", "v2"):
    model_span = next(s for s in spans if s["name"] == f"context-{version}")
    assert model_span["meta"]["input"]["prompt"]["version"] == version

LLMObs.disable()
print("Datadog native SDK privacy/correlation checks passed")
