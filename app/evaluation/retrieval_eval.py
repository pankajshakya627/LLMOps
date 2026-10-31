"""Retrieval-only evaluation: no model calls beyond the query embedding.

    python -m app.evaluation.retrieval_eval [--k 5] [--min-recall 0.85]

Compare configurations by setting RETRIEVAL_MODE / RERANK_ENABLED in the environment.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import structlog

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.evaluation.answer_evaluation import ExpectedEvidence, load_golden
from app.models.retrieval import RetrieveHit, RetrieveResponse
from app.services.retrieval import retrieve_policy

ROOT = Path(__file__).resolve().parents[2]
FailureType = Literal["none", "retrieval_error", "generation_error"]


def _matches(hit: RetrieveHit, reference: ExpectedEvidence, *, complete: bool) -> bool:
    # A linked circular is loaded whole (clause None), so it carries every clause it contains.
    return hit.citation.doc_id == reference.doc_id and (
        complete or reference.clause is None or hit.citation.clause == reference.clause
    )


def score_retrieval(
    response: RetrieveResponse, expected: Sequence[ExpectedEvidence], k: int
) -> dict[str, Any]:
    """Recall@k and reciprocal rank of the first expected reference, over top-k plus amendments."""
    if not expected:
        raise ValueError("Expected evidence must contain at least one reference")
    ranked = [(hit, False) for hit in response.results[:k]]
    ranked += [(hit, True) for hit in response.amendments]
    ranks: list[int | None] = []
    missing = []
    for reference in expected:
        found = [
            position
            for position, (hit, complete) in enumerate(ranked, 1)
            if _matches(hit, reference, complete=complete)
        ]
        ranks.append(min(found) if found else None)
        if not found:
            missing.append({"doc_id": reference.doc_id, "clause": reference.clause})
    found_ranks = [rank for rank in ranks if rank is not None]
    return {
        "recall_at_k": len(found_ranks) / len(expected),
        "mrr": 1 / min(found_ranks) if found_ranks else 0.0,
        "missing": missing,
    }


def classify_failure(
    expected_status: str, recall: float | None, judge: dict[str, Any]
) -> FailureType:
    """A failed case is a retrieval error when expected evidence was not retrieved."""
    failed = not judge["status_matches"] or judge["correctness"] < 1 or judge["groundedness"] < 1
    if not failed:
        return "none"
    if expected_status == "answered" and recall is not None and recall < 1:
        return "retrieval_error"
    return "generation_error"


async def run(path: Path, settings: Settings, k: int) -> dict[str, Any]:
    cases = [c for c in load_golden(path) if c.expected_status == "answered" and c.context]
    rows = []
    for case in cases:
        response = await retrieve_policy(case.input, settings)
        rows.append({"query": case.input.query, **score_retrieval(response, case.context, k)})
    return {
        "captured_at": datetime.now(UTC).isoformat(),
        "dataset": str(path),
        "k": k,
        "retrieval_mode": settings.retrieval_mode,
        "rerank_enabled": settings.rerank_enabled,
        "case_count": len(rows),
        "mean_recall_at_k": sum(r["recall_at_k"] for r in rows) / len(rows) if rows else 0.0,
        "mean_mrr": sum(r["mrr"] for r in rows) / len(rows) if rows else 0.0,
        "cases": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieval-only recall@k and MRR")
    parser.add_argument("--dataset", type=Path, default=ROOT / "app/evaluation/datasets/answer.jsonl")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "app/evaluation/results/retrieval.json"
    )
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--min-recall", type=float, help="Exit 1 below this mean recall@k")
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k must be positive")
    configure_logging("INFO")
    report = asyncio.run(run(args.dataset, get_settings(), args.k))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    structlog.get_logger().info(
        "retrieval_evaluation_completed",
        output=str(args.output),
        mean_recall_at_k=report["mean_recall_at_k"],
        mean_mrr=report["mean_mrr"],
    )
    if args.min_recall is not None and report["mean_recall_at_k"] < args.min_recall:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
