from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import Mock

import pytest
import structlog
from fastapi.testclient import TestClient
from openinference.instrumentation import get_attributes_from_context
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from app.api import answer as answer_api
from app.chains.prompts.answer import ANSWER_PROMPT, ANSWER_PROMPT_VERSION
from app.chains.prompts.judge import JUDGE_PROMPT, JUDGE_VERSION
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.observability import prompt_annotation_context
from app.core.phoenix import capture_request, correlate_answer, correlate_response
from app.main import create_app
from app.models.answer import AnswerResponse
from app.models.retrieval import RetrieveRequest, RetrieveTimings


def test_json_logs_use_the_current_trace_without_leaking_context(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("INFO")
    with trace.use_span(trace.NonRecordingSpan(trace.SpanContext(1, 2, False))):
        structlog.get_logger().info("correlated_log")
    structlog.get_logger().info("outside")
    inside, outside = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert inside["trace_id"] == f"{1:032x}"
    assert inside["span_id"] == f"{2:016x}"
    assert "trace_id" not in outside and "span_id" not in outside


def test_versioned_prompt_context_is_isolated_between_concurrent_requests_and_failures() -> None:
    async def answer(query: str) -> dict[str, Any]:
        with prompt_annotation_context(
            ANSWER_PROMPT, {"query": query}, prompt_id="answer", version=ANSWER_PROMPT_VERSION
        ):
            await asyncio.sleep(0)
            return dict(get_attributes_from_context())

    async def run() -> list[dict[str, Any]]:
        rows = await asyncio.gather(answer("first"), answer("second"))
        with (
            pytest.raises(RuntimeError),
            prompt_annotation_context(
                JUDGE_PROMPT, {"record": "private"}, prompt_id="judge", version=JUDGE_VERSION
            ),
        ):
            raise RuntimeError("judge failed")
        assert not dict(get_attributes_from_context())
        return rows

    rows = asyncio.run(run())
    assert [json.loads(row["llm.prompt_template.variables"])["query"] for row in rows] == [
        "first",
        "second",
    ]
    assert all(row["llm.prompt_template.version"] == ANSWER_PROMPT_VERSION for row in rows)
    assert all("first" not in row["llm.prompt_template.template"] for row in rows)
    assert not dict(get_attributes_from_context())


def test_prompt_tracking_keeps_the_template_separate_from_runtime_values() -> None:
    prompt = Mock()
    prompt.pretty_repr.return_value = "Question: {query}"
    with prompt_annotation_context(
        prompt, {"query": "synthetic private text"}, prompt_id="answer", version="1"
    ):
        attributes = dict(get_attributes_from_context())
    assert attributes["llm.prompt_template.template"] == "Question: {query}"
    assert json.loads(attributes["metadata"]) == {"prompt_id": "answer"}
    prompt.format_messages.assert_not_called()


def test_http_headers_answer_and_logs_share_the_phoenix_server_span(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, capsys: pytest.CaptureFixture[str]
) -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr("app.main.get_settings", lambda: settings)

    async def generate(request: RetrieveRequest, _: Settings) -> AnswerResponse:
        answer = AnswerResponse(
            as_of=request.as_of,
            status="insufficient_evidence",
            answer="No evidence",
            citations=[],
            generation_ms=0,
            retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
        )
        correlate_answer(answer)
        structlog.get_logger().info("answer_probe")
        return answer

    monkeypatch.setattr(answer_api, "answer_policy", generate)
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=provider,
        server_request_hook=capture_request,
        client_response_hook=correlate_response,
    )
    try:
        with TestClient(app) as client:
            assert client.get("/health").status_code == 200
            assert client.post("/answer", json={}).status_code == 422
            response = client.post("/answer", json={"query": "limit", "as_of": "2026-10-01"})
        assert response.status_code == 200
        body = response.json()
        assert body["phoenix_span_id"] == response.headers["x-phoenix-span-id"]
        assert body["phoenix_trace_id"] == response.headers["x-phoenix-trace-id"]
        logs = [
            json.loads(line)
            for line in capsys.readouterr().out.splitlines()
            if line.startswith("{")
        ]
        event = next(item for item in logs if item.get("event") == "answer_probe")
        assert event["trace_id"] == body["phoenix_trace_id"]
        roots = [
            span for span in exporter.get_finished_spans() if span.kind == trace.SpanKind.SERVER
        ]
        assert sorted(span.attributes["http.status_code"] for span in roots) == [200, 200, 422]
    finally:
        FastAPIInstrumentor.uninstrument_app(app)
        provider.shutdown()
