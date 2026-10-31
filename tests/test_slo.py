from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from langchain_core.runnables import RunnableLambda

from app.core import observability
from app.core.config import Settings, get_settings
from app.core.observability import TokenUsageLogger, latency_summary
from app.evaluation.gates import load_gates
from app.evaluation.slo_check import check_slo
from app.main import create_app
from app.models.answer import AnswerResponse
from app.models.retrieval import RetrieveRequest, RetrieveTimings
from app.services import answer as answer_service


@pytest.fixture(autouse=True)
def clean_metrics() -> None:
    observability.answer_latencies.clear()
    observability.answer_metrics.clear()
    observability.sampled_hallucination.clear()


def _answer(tokens_in: int, tokens_out: int, fail: bool = False) -> Any:
    async def run(_request: RetrieveRequest) -> AnswerResponse:
        message = AIMessage(
            content="x",
            usage_metadata={
                "input_tokens": tokens_in,
                "output_tokens": tokens_out,
                "total_tokens": tokens_in + tokens_out,
            },
        )
        await TokenUsageLogger().on_llm_end(
            LLMResult(generations=[[ChatGeneration(message=message)]])
        )
        if fail:
            raise RuntimeError("model down")
        return AnswerResponse(
            as_of=date(2026, 10, 1),
            status="insufficient_evidence",
            answer="a",
            citations=[],
            retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
            generation_ms=0,
        )

    return RunnableLambda(run)


def _serve(monkeypatch: pytest.MonkeyPatch, chain: Any) -> None:
    monkeypatch.setattr(answer_service, "build_answer_chain", lambda *_a, **_k: chain)
    monkeypatch.setattr(answer_service, "get_chat_model", lambda _s: Mock())


def test_answer_service_records_latency_tokens_and_errors(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    request = RetrieveRequest(query="q", as_of=date(2026, 10, 1))
    _serve(monkeypatch, _answer(1000, 200))
    asyncio.run(answer_service.answer_policy(request, settings))
    _serve(monkeypatch, _answer(10, 5, fail=True))
    with pytest.raises(RuntimeError):
        asyncio.run(answer_service.answer_policy(request, settings))
    assert observability.answer_metrics == {
        "requests": 2,
        "errors": 1,
        "input_tokens": 1010,
        "output_tokens": 205,
    }
    assert latency_summary(observability.answer_latencies)["sample_count"] == 1


def test_judge_tokens_outside_an_answer_request_are_not_counted() -> None:
    message = AIMessage(
        content="x", usage_metadata={"input_tokens": 9, "output_tokens": 1, "total_tokens": 10}
    )
    asyncio.run(
        TokenUsageLogger().on_llm_end(LLMResult(generations=[[ChatGeneration(message=message)]]))
    )
    assert not observability.answer_metrics


def test_answer_metrics_endpoint_prices_tokens_only_when_configured(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    request = RetrieveRequest(query="q", as_of=date(2026, 10, 1))
    _serve(monkeypatch, _answer(1_000_000, 500_000))
    asyncio.run(answer_service.answer_policy(request, settings))
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    body = TestClient(app).get("/metrics/answers").json()
    assert body["answer_requests_total"] == 1
    assert body["answer_error_rate"] == 0
    assert body["cost_per_query_usd"] is None
    priced = settings.model_copy(
        update={"chat_input_price_per_mtok": 2.0, "chat_output_price_per_mtok": 4.0}
    )
    app.dependency_overrides[get_settings] = lambda: priced
    assert TestClient(app).get("/metrics/answers").json()["cost_per_query_usd"] == 4.0


def test_slo_check_reports_pass_fail_and_not_measured() -> None:
    gates = load_gates(Path("app/evaluation/gates.json"))
    healthy = {
        "sample_count": 10,
        "p95_ms": 900.0,
        "answer_error_rate": 0.0,
        "cost_per_query_usd": 0.004,
        "sampled_count": 20,
        "sampled_hallucination_rate": 0.02,
    }
    assert {r["status"] for r in check_slo(healthy, gates)} == {"pass"}
    bad = {
        **healthy,
        "p95_ms": 2500.0,
        "answer_error_rate": 0.01,
        "cost_per_query_usd": None,
        "sampled_hallucination_rate": 0.2,
    }
    statuses = {r["slo"]: r["status"] for r in check_slo(bad, gates)}
    assert statuses == {
        "p95_ms": "fail",
        "error_rate": "fail",
        "cost_per_query_usd": "not_measured",
        "hallucination_rate": "fail",
    }
    idle = {r["slo"]: r["status"] for r in check_slo({**healthy, "sample_count": 0}, gates)}
    assert idle == {
        "p95_ms": "not_measured",
        "error_rate": "not_measured",
        "cost_per_query_usd": "not_measured",
        "hallucination_rate": "pass",
    }
    unsampled = {**healthy, "sampled_count": 0, "sampled_hallucination_rate": None}
    assert {r["slo"]: r["status"] for r in check_slo(unsampled, gates)}[
        "hallucination_rate"
    ] == "not_measured"


def test_ready_checks_the_database_and_hides_failure_details(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    from pymongo.errors import ServerSelectionTimeoutError

    from app.services import retrieval as retrieval_service

    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    monkeypatch.setattr(retrieval_service, "ping_database", lambda _s: None)
    assert client.get("/ready").json() == {"status": "ready"}

    def down(_settings: Settings) -> None:
        raise ServerSelectionTimeoutError("mongodb://user:secret@host unreachable")

    monkeypatch.setattr(retrieval_service, "ping_database", down)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Not ready"}


def test_metrics_endpoint_reports_sampled_hallucination(settings: Settings) -> None:
    observability.sampled_hallucination.extend([0.0, 0.2])
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    body = TestClient(app).get("/metrics/answers").json()
    assert body["sampled_count"] == 2
    assert body["sampled_hallucination_rate"] == pytest.approx(0.1)
