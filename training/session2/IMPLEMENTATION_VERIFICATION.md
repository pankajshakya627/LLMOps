# Session 2 implementation verification — 24 October 2026

Historical verification record. The current application uses Phoenix/OpenInference
and Ragas only; use [phoenix.md](../../app/observability/README.md) for current startup and contracts.

## Delivered

- Explicit OpenAI/Ollama/LiteLLM endpoint, credential and API-mode configuration.
  Default OpenAI Responses behavior remains covered. Custom endpoints require
  explicit keys; ambient SDK URL variables cannot redirect the default clients.
- Shared document/query embedding client with text inputs for custom endpoints,
  result count/dimension/finite-value checks, and corpus/parent profile checks
  before application retrieval or ingestion. Matching legacy OpenAI data works;
  custom profiles require separate compatible stores. Index creation stays manual.
- Independently resolved judge and Ragas metric embeddings in batch/live scoring.
  New comparison reports reject differing evaluator profiles. Batch inputs and
  reference text are scrubbed before model calls and recording.
- Gateway fallback, balancing and opt-in local chat-cache configurations. Cache
  namespaces cover the configured credential, access scope, corpus, model and
  prompt versions. Reported model/cache metadata reaches answer provenance and
  existing Datadog annotations; custom endpoint cost is null rather than guessed.
- Optional HTTP integration with a loopback Guardrails AI validation process.
  Configured rejection/outage/malformed decisions fail closed. Existing PII,
  citation and bounded repair controls remain active.

Custom embedding metadata is shared between chunk and parent enrichment after a
covered simplification; the full suite was rerun after that change.

Configuration and commands: [runtime.md](../../app/operations/README.md). The original System Design
DOCX/PDF are proposal snapshots; these runtime instructions reflect the code.

## Checks executed

| Check | Result |
|---|---|
| New and affected pytest groups during TDD | Passed after their implementation changes |
| `.venv/bin/python -m pytest -q tests --junitxml=/tmp/nexa-session2-pytest.xml` | **255 passed, 1 failed**, 0 skipped, 34.44 s |
| `.venv/bin/ruff check .` | Passed |
| `.venv/bin/mypy .` | Passed: 133 source files |
| Final gateway-focused pytest after an added type-narrowing assertion | 6 passed |
| Real Guardrails AI 0.11.0 self-check | Passed in isolated Python 3.13 environment |
| Real LiteLLM 1.106.2 SDK/cache self-check with mock responses | Passed in the same isolated tool environment |
| Original tests, CONSTRAINTS.md, pyproject.toml and uv.lock compared with the pre-edit snapshot | Byte-for-byte unchanged |
| Added Python lines checked for suppressions and test skips | None found |

The seven new test modules add **41 cases**. Existing focused constraints tests
and telemetry tests are included in the full suite. [verification.json](verification.json)
contains counts and protected-file hashes. The JUnit file is machine-local and
temporary; the report above preserves the result in this workspace.

### Known baseline failure

`tests/test_architecture_document.py::test_architecture_paths_and_walkthroughs_resolve`
still expects absent `C4-Documentation/nexaassist-architecture.html`, as recorded
in `CONSTRAINTS.md` before this implementation. The full suite exits 1. That test
was not skipped, deleted, changed or weakened, and the unrelated artifact was not
fabricated to make the suite green.

## Framework compatibility finding

Guardrails AI 0.11.0 declares Python `<3.14`, while the application requires
Python `>=3.14`. It therefore runs in an isolated process; the application
environment and dependency manifests were not downgraded or changed.

The expanded real-framework negative check found Guardrails can prune extra JSON
fields and report success. The validation process now rejects invalid original
JSON with the shared strict Pydantic model before Guardrails normalization.
Self-checks cover valid abstention, valid quoted-answer shape, forbidden status,
invalid evidence ID and unexpected fields. Unit tests also cover malformed JSON,
bad decision types and validator outage. These checks establish schema behavior,
not factual correctness or comprehensive injection resistance.

The real LiteLLM SDK self-check uses explicitly labelled mock responses and its
SDK-only fault flag. It exercises two fixture deployment IDs, fallback, exact-cache
reuse and scope/evidence misses. It does not simulate a live proxy outage or
establish distribution across physical servers.

## Evidence limits and remaining live preflight

No model downloads, GPU generation, OpenAI calls, Atlas reads/writes or Datadog
cloud exports were performed. Full proxy deployment, physical replicas, actual
model tags/digests, structured-output support, embedding length, Atlas index
readiness, live quality and performance remain to be measured against prepared
synthetic services. Existing evaluation/SLO thresholds remain placeholders.

Profile checks validate declared metadata, not actual model weights. Metadata
scans have a two-second deadline; an immutable corpus manifest is the next scaling
step. Concurrent ingestion and atomic cross-collection publication remain outside
the current guarantees. The optional local cache and unauthenticated loopback
validation process are classroom configurations, not public multi-tenant services.

Git history, ownership, branches and commits were unavailable because this copy
has no Git metadata. The pre-edit comparison used an authorized machine-local
source snapshot without `.env` secrets. No context0 connector was available.
