from __future__ import annotations

import asyncio
from datetime import date
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api import answer as answer_api
from app.core import observability
from app.core.config import Settings, get_settings
from app.main import create_app
from app.models.answer import AnswerCitation, AnswerResponse
from app.models.evaluation import METRIC_NAMES, QualityScore
from app.models.retrieval import Citation, RetrieveRequest, RetrieveTimings
from app.services import evaluation as service

REQUEST = RetrieveRequest(query="Maximum loan amount?", as_of=date(2026, 10, 1))


def _answer(status: str = "answered") -> AnswerResponse:
    citation = Citation(
        doc_id="POL-HL-V3",
        title="T",
        policy_version="3",
        clause="4.1",
        effective_date=date(2025, 10, 1),
    )
    return AnswerResponse(
        as_of=REQUEST.as_of,
        status=status,  # type: ignore[arg-type]
        answer="7.5 crore [1]",
        citations=[
            AnswerCitation(evidence_id=1, quote="Maximum is 7.5 crore.", matched_child=citation)
        ]
        if status == "answered"
        else [],
        retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
        generation_ms=0,
    )


@pytest.fixture(autouse=True)
def clean_window() -> None:
    observability.sampled_hallucination.clear()


def test_sampling_is_off_by_default_and_skips_abstentions(settings: Settings) -> None:
    assert settings.live_eval_sample_rate == 0
    assert not service.should_sample(_answer(), settings)
    always = settings.model_copy(update={"live_eval_sample_rate": 1.0})
    assert service.should_sample(_answer(), always)
    assert not service.should_sample(_answer("insufficient_evidence"), always)


def test_sampled_scoring_uses_cited_quotes_and_never_raises(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    metrics = {
        name: QualityScore(status="unavailable", reason="No reference") for name in METRIC_NAMES
    }
    metrics["faithfulness"] = QualityScore(status="scored", value=0.9)
    score = AsyncMock(return_value=metrics)
    monkeypatch.setattr(service, "score_answer", score)
    asyncio.run(service.score_sampled_answer(REQUEST, _answer(), settings))
    assert list(observability.sampled_hallucination) == [pytest.approx(0.1)]
    assert score.await_args is not None
    _query, _answer_arg, contexts, reference, _settings = score.await_args.args
    assert contexts == ["Maximum is 7.5 crore."]
    assert reference is None

    score.side_effect = RuntimeError("judge down")
    asyncio.run(service.score_sampled_answer(REQUEST, _answer(), settings))  # must not raise


def test_answer_endpoint_schedules_sampled_scoring_after_responding(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    sampled = settings.model_copy(update={"live_eval_sample_rate": 1.0})
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: sampled
    monkeypatch.setattr(answer_api, "answer_policy", AsyncMock(return_value=_answer()))
    scorer = AsyncMock()
    monkeypatch.setattr(answer_api, "score_sampled_answer", scorer)
    response = TestClient(app).post("/answer", json={"query": "fee", "as_of": "2026-10-01"})
    assert response.status_code == 200
    scorer.assert_awaited_once()
    app.dependency_overrides[get_settings] = lambda: settings
    scorer.reset_mock()
    TestClient(app).post("/answer", json={"query": "fee", "as_of": "2026-10-01"})
    scorer.assert_not_awaited()
