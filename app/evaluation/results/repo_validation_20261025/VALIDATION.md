# Repository validation — 25 October 2026

The offline application tests pass. Live backend checks were also executed
against the existing synthetic Atlas corpus with temporary local services.
This is a validation record, not a production-readiness certification.

## Scope and recon

Reviewed application configuration, FastAPI contracts, RAG chains, Atlas adapter
boundaries, ingestion, evaluation, feedback, telemetry, Streamlit tests, training
CLI tests and the separate synthetic banking API. The current workspace is not
a Git repository: commit counts, branch diffs, ownership, churn and bug-magnet
history could not be computed. No repository history was created.

The earlier missing architecture document is present in this workspace, and its
path/walkthrough test passes. No test was removed, skipped or weakened for this
validation. No production prompt, evaluation threshold, application logic,
corpus or index was changed.

## Checks and observed results

| Check | Result |
|---|---|
| Original `tests` baseline | 269 passed in 39.80 seconds |
| Expanded default suite | 306 cases; included in the combined run below |
| Default + synthetic banking API | 328 passed in 35.85 seconds, zero failures/skips |
| Separate actual Phoenix SDK tests | 4 passed in 2.61 seconds |
| Hostile environment fixture check | 40 passed with inherited model, validator and DD settings overridden |
| Real Guardrails AI Python 3.13 self-check | Passed all five built-in schema decisions |
| Real LiteLLM 1.106.2 offline self-check | Passed replica selection, fallback and cache scope/invalidation assertions |
| Ruff | Passed repository-wide |
| Formatting | All six changed test files pass |
| Mypy | Passed, 141 source files |
| Real browser | Blocked before the first route; see below |

The final Python test counts are 328 + 4, not 332 real-browser or live-provider
tests. Existing Streamlit AppTest checks execute the UI and API contracts without
a rendered Chrome/Safari browser. The LiteLLM self-check uses its actual Router
and Cache with offline model fixtures; it does not prove production proxy
deployment failover or multi-worker cache behavior.

JUnit receipts: [pytest.xml](pytest.xml), [phoenix-runtime.xml](phoenix-runtime.xml).
Resolved overlay versions: [versions.json](versions.json).

## Added test coverage

| File | New cases / behavior |
|---|---|
| `tests/test_api_pipeline.py` | 19 cases: actual HTTP routing/services/chains/parser, retrieval-only behavior, verified citations, provenance/tokens, feedback review/export, empty evidence, PII, one repair, repair exhaustion, provider failure, invalid schema, output PII, unavailable evals and invalid request boundaries |
| `tests/test_provider_profiles.py` | 8 cases: shipped local/cloud overlays preserve Qwen retrieval and independent judge configuration; unsafe provider/collector URLs are rejected |
| `tests/test_phoenix.py` | 8 additional cases: non-recording spans, request isolation, body events, conflicting/normalized span IDs, failed exports and transport cleanup |
| `tests/test_live_evaluation.py` | 2 additional cases: missing scorer dependencies produce explicit errors while unavailable reference-dependent metrics stay unavailable |
| `tests/runtime/phoenix_profile_check.py` | 4 actual-SDK cases: conflicting Datadog profile rejected, default privacy and synthetic capture, root/model correlation and token counts, SDK annotation payloads |
| `tests/conftest.py` | Clears Settings-related process variables in the shared offline fixture; `_env_file=None` alone does not isolate environment variables |

The pipeline tests use real business logic. Their isolated boundaries are a
vector-store response, an in-memory parent store, HTTP model transport and
mongomock feedback persistence. These are offline integration tests, not proof
of real Atlas search/index semantics. Real model/Atlas behavior is recorded
separately in the live JSON receipts.

The optional SDK check has a `_check.py` filename and must be invoked explicitly
in its pinned dependency overlay. It adds no import requirement or automatic
skip to the base suite. No new application dependency was added.

## Coverage measurement

Coverage.py branch measurement included subprocesses used by CLI and telemetry
tests. Scope: `app`, `training` and the synthetic banking server; the banking test
file itself is omitted. Counts are execution evidence, not correctness scores.

| Scope | Statements executed | Branches executed |
|---|---|---|
| Application | 2184 / 2629 | 422 / 568 |
| Training modules | 505 / 550 | 55 / 76 |
| Synthetic banking server | 203 / 205 | 34 / 36 |
| Total | 2892 / 3384 = 85.5% | 511 / 680 = 75.1% |

Coverage.py's combined statement/branch figure is 83.7%. Both
`app/core/phoenix.py` and `app/phoenix_main.py` have all measured statements and
branches exercised. Some standalone evaluation/demo entry points and diagnostics
remain unexercised; see [coverage.json](coverage.json). These figures do not
include browser behavior, slide exports, notebook execution or load testing.

The first baseline coverage attempt did not follow child processes. It was not
used to claim missing training coverage; the final configuration enables
`patch = subprocess` and combines child results.

## Live backend checks

Initially no API, Phoenix, Guardrails, Streamlit or Ollama service was listening.
The Docker client was installed but its daemon socket was unavailable. To test
the backend without Docker, temporary Ollama, Guardrails (8103), local API (8003)
and cloud API (8004) processes were started. Both APIs passed `/health` and
`/ready`. `.env` supplied the existing cloud credentials/model settings; no key
was copied into these artifacts.

Both candidates used Qwen `qwen3-embedding:0.6b`, the existing 1024-dimensional
Qwen corpus/index and prompt 1.1.0. The local model was
`qwen3.5:9b-mlx`, and the configured cloud candidate was `gpt-6-luna`. The independent
judge was `gpt-6.1-sol`. These identify this run, not universally required models.

