"""Run explicitly with requirements-phoenix.txt; no collector or model service is needed."""

from __future__ import annotations

import importlib
import json
import sys
from typing import Any

import httpx
import httpx2
import pytest
from fastapi.testclient import TestClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openinference.instrumentation import TracerProvider
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from phoenix.client import Client

from app.api import answer as answer_api
from app.core import config
from app.core.config import Settings
from app.core.observability import prompt_annotation_context
from app.core.phoenix import correlate_answer
from app.evaluation.phoenix_export import build_annotations
from app.models.answer import AnswerResponse
from app.models.evaluation import EvaluatedAnswerResponse
from app.models.retrieval import RetrieveRequest, RetrieveTimings

PRIVATE = "SYNTHETIC-PRIVATE-MARKER"


@pytest.mark.parametrize("capture", [False, True])
def test_real_instrumentors_correlate_server_model_tokens_and_content_policy(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, capture: bool
) -> None:
    settings = settings.model_copy(update={"phoenix_capture_content": capture})
    exporter = InMemorySpanExporter()

    def register(**kwargs: Any) -> TracerProvider:
        assert kwargs["endpoint"] == f"{settings.phoenix_base_url}/v1/traces"
        assert kwargs["set_global_tracer_provider"] is False
        provider = TracerProvider(config=kwargs["config"])
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        return provider

    def respond(request: httpx2.Request) -> httpx2.Response:
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
                        "message": {"role": "assistant", "content": PRIVATE},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 8, "completion_tokens": 3, "total_tokens": 11},
            },
        )

    async def generate(request: RetrieveRequest, _settings: Settings) -> AnswerResponse:
        async with httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport:
            model = ChatOpenAI(
                model="offline-candidate",
                api_key="synthetic-key",
                base_url="http://provider.invalid/v1",
                use_responses_api=False,
                http_async_client=transport,
            )
            prompt = ChatPromptTemplate.from_messages([("human", "{query}")])
            variables = {"query": request.query}
            with prompt_annotation_context(prompt, variables, prompt_id="answer", version="1.2.0"):
                await (prompt | model).ainvoke(
                    variables, config={"metadata": {"synthetic_private": PRIVATE}}
                )
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

    monkeypatch.setattr(config, "get_settings", lambda: settings)
    monkeypatch.setattr("phoenix.otel.register", register)
    monkeypatch.setattr(answer_api, "answer_policy", generate)
    profile = importlib.import_module("app.phoenix_main")
    import app.main as main_module

    monkeypatch.setattr(main_module, "get_settings", lambda: settings)
    profile.app.dependency_overrides[config.get_settings] = lambda: settings
    try:
        with TestClient(profile.app) as client:
            assert client.get("/health").status_code == 200
            assert client.post("/answer", json={}).status_code == 422
            response = client.post("/answer", json={"query": PRIVATE, "as_of": "2026-10-01"})
            assert response.status_code == 200
        spans = exporter.get_finished_spans()
        assert not any(span.name.startswith("GET /health") for span in spans)
        root = next(
            span
            for span in spans
            if f"{span.context.span_id:016x}" == response.headers["x-phoenix-span-id"]
        )
        assert root.attributes is not None and root.attributes["http.route"] == "/answer"
        if capture:
            assert json.loads(root.attributes["output.value"])["answer"] == "No evidence."
        else:
            # OpenInference may add its sentinel without retaining any result content.
            assert root.attributes.get("output.value") in (None, "__REDACTED__")
        assert f"{root.context.trace_id:032x}" == response.headers["x-phoenix-trace-id"]
        assert response.json()["phoenix_trace_id"] == response.headers["x-phoenix-trace-id"]
        assert response.json()["phoenix_span_id"] == response.headers["x-phoenix-span-id"]
        llm = next(
            span
            for span in spans
            if span.attributes and span.attributes.get("openinference.span.kind") == "LLM"
        )
        assert llm.context.trace_id == root.context.trace_id
        assert llm.attributes is not None and llm.attributes["llm.token_count.total"] == 11
        assert llm.attributes["llm.prompt_template.version"] == "1.2.0"
        assert (PRIVATE in str([dict(span.attributes or {}) for span in spans])) is capture
    finally:
        FastAPIInstrumentor.uninstrument_app(profile.app)
        LangChainInstrumentor().uninstrument()
        sys.modules.pop("app.phoenix_main", None)


def test_real_phoenix_client_serializes_scores_to_the_exact_server_span() -> None:
    response = EvaluatedAnswerResponse.model_validate(
        {
            "answer": {
                "as_of": "2026-10-01",
                "status": "insufficient_evidence",
                "answer": "No evidence.",
                "citations": [],
                "generation_ms": 0,
                "retrieval_timings": {"search_ms": 0, "parent_ms": 0, "total_ms": 0},
            },
            "quality": {
                "metrics": {
                    "faithfulness": {"status": "scored", "value": 0.0},
                    "answer_relevancy": {"status": "scored", "value": 1.0},
                    "context_precision": {"status": "unavailable", "reason": "No reference"},
                    "context_recall": {"status": "error", "reason": "Judge timeout"},
                },
                "reference_source": "none",
                "evaluated_at": "2026-10-25T00:00:00Z",
            },
        }
    )
    sent = []

    def publish(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/span_annotations"
        assert request.url.params["sync"] == "true"
        data = json.loads(request.content)["data"]
        sent.extend(data)
        return httpx.Response(200, json={"data": [{"id": str(i)} for i in range(len(data))]})

    with httpx.Client(
        base_url="http://collector.invalid", transport=httpx.MockTransport(publish)
    ) as transport:
        Client(
            base_url="http://collector.invalid", http_client=transport
        ).spans.log_span_annotations(
            span_annotations=build_annotations(response, "0123456789abcdef"), sync=True
        )
    values = {item["name"]: item for item in sent}
    assert len(sent) == 4
    assert all(item["span_id"] == "0123456789abcdef" for item in sent)
    assert values["ragas_faithfulness"]["result"]["score"] == 0.0
    assert "score" not in values["ragas_context_precision"]["result"]
    assert values["ragas_context_recall"]["result"]["label"] == "error"
