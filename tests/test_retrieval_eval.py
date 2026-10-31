from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from app.core.config import Settings
from app.evaluation import retrieval_eval
from app.evaluation.answer_evaluation import ExpectedEvidence
from app.evaluation.retrieval_eval import classify_failure, score_retrieval
from app.models.retrieval import Citation, RetrieveHit, RetrieveResponse, RetrieveTimings


def _hit(doc_id: str, clause: str | None, rank: int = 1) -> RetrieveHit:
    return RetrieveHit(
        rank=rank,
        score=0.5,
        text="t",
        parent_text="t",
        citation=Citation(
            doc_id=doc_id,
            title="T",
            policy_version="1",
            clause=clause,
            effective_date=date(2025, 10, 1),
        ),
    )


def _response(
    results: list[RetrieveHit], amendments: list[RetrieveHit] | None = None
) -> RetrieveResponse:
    return RetrieveResponse(
        as_of=date(2026, 10, 1),
        results=results,
        amendments=amendments or [],
        timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
    )


def test_score_retrieval_reports_recall_mrr_and_missing_references() -> None:
    expected = [
        ExpectedEvidence(doc_id="POL-HL-V3", clause="4.1"),
        ExpectedEvidence(doc_id="POL-HL-V3", clause="7.2"),
    ]
    response = _response([_hit("POL-HL-V3", "3.4", 1), _hit("POL-HL-V3", "7.2", 2)])
    score = score_retrieval(response, expected, k=5)
    assert score["recall_at_k"] == 0.5
    assert score["mrr"] == 0.5
    assert score["missing"] == [{"doc_id": "POL-HL-V3", "clause": "4.1"}]


def test_score_retrieval_respects_k_and_counts_linked_circulars() -> None:
    expected = [ExpectedEvidence(doc_id="CIR-2026-07", clause="3.1")]
    late = _response([_hit("POL-HL-V3", "3.4", 1), _hit("CIR-2026-07", "3.1", 2)])
    assert score_retrieval(late, expected, k=1)["recall_at_k"] == 0
    assert score_retrieval(late, expected, k=2)["recall_at_k"] == 1
    # A complete linked circular has no clause but contains every clause.
    linked = _response([_hit("POL-HL-V3", "3.4")], [_hit("CIR-2026-07", None)])
    assert score_retrieval(linked, expected, k=1)["recall_at_k"] == 1


def test_classify_failure_separates_retrieval_from_generation() -> None:
    good = {"correctness": 1.0, "groundedness": 1.0, "status_matches": True}
    bad = {"correctness": 0.0, "groundedness": 1.0, "status_matches": True}
    assert classify_failure("answered", 1.0, good) == "none"
    assert classify_failure("answered", 0.5, bad) == "retrieval_error"
    assert classify_failure("answered", 1.0, bad) == "generation_error"
    assert classify_failure("insufficient_evidence", None, bad) == "generation_error"


def test_empty_reference_is_rejected_instead_of_reporting_successful_recall() -> None:
    with pytest.raises(ValueError, match="at least one"):
        score_retrieval(_response([]), [], k=1)


def test_retrieval_harness_skips_unanswerable_cases_and_aggregates_actual_hits(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
) -> None:
    retrieve = AsyncMock(return_value=_response([]))
    monkeypatch.setattr(retrieval_eval, "retrieve_policy", retrieve)
    report = asyncio.run(retrieval_eval.run(Path("app/evaluation/datasets/answer.jsonl"), settings, 5))
    assert report["case_count"] == 8
    assert retrieve.await_count == 8
    assert report["mean_recall_at_k"] == report["mean_mrr"] == 0
    assert all(row["missing"] for row in report["cases"])
