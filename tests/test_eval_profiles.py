from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.runnables import RunnableLambda

from app.core.config import Settings
from app.evaluation import live, ragas_metrics
from app.evaluation import run as evaluation
from app.models.answer import AnswerDraft, AnswerResponse
from app.models.evaluation import METRIC_NAMES
from app.models.retrieval import RetrieveResponse


def evidence() -> RetrieveResponse:
    return RetrieveResponse.model_validate(
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


def test_batch_scrubs_input_before_generation_judge_records_and_traces(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    settings = settings.model_copy(
        update={
            "chat_base_url": "http://127.0.0.1:4000/v1",
            "chat_api_mode": "chat_completions",
            "eval_judge_model": "fixed-judge",
        }
    )
    case = evaluation.load_cases(Path("app/evaluation/datasets/answer.jsonl"))[0]
    case = case.model_copy(
        update={
            "input": case.input.model_copy(
                update={
                    "query": "asha.rao@example.com phone 98765 43210: limit?",
                }
            )
        }
    )
    captured: list[str] = []
    configs: list[Settings] = []
    model = Mock()

    def structured(schema: Any, **_: Any) -> RunnableLambda:
        def respond(prompt: Any) -> dict[str, Any]:
            captured.append(prompt.to_string())
            return (
                {
                    "status": "answered",
                    "answer": "7.5 crore [1]",
                    "evidence": [{"evidence_id": 1, "quote": "7.5 crore"}],
                }
                if schema is AnswerDraft
                else {"correctness": 1, "groundedness": 1, "rationale": "Offline fixture"}
            )

        return RunnableLambda(respond)

    model.with_structured_output.side_effect = structured

    def factory(config: Settings) -> Any:
        configs.append(config)
        return model

    monkeypatch.setattr(evaluation, "get_chat_model", factory)
    retrieve = AsyncMock(return_value=evidence())
    monkeypatch.setattr(evaluation, "retrieve_policy", retrieve)
    monkeypatch.setattr(evaluation, "resolve_reference_contexts", lambda *_: ["Reference"])
    records = asyncio.run(evaluation.collect_records([case], settings))
    all_text = str(captured) + str(records) + str(retrieve.await_args)
    assert "asha.rao" not in all_text and "98765" not in all_text
    assert "[REDACTED_EMAIL]" in records[0]["user_input"]
    assert configs[1].chat_model == "fixed-judge"
    assert configs[1].chat_base_url == "https://api.openai.com/v1"
    assert configs[1].chat_api_mode == "responses"


def test_live_metrics_hold_judge_and_metric_embeddings_fixed(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    candidate = settings.model_copy(
        update={
            "chat_model": "qwen3.5:9b-mlx",
            "chat_base_url": "http://127.0.0.1:4000/v1",
            "chat_api_mode": "chat_completions",
            "embedding_model": "nexa-embed-local",
            "embedding_dimensions": 1024,
            "embedding_base_url": "http://127.0.0.1:4000/v1",
            "embedding_profile": "qwen3-local",
            "eval_judge_model": "fixed-judge",
        }
    )
    factories = [Mock(return_value=object()), Mock(return_value=object())]
    monkeypatch.setattr(live, "get_chat_model", factories[0])
    monkeypatch.setattr(live, "get_embeddings", factories[1])
    scorer = SimpleNamespace(
        metrics={
            name: SimpleNamespace(ascore=AsyncMock(return_value=SimpleNamespace(value=0.8)))
            for name in METRIC_NAMES
        }
    )
    monkeypatch.setattr(ragas_metrics, "RagasScorer", lambda *_: scorer)
    answer = AnswerResponse(
        as_of="2026-10-01",
        status="answered",
        answer="7.5 crore",
        citations=[],
        retrieval_timings=evidence().timings,
        generation_ms=1,
    )
    scores = asyncio.run(live.score_answer("Limit?", answer, ["7.5 crore"], "7.5 crore", candidate))
    assert all(score.status == "scored" for score in scores.values())
    judge = factories[0].call_args.args[0]
    embed = factories[1].call_args.args[0]
    assert judge.chat_base_url == embed.embedding_base_url == "https://api.openai.com/v1"
    assert embed.embedding_model == "text-embedding-3-small" and embed.embedding_dimensions == 1536


def test_comparison_refuses_changed_evaluator_profile() -> None:
    from app.evaluation.compare import compare_runs

    old = {
        "status": "completed",
        "dataset_sha256": "fixture",
        "judge_model": "fixed",
        "judge_prompt_version": "v1",
        "ragas_version": "fixture",
        "evaluation_profiles": {"metric_embedding_model": "fixed-embedding"},
        "records": [
            {
                "case_id": "1",
                "judge": {
                    "correctness": 1,
                    "groundedness": 1,
                    "status_matches": True,
                },
            }
        ],
        "ragas": {"means": {"faithfulness": 1}},
    }
    new = {**old, "evaluation_profiles": {"metric_embedding_model": "different"}}
    with pytest.raises(ValueError, match="evaluation_profiles"):
        compare_runs(old, new, 0.05)
