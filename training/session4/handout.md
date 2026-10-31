# Session 4 — Secure serving, reliability and cost

Run from the project root. Use `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/nexaassist` once, then prefix Python and pytest commands with `uv run --no-sync`. All required labs are offline and use fakes. A green fake proves control flow, not live model quality.

Each three-hour class: concepts 25 min, walkthrough 20 min, pair labs 90 min (including a 10 min break), gate review 25 min, wrap-up 20 min.

## Outcomes

Explain request validation, service boundaries, resource controls, readiness versus liveness, and meaningful SLO measurement.

## Lab 1 — Fail the actual API safely (25 min)
```bash
uv run --no-sync python -m training.session4.serving
```
The real FastAPI routes run with injected offline services. Expect liveness 200, readiness 503 with hidden details, answer statuses [503, 503, 429], invalid input 422. ASGI transport does not run lifespan; startup telemetry is tested separately. Trace each response into `app/api/answer.py`, `app/api/operations.py`, and `app/api/limits.py`.

Exercise: change the lab limit to 3 and add a fourth request; predict [503, 503, 503, 429]. Discuss why workers and proxies change effective quotas. No provider is called.

## Lab 2 — Security controls (25 min)
```bash
uv run --no-sync pytest tests/test_input_rail.py tests/test_output_cap.py tests/test_rate_limit.py tests/test_readiness_timeout.py -q
uv run --no-sync python -m training.session3.answers
```
Follow query redaction before embeddings and generation. Inspect `app/chains/llm.py` for the output cap. The new output rail returns the existing safe abstention if the generated answer OR evidence quote contains detected PII; it never edits a quote. It covers email, phone, PAN and Aadhaar patterns, not arbitrary names, addresses or toxicity. No content is logged on the blocked path.

## Lab 3 — Container and operational review (30 min)
Read `app/Dockerfile` and `app/Dockerfile.dockerignore` (check actual paths). Identify non-root user, dependency lock, excluded secrets, health probe. Run existing telemetry tests:
```bash
uv run --no-sync pytest tests/test_slo.py tests/test_telemetry.py -q
```
Read `app/database/mongo.py`: `with timeout(2)` bounds the driver ping in its worker thread; it does not shrink normal retrieval deadlines. Infrastructure/DNS scheduling can add wall time. Ping success does not prove that a vector index is queryable.

## Optional live SLO exercise
Start `uvicorn app.main:app` with approved environment; send a representative request mix, then run `python -m app.evaluation.slo_check --base-url http://127.0.0.1:8000`. Use `/metrics/answers` for measured inputs. Empty traffic or missing prices yields not_measured, not a pass. Metrics are process-local and combine a latency window with cumulative token counters; they are not fleet SLOs.

Compute cost as `(input_tokens * input_price + output_tokens * output_price) / 1_000_000`. Enter current approved provider prices; no slide treats the saved prices as current. Estimate monthly cost from traffic and measured per-query cost. The response is buffered, so TTFT/TPS cannot be inferred from generation_ms.

## Exit gate and answers
Submit an API failure matrix, security limitations, and a load-test plan with owner-approved latency/cost/error targets. Offline fakes do not establish a load-test result. 422 means invalid contract, 429 means quota, 503 means dependency unavailable. A live release stays blocked while a required SLO is not_measured.

## Course alignment for this session

See [the complete lesson-to-slide map](../decks/COURSE_ALIGNMENT.md). Source-course technologies are translated to the existing MongoDB/LangChain architecture; design extensions are not live implementation claims.

Additional inference practical: run `uv run --no-sync python -m training.session4.capacity`. Expected weight-only estimates are 16/8/4 decimal GB for idealized 8B FP16/INT8/INT4 weights. Scenario cost is $0.15/day and $4.50/30 days. Identify the unmeasured cache/runtime/concurrency costs.
