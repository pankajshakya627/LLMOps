# Implemented for the LLMOps showcase

## Application changes

| Path | Change |
|---|---|
| `app/chains/prompts/answer.py`, `app/chains/answer.py` | Prompt 1.1.0, escaped data fields, structured-output reminder and provenance pin |
| `app/evaluation/run.py` | Scoped case IDs, selected-case fingerprint and answer-prompt identity |
| `app/evaluation/compare.py` | Reject incompatible reports; compare stable case IDs; block case flips as well as score regressions |
| `app/database/feedback.py` | Institution-scoped read of one authoritative feedback record |
| `app/services/feedback.py`, `app/api/feedback.py` | Authenticated curated export using accepted review state; strict target, matching input, PII check and review bundle |
| `app/ui/app.py` | Blank-by-default reviewer target form and JSONL/review downloads |

These changes add no application dependencies, settings, vector-store migration, dataset remapping or deployment mutation. The output PII rail and two-second readiness deadline were implemented in the earlier training pass.

## Classroom delivery

Five updated editable decks contain 149 slides with notes, retain all sixteen course lessons, and include runnable showcases; Sessions 1–2 each have 16 slides. New labs exercise the real PDF pipeline, production prompt rendering, comparison gate and feedback API using offline dependencies. `python -m training.showcase` runs all five classes. See `SHOWCASE_RUNBOOK.md` for the exact walkthroughs and limits.

## Checks

Ruff and mypy pass. Full offline suite: 213 passed, 1 pre-existing failure because `C4-Documentation/nexaassist-architecture.html` is absent. The test was retained. UI workflows are covered by headless AppTest against the actual API with fakes. All five slide quality/export gates pass with zero warnings. Sessions 1–2 now have 16 slides each; all 32 pages were visually reviewed and their PDFs rendered. See `decks/session_1_2_verification.md`.

OpenAI, Atlas and Phoenix live behavior was not evaluated. Prompt 1.1.0 needs live golden and adversarial evaluation before a real release. Exported targets require SME source verification; accepted user feedback does not establish truth. No real-browser UI or Microsoft PowerPoint check was performed. Organizational gates and prices remain placeholders.
