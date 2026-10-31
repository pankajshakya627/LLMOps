from __future__ import annotations

import hashlib
import re

from app.chains.prompts.answer import ANSWER_PROMPT, ANSWER_PROMPT_SHA, ANSWER_PROMPT_VERSION
from app.chains.prompts.judge import JUDGE_PROMPT, JUDGE_VERSION

# Prompt regression pins. Editing a prompt changes its fingerprint and fails the test.
# To accept the change: bump the version constant, then update the pair below and record
# the reason. Re-run the golden evaluation (python -m app.evaluation.run) before merging.
# 1.2.0: numeric citation example and exact numeric copying after live local draft failures.
# Live candidate results are recorded in docs/debug/closing-validation-gaps-20261025.
PINNED_ANSWER = ("1.2.0", "f29e38485765")
PINNED_JUDGE = ("policy-judge-v2", "7e6716ec19ac")


def test_answer_prompt_demonstrates_the_numeric_marker_contract() -> None:
    system = str(
        ANSWER_PROMPT.format_messages(**{name: "unused" for name in ANSWER_PROMPT.input_variables})[
            0
        ].content
    )
    assert re.search(r"\[\d+\]", system), "Show an actual numeric marker, not a literal field name"


def test_answer_prompt_text_change_requires_a_version_bump() -> None:
    assert (
        ANSWER_PROMPT_SHA == hashlib.sha256(ANSWER_PROMPT.pretty_repr().encode()).hexdigest()[:12]
    )
    assert (ANSWER_PROMPT_VERSION, ANSWER_PROMPT_SHA) == PINNED_ANSWER, (
        "Answer prompt changed: bump ANSWER_PROMPT_VERSION, update PINNED_ANSWER, re-run evals"
    )


def test_judge_prompt_text_change_requires_a_version_bump() -> None:
    sha = hashlib.sha256(JUDGE_PROMPT.pretty_repr().encode()).hexdigest()[:12]
    assert (JUDGE_VERSION, sha) == PINNED_JUDGE, (
        "Judge prompt changed: bump JUDGE_VERSION, update PINNED_JUDGE, re-run evals"
    )
