from __future__ import annotations

import asyncio
from datetime import date
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.runnables import RunnableLambda

from app.core.config import Settings
from app.models.answer import AnswerResponse
from app.models.retrieval import RetrieveRequest, RetrieveResponse, RetrieveTimings
from app.services import answer as answer_service
from app.services import evaluation as evaluation_service
from app.services import retrieval as retrieval_service

TIMINGS = RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0)


def first_arg(mock: Any) -> Any:
    assert mock.await_args is not None
    return mock.await_args.args[0]


RAW = "My email is asha.rao@example.com and phone 98765 43210: what is the fee?"


def _request(query: str = RAW) -> RetrieveRequest:
    return RetrieveRequest(query=query, as_of=date(2026, 10, 1))


def test_scrub_request_redacts_identifiers_and_leaves_clean_queries_alone(
    settings: Settings,
) -> None:
    clean = _request("What is the processing fee for NexaHome loans above ₹7,50,00,000?")
    assert retrieval_service.scrub_request(clean, settings) == clean
    scrubbed = retrieval_service.scrub_request(_request(), settings)
    assert "asha.rao" not in scrubbed.query and "98765" not in scrubbed.query
    assert "[REDACTED_EMAIL]" in scrubbed.query and "what is the fee?" in scrubbed.query
    assert scrubbed.as_of == date(2026, 10, 1)


def test_query_redaction_can_be_disabled(settings: Settings) -> None:
    off = settings.model_copy(update={"redact_queries": False})
    assert retrieval_service.scrub_request(_request(), off).query == RAW


def test_retrieval_chain_never_receives_the_raw_query(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    chain = Mock()
    chain.ainvoke = AsyncMock(
        return_value=RetrieveResponse(as_of=date(2026, 10, 1), results=[], timings=TIMINGS)
    )
    monkeypatch.setattr(retrieval_service, "get_embeddings", lambda _s: object())
    monkeypatch.setattr(retrieval_service, "get_vector_store", lambda *_a: object())
    monkeypatch.setattr(retrieval_service, "get_parent_store", lambda _s: object())
    monkeypatch.setattr(retrieval_service, "build_retrieval_chain", lambda *_a, **_k: chain)
    asyncio.run(retrieval_service.retrieve_policy(_request(), settings))
    sent = first_arg(chain.ainvoke)
    assert "asha.rao" not in sent.query and "98765" not in sent.query


def test_answer_chain_never_receives_the_raw_query(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    seen: list[str] = []

    async def run(request: RetrieveRequest) -> AnswerResponse:
        seen.append(request.query)
        return AnswerResponse(
            as_of=request.as_of,
            status="insufficient_evidence",
            answer="a",
            citations=[],
            retrieval_timings=TIMINGS,
            generation_ms=0,
        )

    monkeypatch.setattr(answer_service, "build_answer_chain", lambda *_a, **_k: RunnableLambda(run))
    monkeypatch.setattr(answer_service, "get_chat_model", lambda _s: Mock())
    asyncio.run(answer_service.answer_policy(_request(), settings))
    assert len(seen) == 1 and "asha.rao" not in seen[0] and "98765" not in seen[0]


def test_evaluated_answer_path_also_scrubs_before_retrieval(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    from app.models.evaluation import METRIC_NAMES, EvaluatedAnswerRequest, QualityScore

    retrieve = AsyncMock(
        return_value=RetrieveResponse(as_of=date(2026, 10, 1), results=[], timings=TIMINGS)
    )
    monkeypatch.setattr(evaluation_service, "retrieve_policy", retrieve)
    monkeypatch.setattr(evaluation_service, "get_chat_model", lambda _s: Mock())
    unavailable = {name: QualityScore(status="unavailable", reason="stub") for name in METRIC_NAMES}
    monkeypatch.setattr(evaluation_service, "score_answer", AsyncMock(return_value=unavailable))
    request = EvaluatedAnswerRequest(query=RAW, as_of=date(2026, 10, 1))
    asyncio.run(evaluation_service.answer_with_quality(request, settings))
    sent = first_arg(retrieve)
    assert "asha.rao" not in sent.query
    # The judge model is also an external provider: it must not see the raw question either.
    judged_query = first_arg(evaluation_service.score_answer)
    assert "asha.rao" not in judged_query


def test_sampled_scoring_scrubs_the_question_before_the_judge(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    from app.models.evaluation import METRIC_NAMES, QualityScore

    unavailable = {name: QualityScore(status="unavailable", reason="stub") for name in METRIC_NAMES}
    score = AsyncMock(return_value=unavailable)
    monkeypatch.setattr(evaluation_service, "score_answer", score)
    answer = AnswerResponse(
        as_of=date(2026, 10, 1),
        status="answered",
        answer="a [1]",
        citations=[],
        retrieval_timings=TIMINGS,
        generation_ms=0,
    )
    asyncio.run(evaluation_service.score_sampled_answer(_request(), answer, settings))
    assert "asha.rao" not in first_arg(score)
