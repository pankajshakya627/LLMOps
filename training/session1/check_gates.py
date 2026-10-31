"""Lab 4: check that a thresholds file is valid before you rely on it.

Run from the project root: uv run --no-sync python -m training.session1.check_gates evaluation/gates.mine.json
Exit code 0 when valid, 1 when a field is unknown, missing or out of range.
"""

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import ValidationError

from app.evaluation.gates import load_gates
from training.console import say


def main() -> int:
    if len(sys.argv) != 2:
        say("usage: python -m training.session1.check_gates PATH_TO_GATES_JSON")
        return 2
    try:
        gates = load_gates(Path(sys.argv[1]))
    except ValidationError as error:
        for problem in error.errors(include_url=False, include_input=False):
            say("INVALID:", ".".join(str(part) for part in problem["loc"]), "-", problem["msg"])
        return 1
    say(f"valid: status={gates.status} p95_total_ms_max={gates.p95_total_ms_max}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
