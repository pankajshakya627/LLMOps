# Session 5 — Operate, review feedback and rehearse rollback

Run from the project root. Use `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/nexaassist` once, then prefix Python and pytest commands with `uv run --no-sync`. All required labs are offline and use fakes. A green fake proves control flow, not live model quality.

Each three-hour class: concepts 25 min, walkthrough 20 min, pair labs 90 min (including a 10 min break), gate review 25 min, wrap-up 20 min.

## Outcomes

Explain operational traces versus semantic evaluation, curate reviewed failures, compare releases fairly, and rehearse a reversible rollback.

## Lab 1 — Incident drill (25 min)
```bash
uv run --no-sync python -m training.session5.incident
```
Expect no traffic → all SLOs not_measured; scenario p95 2500 ms and hallucination proxy 0.15 → failures under the shipped placeholder gates; faithfulness replay delta −0.25 → regression. The drill calls production checkers with synthetic data and does not deploy or change a database.

Exercise: change sampled_count to 0 and sampled_hallucination_rate to None. Explain why missing observation cannot clear a safety incident. Change p95 only and distinguish operational recovery from answer-quality recovery.

## Lab 2 — Feedback governance (25 min)
```bash
uv run --no-sync pytest tests/test_feedback.py tests/test_sampling.py tests/test_compare.py -q
```
Read `app/models/feedback.py`, `app/services/feedback.py`, and `app/api/feedback.py`. Follow pending → accepted/rejected, reviewer authentication, stable feedback IDs and answer provenance. The submitted response is client supplied; provenance is useful context, not a cryptographic proof. Feedback is a signal; a thumbs-down is not a reference answer.

Take a COPIED golden case, write a corrected response against the real policy clause, and validate it with `load_golden` as in Session 3. Add a separate memo recording feedback reference, source, verifier, and reason. Run `uv run --no-sync python -m training.session5.feedback_loop`. The authenticated export requires an accepted stored review and a separately curated target for the same request. Download the validated JSONL and review bundle from the reviewer screen; dataset promotion remains a reviewed manual step. No existing refusal/injection mapping is silently changed.

## Lab 3 — Rollback tabletop (30 min)
Write a release file naming prompt ID/version/hash, model and embedding configuration, dimensions, collection/index/parent collection, golden dataset hash, quality report, SLO report, approver and rollback owner. Use exact IDs from your environment; do not invent a release tag when this folder has no Git metadata.

Sequence: hold candidate → record symptom and trace → restore the known-good app/prompt/retrieval configuration → replay failing and golden cases → collect representative SLO traffic → obtain release decision. Changing VECTOR_INDEX_NAME alone does not isolate data: ingestion writes the configured collection and parent store. Blue/green needs separate compatible chunk AND parent collections and a tested configuration switch. This course supplies a tabletop; no index promotion script or database mutation is performed.

## Optional Phoenix demonstration
Follow [the Phoenix guide](../../app/observability/README.md) and inspect HTTP/runnable/model
spans, prompt versions, token counts and explicit Ragas annotations.
`LIVE_EVAL_SAMPLE_RATE=0` disables sampled judging; a nonzero rate spends model
tokens. Sampled faithfulness uses cited quotes and remains a limited proxy.

## Exit gate and answer key
Submit incident timeline, curated-case memo, release file and rollback evidence. Fail closed on missing required measurements. The comparison now rejects mismatched case/dataset fingerprints, judge identities and metric sets. Inspect the experiment configuration and corpus before interpreting compatible deltas. Agents, memory, query rewriting and streaming remain future scope until they have a separate requirement and evaluation plan.

## Course alignment for this session

See [the complete lesson-to-slide map](../decks/COURSE_ALIGNMENT.md). Source-course technologies are translated to the existing MongoDB/LangChain architecture; design extensions are not live implementation claims.

Additional orchestration practical: run `uv run --no-sync python -m training.session5.memory_design`. Explain how a two-message fixture loses earlier scope and why a rewrite fallback still leaves ambiguity. This is a design simulation, not durable memory.

See [the showcase runbook](../SHOWCASE_RUNBOOK.md) for the reviewer screen and API walkthrough. No token → 401; pending/rejected review → 409; accepted review with a curated valid target → 200.
