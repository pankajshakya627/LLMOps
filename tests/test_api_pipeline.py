"""Offline API integration: real services/chains/parser, isolated provider and store I/O."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock, Mock

import httpx2 as httpx
import mongomock
import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_core.stores import InMemoryStore
from langchain_core.vectorstores import VectorStore
from openai import AsyncOpenAI

import app.main as main_module
from app.chains.llm import get_chat_model
from app.core import observability
from app.core.config import Settings, get_settings
from app.database import feedback as feedback_database
from app.services import answer as answer_service
from app.services import evaluation as evaluation_service
from app.services import retrieval as retrieval_service

QUESTION = {
    "query": "What is the maximum loan amount for a NexaHome Loan?",
    "as_of": "2026-10-01",
    "product_id": "NEXA-HL",
    "top_k": 20,
}
POLICY = "Maximum loan amount is ₹7,50,00,000."
VALID_DRAFT = {
    "status": "answered",
    "answer": "The maximum is ₹7,50,00,000. [1]",
    "evidence": [{"evidence_id": 1, "quote": POLICY}],
}
REVIEW_HEADERS = {"Authorization": "Bearer reviewer-test-token-000000000000000000"}


@dataclass
class Pipeline:
    client: TestClient
    search: AsyncMock
    requests: list[dict[str, Any]] = field(default_factory=list)
    drafts: list[dict[str, Any]] = field(default_factory=lambda: [VALID_DRAFT])
    provider_status: int = 200


@pytest.fixture
def pipeline(monkeypatch: pytest.MonkeyPatch, settings: Settings) -> Iterator[Pipeline]:
    settings = Settings.model_validate(
        {
            **settings.model_dump(),
            "chat_base_url": "http://provider.invalid/v1",
            "chat_api_key": "offline-key",
            "chat_api_mode": "chat_completions",
            "chat_model": "offline-candidate",
            "feedback_reviewer_token": REVIEW_HEADERS["Authorization"].removeprefix("Bearer "),
        }
    )
    metadata = {
        "doc_id": "POL-HL-V3",
        "title": "Home loan policy",
        "policy_version": "3.0",
        "clause": "4.1",
        "parent_id": "home-amount",
        "effective_date": "2025-10-01",
        "product_id": "NEXA-HL",
        "institution": "NexaBank",
        "jurisdiction": "IN",
        "confidentiality_level": "internal",
    }
    document = Document(page_content=POLICY, metadata=metadata)
    parents = InMemoryStore()
    parents.mset([("home-amount", document)])
    vector = Mock(spec=VectorStore)
    search = AsyncMock(return_value=[(document, 0.95)])
    vector.asimilarity_search_with_score = search
    monkeypatch.setattr(retrieval_service, "get_embeddings", lambda _: object())
    monkeypatch.setattr(retrieval_service, "get_vector_store", lambda *_: vector)
    monkeypatch.setattr(retrieval_service, "get_parent_store", lambda _: parents)
    monkeypatch.setattr(
        retrieval_service, "build_amendment_search", lambda _: RunnableLambda(lambda _: [])
    )
    storage: Any = mongomock.MongoClient().db
    monkeypatch.setattr(feedback_database, "_database", lambda _: storage)
    monkeypatch.setattr(main_module, "get_settings", lambda: settings)
    app = main_module.create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    runtime = Pipeline(client=TestClient(app), search=search)

    def respond(request: httpx.Request) -> httpx.Response:
        runtime.requests.append(json.loads(request.content))
        if runtime.provider_status != 200:
            return httpx.Response(runtime.provider_status, json={"error": {"message": "private"}})
        draft = runtime.drafts.pop(0) if len(runtime.drafts) > 1 else runtime.drafts[0]
        return httpx.Response(
            200,
            json={
                "id": "offline-completion",
                "object": "chat.completion",
                "created": 0,
                "model": "observed-offline-candidate",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": json.dumps(draft)},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 30, "completion_tokens": 10, "total_tokens": 40},
            },
        )

    transport = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    provider = AsyncOpenAI(
        base_url=settings.chat_base_url, api_key="offline-key", http_client=transport, max_retries=0
    )
    model = get_chat_model(settings)
    model.root_async_client = provider
    model.async_client = provider.chat.completions
    monkeypatch.setattr(answer_service, "get_chat_model", lambda _: model)
    monkeypatch.setattr(evaluation_service, "get_chat_model", lambda _: model)
    counters = (observability.answer_metrics, retrieval_service.retrieval_metrics)
    histories = (observability.answer_latencies, observability.retrieval_latencies)
    counter_snapshots = [counter.copy() for counter in counters]
    history_snapshots = [history.copy() for history in histories]
    for counter in counters:
        counter.clear()
    for history in histories:
        history.clear()
    try:
        with runtime.client:
            yield runtime
    finally:
        asyncio.run(provider.close())
        for counter, saved_counter in zip(counters, counter_snapshots, strict=True):
            counter.clear()
            counter.update(saved_counter)
        for history, saved_history in zip(histories, history_snapshots, strict=True):
            history.clear()
            history.extend(saved_history)


def test_answer_can_be_reviewed_and_exported_without_replacing_business_layers(
    pipeline: Pipeline,
) -> None:
    response = pipeline.client.post("/answer", json=QUESTION)
    assert response.status_code == 200
    answer = response.json()
    assert answer["answer"] == VALID_DRAFT["answer"]
    assert answer["citations"][0]["matched_child"]["doc_id"] == "POL-HL-V3"
    assert answer["provenance"]["observed_chat_model"] == "observed-offline-candidate"
    metrics = pipeline.client.get("/metrics/answers").json()
    assert metrics["answer_requests_total"] == 1
    assert metrics["input_tokens_total"] == 30
    assert metrics["output_tokens_total"] == 10
    saved = pipeline.client.post(
        "/feedback", json={"request": QUESTION, "response": answer, "helpful": True}
    )
    assert saved.status_code == 201
    identifier = saved.json()["feedback_id"]
    assert pipeline.client.get("/feedback").status_code == 401
    reviewed = pipeline.client.post(
        f"/feedback/{identifier}/review",
        headers=REVIEW_HEADERS,
        json={"status": "accepted", "reviewer": "Instructor", "review_note": "Policy checked."},
    )
    assert reviewed.status_code == 200
    exported = pipeline.client.post(
        f"/feedback/{identifier}/golden",
        headers=REVIEW_HEADERS,
        json={
            "input": QUESTION,
            "expected_output": POLICY,
            "expected_status": "answered",
            "context": [{"doc_id": "POL-HL-V3", "clause": "4.1"}],
        },
    )
    assert exported.status_code == 200
    assert exported.json()["case"]["expected_output"] == POLICY
    assert exported.json()["review"]["reviewer"] == "Instructor"


def test_retrieval_returns_evidence_without_calling_the_chat_provider(pipeline: Pipeline) -> None:
    response = pipeline.client.post("/retrieve", json=QUESTION)
    assert response.status_code == 200
    assert response.json()["results"][0]["parent_text"] == POLICY
    assert not pipeline.requests
    assert pipeline.search.await_args is not None
    assert {"product_id": "NEXA-HL"} in pipeline.search.await_args.kwargs["pre_filter"]["$and"]


def test_empty_search_abstains_without_spending_generation_tokens(pipeline: Pipeline) -> None:
    pipeline.search.return_value = []
    response = pipeline.client.post("/answer", json=QUESTION)
    assert response.status_code == 200
    assert response.json()["status"] == "insufficient_evidence"
    assert response.json()["generation_ms"] == 0
    assert response.json()["citations"] == []
    assert not pipeline.requests


def test_query_pii_is_removed_before_search_and_the_serialized_model_request(
    pipeline: Pipeline,
) -> None:
    private = "learner@example.com"
    response = pipeline.client.post("/answer", json={**QUESTION, "query": f"{private} loan limit?"})
    assert response.status_code == 200
    assert pipeline.search.await_args is not None
    assert private not in pipeline.search.await_args.args[0]
    assert "[REDACTED_EMAIL]" in pipeline.search.await_args.args[0]
    assert private not in json.dumps(pipeline.requests)
    assert "[REDACTED_EMAIL]" in json.dumps(pipeline.requests)


def test_citation_repair_reuses_evidence_and_returns_only_the_verified_draft(
    pipeline: Pipeline,
) -> None:
    pipeline.drafts.insert(0, {**VALID_DRAFT, "evidence": [{"evidence_id": 1, "quote": "fake"}]})
    response = pipeline.client.post("/answer", json=QUESTION)
    assert response.status_code == 200
    assert response.json()["status"] == "answered"
    assert response.json()["citations"][0]["quote"] == POLICY
    assert pipeline.search.await_count == 1
    assert len(pipeline.requests) == 2
    assert "previous draft failed citation validation" in json.dumps(pipeline.requests[1])


def test_unrepairable_citations_abstain_after_two_provider_calls(pipeline: Pipeline) -> None:
    pipeline.drafts[:] = [{**VALID_DRAFT, "evidence": [{"evidence_id": 1, "quote": "invented"}]}]
    response = pipeline.client.post("/answer", json=QUESTION)
    assert response.status_code == 200
    assert response.json()["status"] == "insufficient_evidence"
    assert response.json()["citations"] == []
    assert len(pipeline.requests) == 2


def test_provider_failure_is_a_sanitized_503_and_counted_in_metrics(pipeline: Pipeline) -> None:
    pipeline.provider_status = 503
    response = pipeline.client.post("/answer", json=QUESTION)
    assert response.status_code == 503
    assert response.json() == {"detail": "Answer service unavailable"}
    assert len(pipeline.requests) == 1
    metrics = pipeline.client.get("/metrics/answers").json()
    assert metrics["answer_errors_total"] == 1
    assert metrics["answer_error_rate"] == 1


@pytest.mark.parametrize(
    "draft,expected_status",
    [
        ({**VALID_DRAFT, "status": "approve_loan"}, 503),
        ({**VALID_DRAFT, "answer": "Contact learner@example.com [1]"}, 200),
    ],
)
def test_invalid_schema_and_output_pii_never_return_an_unsafe_answer(
    pipeline: Pipeline, draft: dict[str, Any], expected_status: int
) -> None:
    pipeline.drafts[:] = [draft]
    response = pipeline.client.post("/answer", json=QUESTION)
    assert response.status_code == expected_status
    assert "learner@example.com" not in response.text
    assert len(pipeline.requests) == 1
    if expected_status == 200:
        assert response.json()["status"] == "insufficient_evidence"
        assert response.json()["citations"] == []


def test_evaluated_empty_search_preserves_unavailable_scores_through_http(
    pipeline: Pipeline,
) -> None:
    pipeline.search.return_value = []
    response = pipeline.client.post("/answer/evaluated", json=QUESTION)
    assert response.status_code == 200
    assert response.json()["quality"]["reference_source"] == "golden_dataset"
    assert all(
        metric["status"] == "unavailable" and metric["value"] is None
        for metric in response.json()["quality"]["metrics"].values()
    )
    assert pipeline.search.await_count == 1
    assert not pipeline.requests


@pytest.mark.parametrize("route", ["/retrieve", "/answer", "/answer/evaluated"])
@pytest.mark.parametrize("change", [{"query": "   "}, {"top_k": 21}, {"as_of": "bad-date"}])
def test_invalid_api_requests_never_reach_search_or_generation(
    pipeline: Pipeline, route: str, change: dict[str, Any]
) -> None:
    assert pipeline.client.post(route, json={**QUESTION, **change}).status_code == 422
    pipeline.search.assert_not_awaited()
    assert not pipeline.requests
