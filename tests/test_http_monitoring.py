from __future__ import annotations

import json

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from starlette.responses import StreamingResponse

from app.core.http_monitoring import CAPTURE_LIMIT
from app.core.phoenix import capture_request, correlate_response
from app.main import create_app


@pytest.mark.parametrize("capture", [False, True])
def test_all_route_monitoring_and_capture_do_not_change_responses(capture: bool) -> None:
    app = create_app()
    app.state.phoenix_capture_content = capture

    @app.post("/probe/{item_id}")
    async def probe(item_id: str, payload: dict) -> dict:
        return payload

    @app.get("/unavailable")
    async def unavailable() -> None:
        raise HTTPException(503, "Synthetic outage")

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=provider,
        server_request_hook=capture_request,
        client_response_hook=correlate_response,
    )
    payload = {"query": "Contact learner@example.com", "api_key": "sk-synthetic-secret"}
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                "/probe/one?token=hidden-query",
                json=payload,
                headers={"Authorization": "Bearer hidden-header"},
            )
            assert response.json() == payload
            assert client.post("/probe/two", json={"query": "another"}).status_code == 200
            assert client.post("/probe/three", content="invalid").status_code == 422
            assert client.get("/unavailable").status_code == 503
            assert client.get("/unknown/one").status_code == 404
            assert client.get("/unknown/two").status_code == 404
            assert client.get("/health").status_code == 200
            invalid = client.post(
                "/answer",
                json={
                    "query": "Synthetic loan question",
                    "as_of": "2026-10-01",
                    "password": "SYNTHETIC_PASSWORD_MARKER",
                },
            )
            assert invalid.status_code == 422
            numeric_invalid = client.post(
                "/answer",
                json={
                    "query": 9876543210,
                    "as_of": "2026-10-01",
                    "aadhaar": 123412341234,
                    "client_secret": "CLIENT_SECRET_MARKER",
                    "apiKey": "API_KEY_MARKER",
                },
            )
            assert numeric_invalid.status_code == 422
            metrics = client.get("/metrics/http").json()
        rows = {(r["method"], r["route"]): r for r in metrics["routes"]}
        row = rows["POST", "/probe/{item_id}"]
        assert row["requests"] == 3 and row["client_errors"] == 1
        assert row["sample_count"] == 3 and row["p95_ms"] >= 0
        assert rows["GET", "/unavailable"]["server_errors"] == 1
        assert rows["GET", "__unmatched__"]["requests"] == 2
        assert rows["POST", "/answer/evaluated"]["requests"] == 0
        assert rows["GET", "/health"]["requests"] == 1
        root = next(
            s
            for s in exporter.get_finished_spans()
            if f"{s.context.span_id:016x}" == response.headers["x-phoenix-span-id"]
        )
        attributes = dict(root.attributes or {})
        assert root.kind == trace.SpanKind.SERVER
        assert "hidden-query" not in str(attributes)
        assert "hidden-header" not in str(attributes)
        if capture:
            for direction in ("input", "output"):
                value = json.loads(attributes[f"{direction}.value"])
                assert value == {
                    "query": "Contact [REDACTED_EMAIL]",
                    "api_key": "[REDACTED_SECRET]",
                }
        else:
            assert "input.value" not in attributes and "output.value" not in attributes
        invalid_span = next(
            s
            for s in exporter.get_finished_spans()
            if f"{s.context.span_id:016x}" == invalid.headers["x-phoenix-span-id"]
        )
        assert "SYNTHETIC_PASSWORD_MARKER" not in str(invalid_span.attributes)
        numeric_span = next(
            s
            for s in exporter.get_finished_spans()
            if f"{s.context.span_id:016x}" == numeric_invalid.headers["x-phoenix-span-id"]
        )
        for marker in ("9876543210", "123412341234", "CLIENT_SECRET_MARKER", "API_KEY_MARKER"):
            assert marker not in str(numeric_span.attributes)
    finally:
        FastAPIInstrumentor.uninstrument_app(app)
        provider.shutdown()


def test_streaming_large_payloads_and_unhandled_errors_are_bounded() -> None:
    app = create_app()
    app.state.phoenix_capture_content = True

    @app.get("/large")
    async def large() -> StreamingResponse:
        async def chunks():
            yield b'{"result":"'
            yield b"x" * (CAPTURE_LIMIT + 1)
            yield b'"}'

        return StreamingResponse(chunks(), media_type="application/json")

    @app.get("/broken")
    async def broken() -> None:
        raise RuntimeError("synthetic failure")

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=provider, server_request_hook=capture_request
    )
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            assert len(client.get("/large").json()["result"]) == CAPTURE_LIMIT + 1
            assert client.get("/broken").status_code == 500
            rows = client.get("/metrics/http").json()["routes"]
        large_span = next(s for s in exporter.get_finished_spans() if s.name == "GET /large")
        assert large_span.attributes is not None
        assert "exceeds 64 KiB" in large_span.attributes["nexa.output.capture"]
        assert "output.value" not in large_span.attributes
        assert next(r for r in rows if r["route"] == "/broken")["server_errors"] == 1
    finally:
        FastAPIInstrumentor.uninstrument_app(app)
        provider.shutdown()
