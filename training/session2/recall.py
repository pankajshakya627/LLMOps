"""Lab 5: score hand-made retrieval results with recall@k and MRR.

Run from the project root: uv run --no-sync python -m training.session2.recall
No network, database or model key is used.
"""

from __future__ import annotations

from datetime import date

from app.evaluation.answer_evaluation import ExpectedEvidence
from app.evaluation.retrieval_eval import score_retrieval
from app.models.retrieval import Citation, RetrieveHit, RetrieveResponse, RetrieveTimings
from training.console import say


def hit(rank: int, doc_id: str, clause: str | None) -> RetrieveHit:
    citation = Citation(
        doc_id=doc_id,
        title="t",
        policy_version="1",
        clause=clause,
        effective_date=date(2025, 10, 1),
    )
    return RetrieveHit(rank=rank, score=1 / rank, text="t", parent_text="t", citation=citation)


def response(results, amendments=()):
    return RetrieveResponse(
        as_of=date(2026, 10, 1),
        results=list(results),
        amendments=list(amendments),
        timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
    )


# Case: "What is the maximum loan amount?"  Expected evidence: POL-HL-V3 clause 4.1
want = [ExpectedEvidence(doc_id="POL-HL-V3", clause="4.1")]
scenarios = {
    "A: right clause is rank 1": response([hit(1, "POL-HL-V3", "4.1"), hit(2, "POL-HL-V3", "3.4")]),
    "B: right clause is rank 4": response(
        [
            hit(1, "POL-HL-V3", "3.4"),
            hit(2, "POL-HL-V3", "3.1"),
            hit(3, "POL-HL-V2", "4.1"),
            hit(4, "POL-HL-V3", "4.1"),
        ]
    ),
    "C: only the old version found": response(
        [hit(1, "POL-HL-V2", "4.1"), hit(2, "POL-HL-V1", "4.1")]
    ),
    "D: empty result": response([]),
}
for k in (1, 3, 5):
    say(f"--- k={k}")
    for name, resp in scenarios.items():
        s = score_retrieval(resp, want, k=k)
        say(
            f"  {name:<32} recall@k={s['recall_at_k']:.1f}  mrr={s['mrr']:.2f}  missing={s['missing']}"
        )

# Case with two required passages (the fee question needs the circular's clauses 3.1 and 5.1)
fee = [
    ExpectedEvidence(doc_id="CIR-2026-07", clause="3.1"),
    ExpectedEvidence(doc_id="CIR-2026-07", clause="5.1"),
]
partial = response([hit(1, "POL-HL-V3", "6.2"), hit(2, "CIR-2026-07", "3.1")])
say("\nfee question, only one of two needed clauses found:", score_retrieval(partial, fee, k=5))
linked = response([hit(1, "POL-HL-V3", "6.2")], amendments=[hit(1, "CIR-2026-07", None)])
say("fee question, circular delivered whole as an amendment:", score_retrieval(linked, fee, k=5))
