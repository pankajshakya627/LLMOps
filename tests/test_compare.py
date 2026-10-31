from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from app.evaluation import compare
from app.evaluation.compare import compare_runs


def _run(faithfulness: float, correctness: float, matches: bool = True) -> dict[str, Any]:
    return {
        "status": "completed",
        "dataset_sha256": "same-reviewed-dataset",
        "judge_model": "fixture-judge",
        "judge_prompt_version": "fixture-v1",
        "ragas_version": "fixture-v1",
        "ragas": {"means": {"faithfulness": faithfulness}},
        "records": [
            {
                "case_id": "case-1",
                "user_input": "q1",
                "judge": {
                    "correctness": correctness,
                    "groundedness": 1.0,
                    "status_matches": matches,
                },
                "failure_type": "none" if matches and correctness == 1 else "generation_error",
            }
        ],
    }


def test_no_change_is_not_a_regression() -> None:
    result = compare_runs(_run(0.9, 1.0), _run(0.9, 1.0), tolerance=0.05)
    assert result["regressions"] == [] and result["flipped_cases"] == []


def test_drop_beyond_tolerance_and_flipped_case_are_reported() -> None:
    result = compare_runs(_run(0.9, 1.0), _run(0.8, 0.5, matches=False), tolerance=0.05)
    names = {item["metric"] for item in result["regressions"]}
    assert {"faithfulness", "judge_correctness", "status_match_rate"} <= names
    assert result["flipped_cases"] == [
        {"case_id": "case-1", "case": "q1", "before": "none", "after": "generation_error"}
    ]


def test_small_drop_within_tolerance_is_ignored() -> None:
    result = compare_runs(_run(0.9, 1.0), _run(0.87, 1.0), tolerance=0.05)
    assert result["regressions"] == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "failed"),
        ("dataset_sha256", "different"),
        ("judge_model", "different"),
        ("judge_prompt_version", "different"),
        ("ragas_version", "different"),
        ("records", []),
    ],
)
def test_incomparable_runs_are_rejected(field: str, value: Any) -> None:
    new = _run(0.9, 1.0)
    new[field] = value
    with pytest.raises(ValueError):
        compare_runs(_run(0.9, 1.0), new, 0.05)


@pytest.mark.parametrize(
    "change", ["missing_metric", "nan", "different_case", "duplicate_case", "legacy"]
)
def test_incomplete_or_ambiguous_evidence_is_rejected(change: str) -> None:
    new = _run(0.9, 1.0)
    if change == "missing_metric":
        new["ragas"]["means"] = {}
    elif change == "nan":
        new["ragas"]["means"]["faithfulness"] = float("nan")
    elif change == "different_case":
        new["records"][0]["case_id"] = "other-case"
    elif change == "duplicate_case":
        new["records"].append(new["records"][0])
    else:
        del new["dataset_sha256"]
    with pytest.raises(ValueError):
        compare_runs(_run(0.9, 1.0), new, 0.05)


def test_case_flips_use_ids_when_question_text_is_repeated() -> None:
    old = _run(0.9, 1.0)
    old["records"].append({**old["records"][0], "case_id": "different-policy-date"})
    new = _run(0.9, 1.0)
    failed = _run(0.9, 0.5)["records"][0]
    new["records"].append({**failed, "case_id": "different-policy-date"})
    assert compare_runs(old, new, 0.05)["flipped_cases"] == [
        {
            "case_id": "different-policy-date",
            "case": "q1",
            "before": "none",
            "after": "generation_error",
        }
    ]


@pytest.mark.parametrize("mismatched,code", [(False, 1), (True, 2)])
def test_comparison_cli_blocks_case_flip_or_incomparable_evidence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    mismatched: bool,
    code: int,
) -> None:
    old, new = _run(0.9, 1.0), _run(0.9, 1.0)
    new["records"][0]["failure_type"] = "generation_error"
    if mismatched:
        new["dataset_sha256"] = "different"
    before, after = tmp_path / "old.json", tmp_path / "new.json"
    before.write_text(json.dumps(old))
    after.write_text(json.dumps(new))
    monkeypatch.setattr(sys, "argv", ["compare", str(before), str(after)])
    with pytest.raises(SystemExit) as stopped:
        compare.main()
    assert stopped.value.code == code
