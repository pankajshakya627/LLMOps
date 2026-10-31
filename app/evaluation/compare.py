"""Compare two saved evaluation runs to see whether quality drifted between them.

    python -m app.evaluation.compare OLD.json NEW.json

Exits 1 when an aggregate metric drops by more than the tolerance in app/evaluation/gates.json.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import structlog

from app.core.logging import configure_logging
from app.evaluation.gates import load_gates

ROOT = Path(__file__).resolve().parents[2]


def aggregates(report: dict[str, Any]) -> dict[str, float]:
    records = report["records"]
    values: dict[str, float] = dict(report["ragas"]["means"])
    if records:
        for key in ("correctness", "groundedness"):
            values[f"judge_{key}"] = sum(r["judge"][key] for r in records) / len(records)
        values["status_match_rate"] = sum(r["judge"]["status_matches"] for r in records) / len(
            records
        )
    return values


def compare_runs(old: dict[str, Any], new: dict[str, Any], tolerance: float) -> dict[str, Any]:
    if not math.isfinite(tolerance) or not 0 <= tolerance <= 1:
        raise ValueError("Tolerance must be finite and between 0 and 1")
    for report in (old, new):
        if report.get("status") != "completed" or not report.get("records"):
            raise ValueError("Comparison requires two completed, nonempty evaluation runs")
        ids = [record.get("case_id") for record in report["records"]]
        if not all(ids) or len(set(ids)) != len(ids):
            raise ValueError("Comparison requires unique case IDs; regenerate legacy reports")
    for field in ("dataset_sha256", "judge_model", "judge_prompt_version", "ragas_version"):
        if not old.get(field) or old[field] != new.get(field):
            raise ValueError(f"Incomparable evaluation runs: {field} is missing or differs")
    if old.get("evaluation_profiles") != new.get("evaluation_profiles"):
        raise ValueError("Incomparable evaluation runs: evaluation_profiles differ")
    if {r["case_id"] for r in old["records"]} != {r["case_id"] for r in new["records"]}:
        raise ValueError("Evaluation case sets differ")
    before, after = aggregates(old), aggregates(new)
    if before.keys() != after.keys():
        raise ValueError("Evaluation metric sets differ")
    if any(
        not math.isfinite(value) or not 0 <= value <= 1
        for value in (*before.values(), *after.values())
    ):
        raise ValueError("Evaluation scores must be finite and between 0 and 1")
    deltas = {name: after[name] - before[name] for name in before}
    previous = {r["case_id"]: r.get("failure_type") for r in old["records"]}
    return {
        "deltas": {name: round(delta, 4) for name, delta in sorted(deltas.items())},
        "regressions": [
            {"metric": name, "before": before[name], "after": after[name]}
            for name, delta in sorted(deltas.items())
            if delta < -tolerance
        ],
        "flipped_cases": [
            {
                "case_id": r["case_id"],
                "case": r["user_input"],
                "before": previous[r["case_id"]],
                "after": r["failure_type"],
            }
            for r in new["records"]
            if previous[r["case_id"]] == "none" and r.get("failure_type") != "none"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two evaluation run reports")
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--gates", type=Path, default=ROOT / "app/evaluation/gates.json")
    args = parser.parse_args()
    configure_logging("INFO")
    tolerance = load_gates(args.gates).regression_tolerance
    try:
        result = compare_runs(
            json.loads(args.old.read_text()), json.loads(args.new.read_text()), tolerance
        )
    except (ValueError, KeyError, TypeError) as exc:
        structlog.get_logger().error("evaluation_comparison_refused", reason=str(exc))
        raise SystemExit(2) from None
    structlog.get_logger().info("evaluation_comparison", **result)
    if result["regressions"] or result["flipped_cases"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
