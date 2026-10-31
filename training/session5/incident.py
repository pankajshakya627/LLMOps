"""Operate a synthetic incident using the real SLO and comparison functions."""

from __future__ import annotations

from pathlib import Path

from app.evaluation.compare import compare_runs
from app.evaluation.gates import load_gates
from app.evaluation.slo_check import check_slo
from training.console import say
from training.session3.comparison import scenario_report


def main() -> None:
    gates = load_gates(Path("app/evaluation/gates.json"))
    metrics: dict[str, int | float | None] = {
        "sample_count": 0,
        "sampled_count": 0,
        "p95_ms": 0,
        "answer_error_rate": 0,
        "cost_per_query_usd": None,
        "sampled_hallucination_rate": None,
    }
    results = check_slo(metrics, gates)
    assert all(row["status"] == "not_measured" for row in results)
    say("no traffic: all SLOs not_measured")
    metrics.update(
        sample_count=100,
        sampled_count=20,
        p95_ms=2500,
        cost_per_query_usd=0.005,
        sampled_hallucination_rate=0.15,
    )
    results = check_slo(metrics, gates)
    failed = [row["slo"] for row in results if row["status"] == "fail"]
    assert failed == ["p95_ms", "hallucination_rate"]
    say("incident: failed SLOs =", failed)
    old, new = scenario_report(0.95), scenario_report(0.70)
    comparison = compare_runs(old, new, gates.regression_tolerance)
    assert len(comparison["regressions"]) == 1
    say("replay: faithfulness delta =", comparison["deltas"]["faithfulness"])
    say("decision: hold release, restore known-good artifacts, replay golden cases")
    say("Scenario data only: no deployment or database was changed.")


if __name__ == "__main__":
    main()
