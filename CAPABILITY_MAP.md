# Capability Map: Session 2 LLMOps Core

Status: Capability map approved by the user on 24 October 2026 ("yes go with the plan").
The user subsequently approved code implementation. All four modules are implemented
and checked offline; live deployment/model preflight is not claimed.

## Objective

Connect the Session 2 practical stack to NexaAssist: Ollama chat
`qwen3.5:9b-mlx` and embeddings `qwen3-embedding:0.6b`, alongside the existing
OpenAI configuration, using LiteLLM, Phoenix, Ragas and Guardrails AI.

## Approved boundaries

These are units of work within the existing application layers, not new services.

| Module id | Responsibility | Depends on |
|---|---|---|
| `model-access` | Configure compatible chat and embedding endpoints; preserve existing OpenAI behavior; enforce matching ingestion/query embedding profiles and isolate local/cloud vector collections and indexes. Keep judge credentials and endpoints separately configurable. | — |
| `gateway-routing` | Connect the app to the existing LiteLLM configuration; exercise bounded chat fallback, load balancing and opt-in isolated response caching. Extend existing Phoenix traces with observed model/routing information and avoid unsupported mixed-model cost claims. | `model-access` |
| `security-guardrails` | Integrate Guardrails AI output validation with existing strict schemas, PII redaction, citation checks and bounded repair. Cover adversarial prompts and scrub batch-evaluation inputs before model calls and telemetry. | `model-access` |
| `evaluation-profiles` | Compare candidate models with a fixed judge and fixed metric embeddings using the existing Ragas harness, exact retrieved contexts, quality gates and Phoenix score submission. Cover normal, fallback and rejected-output paths. | `model-access`, `gateway-routing`, `security-guardrails` |

Build order: `model-access` → `gateway-routing` and `security-guardrails` →
`evaluation-profiles`.

Phoenix instrumentation is extended within these capabilities. Existing token accounting, Ragas scoring and security checks remain the starting point.

## Evidence from the current code

- `app/chains/llm.py` forces the OpenAI Responses API; `app/chains/embeddings.py`
  uses the OpenAI embedding endpoint. Neither factory exposes an alternate endpoint.
- `app/gateway/litellm.yaml` already supplies the requested model aliases
  and chat fallback configuration, with response caching disabled.
- `app/chains/ingestion.py` fingerprints the embedding model and dimensions, but
  changing those settings can replace vectors in the same configured collection.
- `app/core/observability.py`, `app/services/answer.py` and `app/evaluation/`
  already implement substantial Phoenix and Ragas functionality.
- `app/chains/answer.py` and `app/chains/redaction.py` already enforce output,
  citation and PII checks. Guardrails AI now runs from `app/security/guardrails_service.py`.
- Batch evaluation in `app/evaluation/run.py` shares the input security/redaction
  path used by the answer service.

## Constraints carried forward

Follow `CONSTRAINTS.md` and the existing LangChain → services → FastAPI → UI
boundaries. Use MongoDB Atlas exclusively. Never fall back between embedding
families or modify an existing corpus to demonstrate a different embedding profile.
Local-to-cloud fallback must be explicit in configuration and teaching material.
Cache experiments must isolate authorization, evidence and prompt versions.

Implementation will use failing offline tests first, then focused tests, Ruff,
mypy and the full offline suite. Live service results must be reported separately.
The existing missing architecture HTML test remains a documented baseline failure.

## Specification status

| Module id | Specification status |
|---|---|
| `model-access` | [SPEC-model-access.md](SPEC-model-access.md): implemented; provider/corpus contracts checked offline |
| `gateway-routing` | Application adapter and fallback/balancing/cache configs implemented; real SDK logic checked with mock responses |
| `security-guardrails` | PII/citation checks retained, batch queries scrubbed, optional Guardrails AI process integrated and self-checked |
| `evaluation-profiles` | Independent judge/metric settings wired into batch/live evaluation; comparisons reject changed evaluator profiles |

The original [System Design DOCX](training/decks/system_design/Model_Access_Design.docx)
and [PDF](training/decks/system_design/Model_Access_Design.pdf) remain proposal
snapshots. Current implementation details are in the
[runtime guide](app/operations/README.md), [plan](tasks/plan.md),
[task list](tasks/todo.md) and [verification report](training/session2/IMPLEMENTATION_VERIFICATION.md).

Git history and context0 checkpoints were unavailable in this workspace; findings
above come from the current files rather than commit or ownership analysis.

## Optional Phoenix classroom profile

The Phoenix walkthrough uses `app.phoenix_main:app` with the existing API routes.
FastAPI server spans correlate to response headers; LangChain model/runnable
spans use OpenInference. `app.evaluation.phoenix_export` attaches saved
`/answer/evaluated` scores/statuses to the matching HTTP server span. See
[the run guide](app/observability/README.md) and
[verification](training/session2/PHOENIX_VERIFICATION.md). Phoenix is the only observability provider. The uninstrumented factory remains
available for offline callers; no second telemetry provider is installed.
