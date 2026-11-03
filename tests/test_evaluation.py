from __future__ import annotations

import asyncio
import json
import sys
from contextlib import nullcontext
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from pydantic import ValidationError

from app.chains.prompts.answer import ANSWER_PROMPT_VERSION
from app.core.config import Settings
from app.evaluation import run as evaluation
from app.evaluation.run import JudgeScore, case_fingerprint, load_cases, quality_gate


def test_phase1_cases_include_supported_and_abstention_questions() -> None:
    cases = load_cases(Path("app/evaluation/datasets/answer.jsonl"))
    assert len(cases) == 10
    assert sum(case.expected_status == "insufficient_evidence" for case in cases) == 2
    assert all(case.context for case in cases if case.expected_status == "answered")


@pytest.mark.parametrize("gate_mode", ["uniform", "configured"])
@pytest.mark.parametrize("passes", [False, True])
def test_evaluation_cli_persists_results_and_sets_exit_status_from_actual_gate(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    tmp_path: Path,
    gate_mode: str,
    passes: bool,
) -> None:
    output = tmp_path / "nested" / "report.json"
    record = {
        "user_input": "Question",
        "judge": {"correctness": 1.0, "groundedness": 1.0, "status_matches": passes},
    }
    run = AsyncMock(return_value={"records": [record], "ragas": {"means": {"faithfulness": 1.0}}})
    monkeypatch.setattr(evaluation, "run", run)
    monkeypatch.setattr(evaluation, "get_settings", lambda: settings)
    argv = ["evaluation", "--output", str(output), "--limit", "1"]
    if gate_mode == "uniform":
        argv.extend(["--min-score", "0.8"])
    monkeypatch.setattr(sys, "argv", argv)
    if passes:
        evaluation.main()
    else:
        with pytest.raises(SystemExit) as stopped:
            evaluation.main()
        assert stopped.value.code == 1
    report = json.loads(output.read_text())
    assert report["gate"]["status"] == ("passed" if passes else "failed")
    assert run.await_args is not None and len(run.await_args.args[0]) == 1


def test_evaluation_cli_records_dependency_failure_without_misreporting_completed_scores(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    tmp_path: Path,
) -> None:
    output = tmp_path / "failed.json"
    monkeypatch.setattr(
        evaluation, "run", AsyncMock(side_effect=TimeoutError("private provider text"))
    )
    monkeypatch.setattr(evaluation, "get_settings", lambda: settings)
    monkeypatch.setattr(sys, "argv", ["evaluation", "--output", str(output)])
    with pytest.raises(SystemExit) as stopped:
        evaluation.main()
    assert stopped.value.code == 1
    report = json.loads(output.read_text())
    assert report["error_type"] == "TimeoutError"
    assert report["gate"]["status"] == "failed"
    assert "records" not in report and "private" not in output.read_text()


@pytest.mark.parametrize("arguments", [["--limit", "0"], ["--min-score", "1.1"]])
def test_evaluation_cli_rejects_invalid_options_before_model_or_database_work(
    monkeypatch: pytest.MonkeyPatch, arguments: list[str]
) -> None:
    run = AsyncMock()
    monkeypatch.setattr(evaluation, "run", run)
    monkeypatch.setattr(sys, "argv", ["evaluation", *arguments])
    with pytest.raises(SystemExit) as stopped:
        evaluation.main()
    assert stopped.value.code == 2
    run.assert_not_awaited()


def test_case_fingerprint_covers_scope_and_reviewed_expectations() -> None:
    case = load_cases(Path("app/evaluation/datasets/answer.jsonl"))[0]
    assert case_fingerprint(case) == case_fingerprint(case.model_copy(deep=True))
    for changed in (
        case.model_copy(update={"expected_output": "A different reviewed answer"}),
        case.model_copy(
            update={"input": case.input.model_copy(update={"as_of": date(2025, 1, 1)})}
        ),
        case.model_copy(update={"expected_status": "insufficient_evidence"}),
    ):
        assert case_fingerprint(case) != case_fingerprint(changed)