All ten cases from `evaluation/datasets/answer.jsonl` were submitted to each API:
maximum amount, amended processing fee, LTV, personal-loan foreclosure, vehicle
LTV, age limits, two historical policy boundaries, unsupported NRLR and
unsupported cryptocurrency policy. See [live_openai.json](live_openai.json) and
[live_ollama.json](live_ollama.json) for full answers, citations, reference targets,
timings and expected statuses. The machine-readable summary records final status
agreement separately from semantic quality.

| Candidate | HTTP 200 responses | Exact expected-status agreement | Observed behavior |
|---|---|---|---|
| OpenAI | 10 / 10 | 10 / 10 | Eight supported answers and two expected abstentions |
| Ollama | 10 / 10 | 0 / 10 | Eight answerable questions abstained; the two unsupported cases requested clarification instead of the expected abstention |

Ollama's HTTP availability therefore passed while its golden functional
expectations failed. Citation-check warnings were observed on multiple local
requests; some requests instead produced a model-selected abstention. Neither
behavior was relabeled as a successful policy answer. No automatic semantic
fallback was added to hide these failures.

The OpenAI answers were inspected against their source quotes and reference
targets. A full ten-case judge/Ragas release report was not run; matching status
alone is not a quality pass. Local citation failures and safe abstentions are
recorded rather than changing validation rules to force an answer.

One additional maximum-loan request was scored live:

| Metric | Result |
|---|---|
| Faithfulness | 1.0 |
| Answer relevancy | 0.9583873236833522 |
| Context precision | 0.09999999999 |
| Context recall | 1.0 |

The low context precision remains a retrieval-quality concern for this question.
Additional OpenAI requests with synthetic PII and a prompt-injection instruction
returned supported maximum-loan answers without echoing the identifiers or
guaranteeing approval. This does not establish general injection resistance or
complete telemetry sanitization. Live Guardrails accepted the valid schema and
rejected an invalid status and an unknown extra field. An empty `/answer` body
returned HTTP 422. See [live_security_evaluation.json](live_security_evaluation.json).

No live feedback records, corpus documents or vector indexes were written.
No model download was needed. Temporary services were stopped after requests
completed; current service status is not a promise that these ports remain up.

## Unresolved limiter resource boundary

`app/core/rate_limit.py:35` purges expired clients after `max_clients` is reached,
then adds a new identity even if every entry is still active. Reproduction:

```python
from app.core.rate_limit import SlidingWindowLimiter

limiter = SlidingWindowLimiter(
    limit=1, window_seconds=60, clock=lambda: 0.0, max_clients=3
)
for number in range(100):
    limiter.check(str(number))
print(limiter.tracked_clients)  # Observed: 100, despite max_clients=3.
```

This is a capacity-policy gap, not a failed model test. It is not hidden by a
skip/xfail or by changing the current implementation. Agree on whether to reject
new identities or use a shared limiter before adding an enforcement regression
and modifying production behavior. See [TEST_QUALITY.md](TEST_QUALITY.md) for the
Brooks review and [limiter_capacity_probe.json](limiter_capacity_probe.json).

## Browser Test Results

**Test Scope:** Entire current workspace; Git-based affected-route detection unavailable.
**Driver:** None initialized. No Chrome DevTools/qualifying host-native browser
surface was available; fallback `agent-browser` was not installed. No replacement
Playwright/Selenium stack was introduced.

**Pages tested in a real browser:** 0.

| Route / page | Status | Reason |
|---|---|---|
| FastAPI `/docs` | Skip | Browser driver unavailable; API behavior tested separately |
| Guardrails `/docs` | Skip | Browser driver unavailable; validator HTTP requests tested separately |
| Streamlit policy chat | Skip | Browser driver unavailable and Streamlit server not started; AppTest passed |
| Streamlit feedback review/export | Skip | Same browser/server blocker; AppTest and API integration passed |
| Phoenix dashboard / traces / prompts | Skip | Browser driver unavailable and collector container blocked by Docker daemon |
| Architecture HTML explorer | Skip | Browser driver unavailable; document/link checks passed |

**Console errors:** Not measured. **Screenshots/performance/accessibility:** Not measured.
**Result:** PARTIAL. Configure an approved browser driver and restore Docker/
Phoenix plus Streamlit to complete visual and interactive validation. No fresh
scores were published to a Phoenix collector during this run; SDK transport,
trace correlation and privacy were checked offline with actual pinned packages.

## Repeat the checks

Run from the repository root. Optional dependencies are supplied through isolated
uv overlays; initial installation may need network access.

```bash
uv run --no-sync pytest -q tests

uv run --no-sync --with openapi-spec-validator \
  pytest -q tests nexa_synthetic_data/api/mock_server/test_mock_api.py

uv run --no-sync --with-requirements training/session2/requirements-phoenix.txt \
  pytest -q tests/runtime/phoenix_profile_check.py

uv run --no-sync ruff check .
uv run --no-sync mypy .
```

For branch coverage use the saved `coverage.ini` with Coverage.py, then combine
parallel data files before reporting. Keep the Phoenix SDK check as a separate
pytest invocation: passing both the parent `tests` directory and its explicitly
named nonstandard check file in one call did not collect that check in this run.

## Remaining scope

No real-browser rendering, complete ten-case judge/Ragas release evaluation,
multi-worker load/fault test, distributed gateway deployment, notebook execution,
slide/document re-export, comprehensive penetration test or production rollout
was performed. The present offline/live evidence does not establish every
possible use case or production readiness.
