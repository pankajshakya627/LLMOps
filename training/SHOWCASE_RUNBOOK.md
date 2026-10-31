# NexaAssist LLMOps showcase

Use these five agreed scenarios: dated policies/amendments, refusal and injection handling, quality regressions, serving failures, and reviewed feedback becoming a regression case. Session 1 establishes the trusted-source contract; Session 3 demonstrates both safety controls and quality gates.

## Start here

Run from the repository root using the existing Python environment:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/nexaassist
uv run --no-sync python -m training.showcase
# Or one class:
uv run --no-sync python -m training.showcase --session 3
```

Required demonstrations make no live model, Atlas or Phoenix calls. They invoke the application code with clearly identified fakes. A fixture answer or authored score does not measure live model quality, retrieval ranking, latency or capacity.

| Class | Live demonstration in the room | Code to open | Expected evidence | Pair task |
|---|---|---|---|---|
| 1 — Discover | `training.session1.tamper` | `app/services/ingestion.py` | Eight original sources verified; changed copy rejected by SHA-256 | Explain source identity, authority and the release decision |
| 2 — Data and retrieval | `training.session2.policy_dates` | `app/chains/retrieval.py`, `app/database/retrieval.py`, `app/chains/answer.py` | June fee 0.35% cites POL-HL-V3; July fee 0.30% cites CIR-2026-07; wrong product abstains | Inspect the complete circular, including caps and sanction applicability |
| 3 — Prompts and evaluation | `training.session3.prompt_boundaries`, `answers`, `comparison` | `app/chains/prompts/answer.py`, `app/evaluation/run.py`, `app/evaluation/compare.py` | Escaped tags remain data; invented quotes abstain after one repair; detected output PII is blocked; same-set score drop −0.25; different dataset refused | Diagnose syntax, retrieval, generation and comparison failures separately |
| 4 — Serving | `training.session4.serving` | `app/api/answer.py`, `app/api/limits.py`, `app/services/retrieval.py`, `app/database/mongo.py` | Provider failures then quota: 503, 503, 429; invalid input 422; readiness unavailable 503 | Preserve response privacy; distinguish liveness, readiness and capacity |
| 5 — Feedback and operations | `training.session5.feedback_loop`, `incident` | `app/services/feedback.py`, `app/api/feedback.py`, `app/ui/app.py`, `app/evaluation/slo_check.py` | Unauthenticated export 401; pending review 409; accepted plus curated target 200; valid JSONL and review bundle; missing measurements stay unknown | Keep a reviewed case, diagnosis and rollback record |

Session 1 uses 16 slides and runs its demonstration on slide 14. Session 2 now has 19 slides: RAGOps ingestion is on slide 4, the policy-date/recall baseline on slide 6, observability on slide 9, evals on slide 12, gateway experiments on slide 15 and security/output validation on slides 17–18. Its [live tool guide](session2/live_practicals.md) adds Phoenix, Ragas, LiteLLM and Guardrails AI exercises. Sessions 3–5 open with their scenario and command, followed by code and debrief on slides 4–5. Across all decks, notes retain sources, expected results and limitations. Use the session handout for the rest of the three-hour class.

## Dated policy walkthrough

The date demonstration verifies the registered source files, parses the actual PDFs, ingests them through the real chain, and uses its date/product filters, parent expansion and linked amendment loader. Mongo transport, embeddings, ranking and model drafts are fixtures. The model fixture emits citations that the application must validate.

Change one input at a time. Both the lookup and sanction dates are explicit in the June/July examples. A July policy lookup does not automatically change a June sanction's fee. POL-HL-V3 clause 6.2 and CIR-2026-07 clauses 3.1/5.1 supply the fee and applicability. Inspect the full instrument rather than using a similarity score as a precedence rule.

## Reviewer screen walkthrough

In an already configured running app, open **Review feedback**, enter the reviewer token and load the queue. Review the actual source before accepting a signal. An accepted item now shows **Verified reference answer**, **Expected outcome** and **Source clauses**. The target starts blank; no answer or correction is copied automatically.

Enter one source per line, for example:

```text
POL-HL-V3 | 4.1
CIR-2026-07 | 5.1
```

Choose references relevant to your question; these lines illustrate the format. A blank clause means a complete document. Export, then download both the JSONL case and the review bundle. The API checks authentication, institution, accepted stored review, exact request match, required source references for an answered case, strict fields and detected PII. It does not verify semantic truth or append to the shared golden set.

The API is `POST /feedback/{feedback_id}/golden`. Its request is a strict `GoldenAnswer` (`input`, `expected_output`, `context`, `expected_status`); its response contains `case` and `review`. The audit includes feedback ID, institution, reviewer, review note, export time and case fingerprint. Recompute that fingerprint with SHA-256 of `GoldenAnswer.model_dump_json().encode()`; it is a normalized model fingerprint, not a hash of a formatted download file.

Validate an exported file before proposing it for review:

```bash
uv run --no-sync python -c "from pathlib import Path; from app.evaluation.answer_evaluation import load_golden; from training.console import say; say(len(load_golden(Path('/tmp/reviewed.jsonl'))))"
```

Keep the review bundle beside it. An SME chooses the expected outcome and source-supported target. Existing `refuse` and injection category mappings have not been changed. After dataset review, the normal evaluation command can replay the case against configured live services; that is an optional credentialed exercise with model spend.

## Release comparison walkthrough

`app.evaluation.run` now records case IDs, a fingerprint of the selected reviewed cases, and answer-prompt identity. Case identity includes the full scoped request and expected output/status/source references. Reordering cases does not change the set fingerprint. Repeated question text at different dates does not merge cases.

```bash
uv run --no-sync python -m app.evaluation.compare OLD.json NEW.json
```

Exit 0 means no detected regression, 1 means aggregate regression or a newly failing case, and 2 means incomparable or malformed evidence. Both runs must be completed and nonempty, with the same dataset/case IDs, judge model and prompt version, Ragas version and metric names. Scores must be finite. Legacy reports lacking these fields must be regenerated. Keep retrieval configuration and corpus identity in the release record when interpreting a deliberate experiment.

## Implementation in this revision

- Prompt **1.1.0**: XML data fields, escaping of all human-message variables, a closing output reminder, updated fingerprint pin and provenance. Exact source quotes remain unmodified for validation.
- Evaluation: scoped case IDs and dataset fingerprint; compatible-evidence checks; stable per-case comparisons; failed case flips block the CLI even when averages hide them.
- Feedback: scoped record lookup, authenticated curated export, an audit bundle, and reviewer downloads in Streamlit.
- Training: actual-PDF date demo, production-prompt inspection, comparison drill, feedback loop and one instructor command for all five classes.

The existing output PII rail, source hashing, rate limiting and readiness deadline remain part of the demonstrations. Regex PII detection covers selected identifiers; it is not comprehensive. Escaping preserves structure; live prompt-injection behavior remains unverified. Feedback records still contain client-supplied response objects, and the reviewer bearer token is shared rather than an individually verified identity. Dataset promotion, CI, durable conversation memory, streaming and blue/green index promotion are separate work.

## Teaching evidence

Ask each pair to submit the input, predicted behavior, observed transcript, relevant source/code reference, diagnosis, and release decision. Keep authored metrics visibly labeled. Do not lower the placeholder gate thresholds to make a lab pass.

Source concepts: [Educative LLMOps](https://www.educative.io/courses/llmops), with [lesson coverage](decks/COURSE_ALIGNMENT.md). The selected lessons were reread in signed-in Safari for this implementation. No raw lesson text is redistributed.