def test_quality_gate_rejects_low_quality_and_wrong_abstention() -> None:
    report: dict[str, Any] = {
        "ragas": {"means": {"faithfulness": 0.9}},
        "records": [{"judge": {"correctness": 0.9, "groundedness": 0.9, "status_matches": True}}],
    }
    assert quality_gate(report, 0.8)
    report["records"][0]["judge"]["status_matches"] = False
    assert not quality_gate(report, 0.8)
    with pytest.raises(ValidationError):
        JudgeScore(correctness=float("nan"), groundedness=1, rationale="invalid")


def test_ragas_scores_actual_text_and_penalizes_missing_evidence(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    monkeypatch.setenv("RAGAS_DO_NOT_TRACK", "true")
    settings = settings.model_copy(update={"eval_judge_model": "separate-test-judge"})
    model_factory = Mock(wraps=evaluation.get_chat_model)
    embeddings_factory = Mock(wraps=evaluation.get_embeddings)
    monkeypatch.setattr(evaluation, "get_chat_model", model_factory)
    monkeypatch.setattr(evaluation, "get_embeddings", embeddings_factory)
    pytest.importorskip("ragas")
    from ragas.metrics.collections import (
        AnswerRelevancy,
        ContextPrecision,
        ContextRecall,
        Faithfulness,
    )

    scorers = []
    for metric in (Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall):
        score = AsyncMock(return_value=SimpleNamespace(value=0.9))
        monkeypatch.setattr(metric, "ascore", score)
        scorers.append(score)
    record = {
        "expected_status": "answered",
        "user_input": "limit?",
        "response": "7.5 crore",
        "reference": "7.5 crore",
        "retrieved_contexts": ["Actual supplied policy text"],
    }
    result = asyncio.run(
        evaluation.evaluate_ragas([record, {**record, "retrieved_contexts": []}], settings)
    )
    assert result["case_count"] == 2
    assert result["means"]["context_recall"] == 0.45
    assert scorers[0].await_args is not None
    assert scorers[0].await_args.kwargs["retrieved_contexts"] == ["Actual supplied policy text"]
    assert all(score.await_count == 1 for score in scorers)
    assert model_factory.call_args.args[0].chat_model == "separate-test-judge"
    assert (
        embeddings_factory.call_args.args[0].embedding_dimensions == settings.embedding_dimensions
    )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), 1.01, -0.01, 1.0000000000000002])
def test_batch_metrics_validate_scores_like_live_metrics(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, value: float
) -> None:
    pytest.importorskip("ragas")
    from app.evaluation import ragas_metrics
    from app.models.evaluation import METRIC_NAMES

    scorer = SimpleNamespace(
        metrics={
            name: SimpleNamespace(ascore=AsyncMock(return_value=SimpleNamespace(value=value)))
            for name in METRIC_NAMES
        }
    )
    monkeypatch.setattr(ragas_metrics, "RagasScorer", lambda *_: scorer)
    monkeypatch.setattr(evaluation, "get_chat_model", lambda _: object())
    monkeypatch.setattr(evaluation, "get_embeddings", lambda _: object())
    record = {
        "expected_status": "answered",
        "user_input": "limit?",
        "response": "7.5 crore",
        "reference": "7.5 crore",
        "retrieved_contexts": ["Maximum is 7.5 crore."],
    }
    if value == 1.0000000000000002:
        result = asyncio.run(evaluation.evaluate_ragas([record], settings))
        assert result["scores"] == [dict.fromkeys(METRIC_NAMES, 1.0)]
    else:
        with pytest.raises(ValidationError):
            asyncio.run(evaluation.evaluate_ragas([record], settings))


