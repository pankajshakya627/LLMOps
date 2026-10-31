"""Synthetic quality reports evaluated by the production gate, offline."""

from __future__ import annotations

from pathlib import Path

from app.evaluation.gates import gate_failures, load_gates
from app.evaluation.retrieval_eval import classify_failure
from training.console import say


def main() -> None:
    gates = load_gates(Path("app/evaluation/gates.json"))
    for name, recall, faithfulness in (
        ("healthy", 1.0, 1.0),
        ("retrieval miss", 0.0, 0.5),
        ("generation fault", 1.0, 0.5),
    ):
        judge = {"correctness": faithfulness, "groundedness": faithfulness, "status_matches": True}
        report = {
            "ragas": {"means": {"faithfulness": faithfulness}},
            "records": [{"user_input": "synthetic query", "judge": judge}],
        }
        failures = gate_failures(report, gates)
        kind = classify_failure("answered", recall, judge)
        assert bool(failures) == (name != "healthy")
        say(f"{name}: gate={'FAIL' if failures else 'PASS'}, failure_type={kind}")
    say("Synthetic scores demonstrate gate logic; no judge or model was called.")


if __name__ == "__main__":
    main()
