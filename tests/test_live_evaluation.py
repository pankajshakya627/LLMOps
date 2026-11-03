from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.runnables import RunnableLambda
from pydantic import ValidationError

from app.core.config import Settings
from app.evaluation import live
from app.models.answer import AnswerResponse
from app.models.evaluation import METRIC_NAMES, EvaluatedAnswerRequest, QualityScore
from app.models.retrieval import RetrieveResponse
from app.services import answer as answer_service
from app.services import evaluation as service


@pytest.mark.parametrize("traced", [False, True])
def test_plain_answers_correlate_datadog_without_requiring_ragas(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, answer: AnswerResponse, traced: bool
) -> None:
    from ddtrace.llmobs import LLMObs

    monkeypatch.setattr(LLMObs, "enabled", traced)
    monkeypatch.setattr(LLMObs, "export_span", lambda: {"trace_id": f"{1:032x}", "span_id": "2"})
    monkeypatch.setattr(answer_service, "get_chat_model", lambda _: object())
    monkeypatch.setattr(
        answer_service, "build_answer_chain", lambda *_: RunnableLambda(lambda _: answer)
    )
    result = asyncio.run(
        answer_service.answer_policy(
            EvaluatedAnswerRequest(query="Loan limit?", as_of=answer.as_of), settings
        )
    )
    assert result is answer
    assert result.datadog_trace_id == (f"{1:032x}" if traced else None)
    assert result.datadog_span_id == ("2" if traced else None)


def test_cosine_roundoff_is_normalized_but_invalid_scores_are_rejected() -> None:
    assert QualityScore(status="scored", value=1.0000000000000002).value == 1.0
    assert QualityScore(status="scored", value=-1e-16).value == 0.0
    for invalid in (1.01, -0.1, float("inf"), float("nan")):
        with pytest.raises(ValidationError):
            QualityScore(status="scored", value=invalid)


@pytest.fixture
def evidence() -> RetrieveResponse:
    hit = {
        "rank": 1,
        "score": 0.9,
        "text": "Maximum is 7.5 crore.",
        "parent_text": "Maximum is 7.5 crore.",
        "citation": {
            "doc_id": "POL-HL-V3",
            "title": "Home loan",
            "policy_version": "3",
            "clause": "4.1",
            "effective_date": "2025-10-01",
        },
    }
    return RetrieveResponse.model_validate(
        {
            "as_of": "2026-10-01",
            "results": [hit, hit],
            "timings": {"search_ms": 1, "parent_ms": 1, "total_ms": 2},
        }
    )


@pytest.fixture
def answer(evidence: RetrieveResponse) -> AnswerResponse:
    return AnswerResponse(
        as_of=evidence.as_of,
        status="answered",
        answer="7.5 crore [1]",
        citations=[],
        retrieval_timings=evidence.timings,
        generation_ms=1,
    )


@pytest.mark.parametrize("reference_source", ["provided", "golden_dataset", "none"])
@pytest.mark.parametrize("traced", [False, True])
def test_live_scores_reuse_one_answer_and_its_exact_evidence(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    evidence: RetrieveResponse,
    answer: AnswerResponse,
    reference_source: str,
    traced: bool,
) -> None:
    request = EvaluatedAnswerRequest(
        query="What is the maximum loan amount for a NexaHome Loan?",
        as_of=date(2026, 10, 20) if reference_source == "none" else evidence.as_of,
        product_id="NEXA-HL",
        top_k=5,
        reference_answer="Expected 7.5 crore." if reference_source == "provided" else None,
    )
    retrieve = AsyncMock(return_value=evidence)
    monkeypatch.setattr(service, "retrieve_policy", retrieve)
    monkeypatch.setattr(service, "get_chat_model", lambda _: object())
    generated = Mock()

    def chain(retriever: RunnableLambda, *_: object) -> RunnableLambda:
        async def invoke(value: object) -> AnswerResponse:
            assert await retriever.ainvoke(value) is evidence
            generated()
            return answer

        return RunnableLambda(invoke)

    monkeypatch.setattr(service, "build_answer_chain", chain)
    metrics = {name: QualityScore(status="scored", value=0.0) for name in METRIC_NAMES}
    metrics["context_recall"] = QualityScore(status="unavailable", reason="No reference")
    score = AsyncMock(return_value=metrics)
    monkeypatch.setattr(service, "score_answer", score)
    from ddtrace.llmobs import LLMObs

    monkeypatch.setattr(LLMObs, "enabled", traced)
    monkeypatch.setattr(LLMObs, "export_span", lambda: {"trace_id": f"{1:032x}", "span_id": "2"})
    result = asyncio.run(service.answer_with_quality(request, settings))
    assert result.answer is answer
    assert result.answer.datadog_span_id == ("2" if traced else None)
    assert result.quality.reference_source == reference_source
    assert retrieve.await_count == generated.call_count == score.await_count == 1
    assert score.await_args is not None
    assert score.await_args.args[2] == ["Maximum is 7.5 crore."]
    assert (score.await_args.args[3] is None) == (reference_source == "none")
    assert result.quality.metrics["faithfulness"].value == 0.0
    assert result.quality.metrics["context_recall"].status == "unavailable"


