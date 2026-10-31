from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.evaluation.gates import Gates, gate_failures, load_gates


def test_shipped_gates_load_and_are_marked_unconfirmed() -> None:
    gates = load_gates(Path("app/evaluation/gates.json"))
    assert gates.status == "placeholder"
    assert gates.p95_total_ms_max == 2000


def test_unknown_or_out_of_range_gate_values_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "gates.json"
    path.write_text('{"status": "confirmed", "faithfulness_min": 1.5}')
    with pytest.raises(ValidationError):
        load_gates(path)


def _report(faithfulness: float, correctness: float, matches: bool) -> dict[str, Any]:
    return {
        "ragas": {"means": {"faithfulness": faithfulness}},
        "records": [
            {
                "user_input": "q1",
                "judge": {
                    "correctness": correctness,
                    "groundedness": 1.0,
                    "status_matches": matches,
                },
            }
        ],
    }


def test_gate_failures_name_metrics_and_cases() -> None:
    gates = Gates.model_validate_json(Path("app/evaluation/gates.json").read_text())
    assert gate_failures(_report(0.9, 0.9, True), gates) == []
    failures = gate_failures(_report(0.5, 0.9, False), gates)
    metrics = {item["metric"] for item in failures if "metric" in item}
    assert {"faithfulness", "status_match_rate"} <= metrics
    assert {"case": "q1"} in failures
