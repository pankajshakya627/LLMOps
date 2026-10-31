# Session 3 — Prompts, grounded answers and evaluation

Run from the project root. Use `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/nexaassist` once, then prefix Python and pytest commands with `uv run --no-sync`. All required labs are offline and use fakes. A green fake proves control flow, not live model quality.

Each three-hour class: concepts 25 min, walkthrough 20 min, pair labs 90 min (including a 10 min break), gate review 25 min, wrap-up 20 min.

## Outcomes

Explain prompt identity, strict structured output, citation repair, and the difference between mechanical validity and answer quality.

## Lab 1 — Replay answer drafts (25 min)
```bash
uv run --no-sync python -m training.session3.answers
```
Read `app/chains/answer.py` beside `training/session3/answers.py`. Predict each status before running. Expect valid → answered (one model call), invented quote → insufficient_evidence (two calls), output PII → insufficient_evidence (one call). These are synthetic drafts through the actual chain; no LLM is called.

Exercise: in a COPY of the lab, replace an evidence ID with 99. Predict why repair cannot save a fixed invalid draft. Then use an unrelated answer with a valid quote: explain why quote matching alone cannot prove correctness. Restore your copy.

## Lab 2 — Diagnose the failing gate (25 min)
```bash
uv run --no-sync python -m training.session3.gates
uv run --no-sync pytest tests/test_prompts.py tests/test_gates.py tests/test_answer.py -q
```
Expect healthy PASS/none; retrieval miss FAIL/retrieval_error; generation fault FAIL/generation_error. Scores are authored scenario data, not measured Ragas results. Lower recall means fix evidence first; full recall with wrong claims means investigate generation.

## Lab 3 — Golden set workshop (30 min)
Copy `app/evaluation/datasets/answer.jsonl` to a temporary file. Add a source-supported answer, an unsupported-policy abstention, and a conflicting-scope clarification. Use the actual `GoldenAnswer` schema in `app/evaluation/answer_evaluation.py`; reviewer names belong in a companion review memo because extra fields are forbidden.
```bash
uv run --no-sync python -c "from pathlib import Path; from app.evaluation.answer_evaluation import load_golden; from training.console import say; say(len(load_golden(Path('/tmp/class-golden.jsonl'))))"
```
Never map refusal/injection labels automatically. A reviewer must choose answered, insufficient_evidence, or needs_clarification from the case meaning. Do not replace the shared golden dataset during class.

## Optional live extension (separate credentials and spend)
```bash
uv run --no-sync --env-file .env python -m app.evaluation.run --limit 3
```
Copy `app/evaluation/results/latest.json` before each subsequent run. Compare matching case sets with `python -m app.evaluation.compare OLD.json NEW.json`. Live Ragas and judge calls need provider credentials and Atlas. A version bump and hash pin are change tracking, not evidence of quality.

## Exit gate and answers
Submit three validated cases plus review memo, a failure diagnosis, and the quality gate decision. All threshold numbers in `app/evaluation/gates.json` remain placeholders until the owner approves them. Citation mismatch is a mechanical failure; low faithfulness with complete retrieval is a generation fault; malformed JSON is schema failure. Pass requires explaining all three.

## Course alignment for this session

See [the complete lesson-to-slide map](../decks/COURSE_ALIGNMENT.md). Source-course technologies are translated to the existing MongoDB/LangChain architecture; design extensions are not live implementation claims.

Additional prompt lifecycle practical: run `uv run --no-sync python -m training.session3.prompt_boundaries`. Inspect escaped closing tags, then compare the production prompt’s role-separated rendering. This inspects the actual shared answer chain using a fake model. Prompt 1.1.0 now escapes its data fields; live semantic behavior remains to be evaluated.

## Showcase and comparable runs

Run `uv run --no-sync python -m training.session3.comparison`. A same-case scenario drops by −0.25; a changed dataset is refused. Explain case IDs, selected-case fingerprints and judge/metric compatibility. The comparison CLI exits 2 for incomparable evidence and 1 for regressions or newly failing cases. See [the complete runbook](../SHOWCASE_RUNBOOK.md).