def test_invalid_optional_golden_file_preserves_answer(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    evidence: RetrieveResponse,
    answer: AnswerResponse,
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "invalid.jsonl"
    dataset.write_text('{"invalid": "golden case"}\n')
    monkeypatch.setattr(service, "GOLDEN_DATASET", dataset)
    monkeypatch.setattr(service, "retrieve_policy", AsyncMock(return_value=evidence))
    monkeypatch.setattr(service, "get_chat_model", lambda _: object())
    monkeypatch.setattr(service, "build_answer_chain", lambda *_: RunnableLambda(lambda _: answer))
    metrics = {
        name: QualityScore(status="unavailable", reason="No reference") for name in METRIC_NAMES
    }
    score = AsyncMock(return_value=metrics)
    monkeypatch.setattr(service, "score_answer", score)
    result = asyncio.run(
        service.answer_with_quality(
            EvaluatedAnswerRequest(query="Question", as_of=evidence.as_of), settings
        )
    )
    assert result.answer is answer
    assert result.quality.reference_source == "none"
    assert score.await_args is not None and score.await_args.args[3] is None


@pytest.mark.parametrize("reference", [None, "Expected answer"])
def test_ragas_failures_are_explicit_and_do_not_discard_other_metrics(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    answer: AnswerResponse,
    reference: str | None,
) -> None:
    monkeypatch.setenv("RAGAS_DO_NOT_TRACK", "true")
    pytest.importorskip("ragas")
    from app.evaluation import ragas_metrics

    calls = {name: AsyncMock(return_value=SimpleNamespace(value=0.8)) for name in METRIC_NAMES}
    calls["faithfulness"].return_value = SimpleNamespace(value=0.0)
    calls["answer_relevancy"].side_effect = RuntimeError("private provider details")
    scorer = SimpleNamespace(
        metrics={name: SimpleNamespace(ascore=call) for name, call in calls.items()}
    )
    monkeypatch.setattr(ragas_metrics, "RagasScorer", lambda *_: scorer)
    monkeypatch.setattr(live, "get_chat_model", lambda _: object())
    monkeypatch.setattr(live, "get_embeddings", lambda _: object())
    result = asyncio.run(
        live.score_answer("Question", answer, ["Exact source"], reference, settings)
    )
    assert result["faithfulness"].value == 0.0
    assert result["answer_relevancy"].status == "error"
    assert "private" not in str(result["answer_relevancy"].reason)
    for name in ("context_precision", "context_recall"):
        assert calls[name].await_count == int(reference is not None)
        assert result[name].status == ("unavailable" if reference is None else "scored")
    faithfulness_call = calls["faithfulness"].await_args
    assert faithfulness_call is not None
    assert faithfulness_call.kwargs["retrieved_contexts"] == ["Exact source"]


def test_nonfinite_ragas_scores_are_errors(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    answer: AnswerResponse,
) -> None:
    monkeypatch.setenv("RAGAS_DO_NOT_TRACK", "true")
    pytest.importorskip("ragas")
    from app.evaluation import ragas_metrics

    scorer = SimpleNamespace(
        metrics={
            name: SimpleNamespace(
                ascore=AsyncMock(return_value=SimpleNamespace(value=float("nan")))
            )
            for name in METRIC_NAMES
        }
    )
    monkeypatch.setattr(ragas_metrics, "RagasScorer", lambda *_: scorer)
    monkeypatch.setattr(live, "get_chat_model", lambda _: object())
    monkeypatch.setattr(live, "get_embeddings", lambda _: object())
    result = asyncio.run(live.score_answer("Q", answer, ["Source"], "Expected", settings))
    assert all(metric.status == "error" and metric.value is None for metric in result.values())


def test_missing_evaluator_dependencies_produce_errors_without_exposing_provider_details(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, answer: AnswerResponse
) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "app.evaluation.ragas_metrics", None)
    result = asyncio.run(live.score_answer("Q", answer, ["Source"], "Reference", settings))
    assert set(result) == set(METRIC_NAMES)
    assert all(metric.status == "error" and metric.value is None for metric in result.values())
    assert all("ModuleNotFoundError" in (metric.reason or "") for metric in result.values())


def test_missing_reference_stays_unavailable_when_evaluator_initialization_also_fails(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, answer: AnswerResponse
) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "app.evaluation.ragas_metrics", None)
    result = asyncio.run(live.score_answer("Q", answer, ["Source"], None, settings))
    assert result["faithfulness"].status == result["answer_relevancy"].status == "error"
    assert result["context_precision"].status == result["context_recall"].status == "unavailable"
    assert all(metric.value is None for metric in result.values())
