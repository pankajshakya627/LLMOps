# Closing the validation gaps — 25 October 2026

## Debug Summary

**Problem:** The preceding validation found an unbounded active-client map,
unreliable local policy answers, missing real-browser evidence and missing live
Phoenix collector/annotation checks. The course also linked to missing files.

**Root Cause:**

- `app/core/rate_limit.py:35` purged expired identities at capacity, then inserted
  another active identity without enforcing the cap.
- The answer prompt used a literal field-name marker while citation validation
  requires numeric markers. A captured local draft had the correct amount and
  quote but no inline citation. Explicit examples improved local agreement but
  did not resolve all model compliance failures.
- `app/evaluation/phoenix_export.py:79` attempted annotation upload immediately,
  while `app/phoenix_main.py:49` batches trace export. An actual immediate upload
  returned 404; the identical saved span accepted all four scores after ingestion.
- Docker and browser tooling were unavailable during the preceding run. A
  standalone Phoenix collector and isolated headless browser removed those
  environment blockers without modifying the application dependency lock.
- The instructor page referenced a missing trainer script and Datadog document.

**Recommended Tests / Prevention:** The regressions live with their existing
owners: `tests/test_rate_limit.py`, `tests/test_answer.py`, `tests/test_phoenix.py`,
`tests/test_prompts.py` and `tests/test_course_delivery.py`. New storage-diagnostic
and optional Ragas-adapter checks cover previously unexercised real boundaries.
Evaluation CLI tests verify saved reports and nonzero failure exits.

**Fix:**

1. New client identities are rejected when the active map is full. Existing
   identities retain their limits; expired capacity is reclaimed.
2. Prompt 1.2.0 demonstrates numeric citations and exact numeric copying. The
   pure-local candidate achieved 4/10 exact expected statuses, versus 0/10 before.
3. Optional `OPENAI_FALLBACK_MODEL` enables one bounded cloud attempt after an
   OpenAI-compatible provider error or a non-answered result with evidence.
   Retrieval is reused, output limits and validators remain in place, and
   provenance records the actual model and reason. Identical official-model
   retries, empty-evidence fallback and pre-generation budget abstentions are
   avoided. The shared implementation is `app/chains/answer.py:42`. Independent judges do not
   inherit this setting. The private `.env` setting uses its existing approved
   cloud model and credentials; no credential was copied into these artifacts.
4. Annotation exports retry only HTTP 404, at most six attempts two seconds apart.
   Authentication/other HTTP failures still fail immediately; exhaustion fails.
5. Restored the trainer checklist and `DATADOG_README.md`, repaired 25 stale root
   documentation links and documented the standalone collector and fallback.
   The documented deck total now matches the shipped manifest: 152 slides.
6. Corrected the private `.env` embedding profile and parent collection to match
   its existing Qwen collection/index. Cloud chat and independent judge settings
   were preserved. Direct retrieval using that file returned three results and
   one amendment, including maximum-loan evidence; see
   [base-env-retrieval.json](base-env-retrieval.json). Credentials are excluded.

**Confidence:** High in the deterministic fixes and software tests. Live model
quality remains probabilistic; fallback success is not pure-local accuracy.

## Verification evidence

| Final automated check | Result |
|---|---|
| Application, training and synthetic mock API tests | 355 passed; zero failures, errors or skips |
| Optional Phoenix and Ragas runtime tests | 8 passed; zero failures, errors or skips |
| Ruff / formatting | Passed |
| Mypy | Passed, 143 files |
| Aggregate statement / branch coverage | 87.6% / 77.8% |

Receipts: [pytest.xml](pytest.xml), [optional-runtime.xml](optional-runtime.xml),
[coverage.json](coverage.json) and [SUMMARY.json](SUMMARY.json). Coverage includes
the application, training and synthetic mock server, with subprocess collection.

The local-first API with fallback matched **10/10** expected statuses, with five
cloud fallbacks in that run. All original golden inputs and expected statuses
were retained. See [fallback_cases.json](fallback_cases.json). Exact status
agreement does not replace a full semantic quality release evaluation.

