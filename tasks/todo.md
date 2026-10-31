# Session 2 implementation tasks

- [x] Explicit model clients and independent evaluator settings.
  - Acceptance: legacy defaults, local text embedding, credential isolation and caps.
  - Verify: `pytest -q tests/test_model_access.py tests/test_output_cap.py`.
- [x] Corpus and vector integrity checks.
  - Acceptance: incompatible chunks/parents fail before use; legacy corpus works.
  - Verify: `pytest -q tests/test_embedding_profiles.py tests/test_ingestion.py tests/test_retrieval.py`.
- [x] Gateway integration and attributable telemetry.
  - Acceptance: alias requests, observed-model provenance, bounded errors and safe costs.
  - Verify: offline HTTP and gateway config tests.
- [x] Guardrails validation and batch input redaction.
  - Acceptance: configured validator rejects invalid/outage paths; no PII reaches judges.
  - Verify: offline security regression tests and isolated Guardrails self-check.
- [x] Fixed-profile evaluation and operational documentation.
  - Acceptance: candidate changes preserve evaluator identities and exact contexts.
  - Verify: existing/new evaluation tests.
- [x] Run constraints, full regression suite, simplify changed code and save handoff.
  - Acceptance: no weakened constraints/tests; failures and live limits reported.

Delivery: 255 passed; the documented missing architecture HTML test failed. Ruff
and mypy passed; real Guardrails AI/LiteLLM self-checks passed in an isolated tool
environment. See training/session2/IMPLEMENTATION_VERIFICATION.md for limits.