def test_evaluation_reuses_generation_evidence_and_collects_trace(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.runnables import RunnableLambda

    from app.models.answer import AnswerDraft
    from app.models.retrieval import RetrieveResponse

    response = RetrieveResponse.model_validate(
        {
            "as_of": "2026-10-01",
            "results": [
                {
                    "rank": 1,
                    "score": 0.9,
                    "text": "Maximum is 7.5 crore.",
                    "parent_text": "Maximum is 7.5 crore.",
                    "citation": {
                        "doc_id": "POL-HL-V3",
                        "title": "Home Loan",
                        "policy_version": "3",
                        "clause": "4.1",
                        "effective_date": "2025-10-01",
                    },
                }
            ],
            "timings": {"search_ms": 1, "parent_ms": 1, "total_ms": 2},
        }
    )
    retrieval = AsyncMock(return_value=response)
    monkeypatch.setattr(evaluation, "retrieve_policy", retrieval)
    monkeypatch.setattr(
        evaluation, "resolve_reference_contexts", lambda *_: ["Reference source text"]
    )
    model = Mock(spec=BaseChatModel)

    def structured(schema: Any, **_: Any) -> Any:
        if schema is AnswerDraft:
            return RunnableLambda(
                lambda _: {
                    "status": "answered",
                    "answer": "7.5 crore [1]",
                    "evidence": [{"evidence_id": 1, "quote": "7.5 crore"}],
                }
            )
        return RunnableLambda(
            lambda _: {
                "correctness": 0.9,
                "groundedness": 1,
                "rationale": "controlled fixture",
            }
        )

    model.with_structured_output.side_effect = structured
    settings = settings.model_copy(update={"eval_judge_model": "separate-test-judge"})
    configured_models: list[str] = []
    configured_caps: list[int | None] = []

    def get_model(config: Settings) -> Any:
        configured_models.append(config.chat_model)
        configured_caps.append(config.chat_max_output_tokens)
        return model

    monkeypatch.setattr(evaluation, "get_chat_model", get_model)
    records = asyncio.run(
        evaluation.collect_records(
            load_cases(Path("app/evaluation/datasets/answer.jsonl"))[:1], settings
        )
    )
    assert retrieval.await_count == 1
    assert configured_models == [settings.chat_model, "separate-test-judge"]
    # Only answer generation is capped; the judge must be able to write its full rationale.
    assert configured_caps == [settings.chat_max_output_tokens, None]
    assert records[0]["retrieved_contexts"] == ["Maximum is 7.5 crore."]
    assert records[0]["judge"]["status_matches"] is True
    # The expected clause was retrieved, so a judge score below 1 is a generation error.
    assert records[0]["retrieval"]["recall_at_k"] == 1
    assert records[0]["failure_type"] == "generation_error"
    assert {span["name"] for span in records[0]["trace"]} >= {
        "evaluation_retrieval",
        "answer_policy",
    }


def test_batch_report_preserves_profiles_without_a_telemetry_vendor(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    monkeypatch.setattr(evaluation, "collect_records", AsyncMock(return_value=[]))
    monkeypatch.setattr(evaluation, "evaluate_ragas", AsyncMock(return_value={"scores": []}))
    settings = settings.model_copy(update={"eval_judge_model": "separate-test-judge"})
    result = asyncio.run(evaluation.run([], settings))
    assert result["judge_model"] == "separate-test-judge"
    assert len(result["dataset_sha256"]) == 64
    assert result["answer_prompt"]["version"] == ANSWER_PROMPT_VERSION
    assert result["ragas"] == {"scores": []}


@pytest.mark.parametrize("status", ["completed", "not_applicable"])
@pytest.mark.parametrize("export_fails", [False, True])
def test_batch_exports_actual_means_or_unavailable_without_changing_results(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, status: str, export_fails: bool
) -> None:
    identity = {"trace_id": "a" * 32, "span_id": "123"}
    telemetry = SimpleNamespace(
        enabled=True,
        workflow=Mock(return_value=nullcontext()),
        export_span=Mock(return_value=identity),
        annotate=Mock(),
    )
    ragas = {"status": status, "means": dict.fromkeys(evaluation.METRIC_NAMES, 0.0)}
    publish = Mock(side_effect=httpx.ConnectError("private detail") if export_fails else None)
    monkeypatch.setattr(evaluation, "LLMObs", telemetry)
    monkeypatch.setattr(evaluation, "collect_records", AsyncMock(return_value=[]))
    monkeypatch.setattr(evaluation, "evaluate_ragas", AsyncMock(return_value=ragas))
    monkeypatch.setattr(evaluation, "publish_annotations", publish)
    report = asyncio.run(evaluation.run([], settings))
    assert report["ragas"] == ragas and report["datadog_span"] == identity
    quality, joined_span, _settings = publish.call_args.args
    assert joined_span == identity and quality.reference_source == "golden_dataset"
    assert all(
        metric.value == (0.0 if status == "completed" else None)
        and metric.status == ("scored" if status == "completed" else "unavailable")
        for metric in quality.metrics.values()
    )
    telemetry.annotate.assert_called_once_with(
        tags={"evaluation_scope": "batch_mean", "case_count": "0"}
    )