The real collector received traces and stored four Ragas annotations; SDK
readback verified them. The current prompt was registered and inspected in the
native Prompts page. See [annotation_readback.json](annotation_readback.json),
[evaluated.json](evaluated.json) and [phoenix_prompt.json](phoenix_prompt.json).
After the retry fix, a fresh immediate CLI export exited successfully in about
2.29 seconds, and all four annotations were read back; see
[immediate-export-receipt.json](immediate-export-receipt.json). Native prompt
registration records the source version; serving still uses the local template.

The live maximum-loan evaluation scored faithfulness 1.0, recall 1.0, precision
0.10 and relevancy about 0.673. Those last two results do **not** satisfy the
repository's placeholder 0.85 quality targets. Targets were not lowered and this
was not reported as a production quality-gate pass. Presentation order and the
large selected context affect context-precision interpretation; measured low
scores require further retrieval/evaluation review.

## Browser evidence

The user selected headless mode. Tests used agent-browser 0.39.2 with a dedicated
session and installed Chrome; no personal profile or existing tabs were attached.

| Flow | Evidence |
|---|---|
| Swagger policy request | Correct answer rendered; screenshot `swagger-answer.png`; no console messages at capture |
| Streamlit evaluated policy chat | Answer and expandable quote rendered; screenshot `streamlit-answer.png`; no console messages at capture |
| Phoenix traces | Actual project and instrumented root/model traces rendered; `phoenix-traces.png` |
| Phoenix prompt | Actual version 1.2.0 and source hash visible; `phoenix-prompt.png` |
| Phoenix evaluation | All four stored metric annotations expanded on the evaluated trace; `phoenix-evaluation.png` |
| Feedback review/export | Submitted, accepted and exported through the real UI using temporary mongomock feedback storage; `feedback-export.png` |
| Guardrails | Invalid output rejected through Swagger; `guardrails-rejection.png` |
| Architecture explorer | Portable document opened and step navigation exercised; `architecture.png` |

Streamlit's collapsed sidebar was opened before navigation, and Enter committed
the password widget. Off-screen automation attempts and a premature wait were
corrected rather than represented as application defects.

The standalone collector uses isolated `/tmp/nexa-phoenix-gap-validation` storage
on port 6007. Browser feedback writes use only an in-memory store with a synthetic
reviewer credential. The original Atlas corpus/index and real feedback collection
were not modified. Temporary API, UI, validator and collector processes were
stopped after validation; the isolated browser session was closed. No stop signal
was sent to the separate Ollama Desktop runtime.

## Post-Fix Quality

**Scope:** Fix-owned implementation, tests, configuration examples and course
documentation. This workspace has no Git metadata; no branch, commit or PR was
created, and ownership/churn history could not be reconstructed.

**Simplify:** Targeted manual inspection. No broad automatic simplification was
applied where pre-existing user edits could not be distinguished without Git.
The shared answer-chain fallback preserves the same validation path for API and
batch callers, avoiding router-specific business logic.

**Review:** Targeted manual review of capacity handling, retry bounds, credential
selection, evaluator isolation, provenance and safety/error paths. Regression
checks first failed on the reproduced defects and then passed after fixes.

**Residuals:** Pure Ollama remains unreliable; structurally valid factual mistakes
do not trigger the non-answered fallback. Quality targets need separate measured
improvement/calibration. This run is not a load test, penetration test, complete
native Phoenix online-evaluator integration, or full semantic release approval.

**Re-verification:** 363 automated checks passed across the two suites; final
lint/type and coverage receipts are saved beside this report. Historical
validation artifacts remain unchanged.

## Sources for the new environment setup

The [official Phoenix terminal guide](https://arize.com/docs/phoenix/self-hosting/deployment-options)
documents standalone serving. Browser setup follows the
[official agent-browser installation guide](https://agent-browser.dev/installation).
Pinned collector and instrumentation packages run in separate environments.
