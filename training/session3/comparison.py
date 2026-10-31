"""Use the production comparison gate with visibly synthetic score reports."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

from app.evaluation.compare import compare_runs
from app.evaluation.run import case_fingerprint, load_cases
from training.console import say


def scenario_report(faithfulness: float) -> dict[str, Any]:
    case = load_cases(Path("app/evaluation/datasets/answer.jsonl"))[0]
    identifier = case_fingerprint(case)
    return {
        "status": "completed",
        "dataset_sha256": hashlib.sha256(identifier.encode()).hexdigest(),
        "judge_model": "offline-fixture",
        "judge_prompt_version": "fixture-v1",
        "ragas_version": "fixture-v1",
        "ragas": {"means": {"faithfulness": faithfulness}},
        "records": [
            {
                "case_id": identifier,
                "user_input": case.input.query,
                "judge": {"correctness": 1.0, "groundedness": 1.0, "status_matches": True},
                "failure_type": "none",
            }
        ],
    }


def main() -> None:
    old, candidate = scenario_report(0.95), scenario_report(0.70)
    result = compare_runs(old, candidate, 0.05)
    assert result["deltas"]["faithfulness"] == -0.25
    assert result["regressions"]
    say("same reviewed cases: faithfulness delta=-0.25; hold candidate")
    mismatched = copy.deepcopy(candidate)
    mismatched["dataset_sha256"] = "a-different-reviewed-set"
    try:
        compare_runs(old, mismatched, 0.05)
    except ValueError as exc:
        say("different dataset: comparison refused:", exc)
    else:
        raise AssertionError("Mismatched evaluations must not produce a passing comparison")
    say("Scores are fixtures; case identity comes from the actual local golden set.")


if __name__ == "__main__":
    main()
