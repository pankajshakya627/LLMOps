"""Instructor entry point: run all five offline showcases, or one session."""

from __future__ import annotations

import argparse
import subprocess
import sys

from training.console import say

DEMOS = {
    1: ("Trusted evidence", ["training.session1.tamper"]),
    2: ("Dated policies and amendments", ["training.session2.policy_dates"]),
    3: (
        "Prompt controls and quality regressions",
        [
            "training.session3.prompt_boundaries",
            "training.session3.answers",
            "training.session3.comparison",
        ],
    ),
    4: ("Serving failures and resource limits", ["training.session4.serving"]),
    5: (
        "Reviewed feedback and incident recovery",
        ["training.session5.feedback_loop", "training.session5.incident"],
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=int, choices=DEMOS)
    selected = parser.parse_args().session
    for number, (title, modules) in DEMOS.items():
        if selected is None or selected == number:
            say(f"\nSESSION {number}: {title} — OFFLINE")
            sys.stdout.flush()
            for module in modules:
                subprocess.run([sys.executable, "-m", module], check=True, timeout=180)


if __name__ == "__main__":
    main()
