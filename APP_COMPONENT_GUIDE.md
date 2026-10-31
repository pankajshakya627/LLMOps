# NexaAssist component guide

Phoenix/OpenInference provides observability. Ragas provides evaluation metrics.
Use [README.md](README.md) for startup and the
[Session 2 trainer checklist](training/session2/TRAINER_SCRIPT.md) for demonstrations.

## Runtime and boundaries

| Layer | Files | Responsibility |
|---|---|---|
| Serving | [app/phoenix_main.py](app/phoenix_main.py) | Register the Phoenix exporter, instrument FastAPI/LangChain, apply privacy masking and flush on shutdown |
| Gateway | [app/gateway/](app/gateway) | LiteLLM profiles, separate embedding routes, bounded chat fallback and optional exact cache |
| Security | [app/security/](app/security) | Input override checks and the separate Guardrails AI validator |
| Base application | [app/main.py](app/main.py) | Shared routers and startup; an uninstrumented factory for offline callers/tests |
| HTTP | [app/api/](app/api) | Validate requests, enforce reviewer credentials/rate limits, sanitize service failures |
| Services | [app/services/](app/services) | Coordinate retrieval, answers, scoring, ingestion and feedback |
| Chains | [app/chains/](app/chains) | Parse/chunk documents, retrieve context, generate and validate answers |
| Storage | [app/database/](app/database) | Scoped Atlas access, embedding compatibility, parent/amendment resolution and feedback persistence |
| Contracts | [app/models/](app/models) | Strict request/response schemas and provenance |
| Evaluation | [app/evaluation/](app/evaluation) | Ragas adapters, independent judge profiles, quality gates and annotation export |
| UI | [app/ui/app.py](app/ui/app.py) | HTTP-only policy chat, citations, Phoenix trace IDs and feedback/reviewer controls |

Routers delegate to services. Services wire chains and storage adapters. Model
contracts do not call the database or providers. The UI calls FastAPI; it does
not bypass API authorization to access MongoDB directly.

## Observability

[app/core/phoenix.py](app/core/phoenix.py) correlates the HTTP server span with
`x-phoenix-trace-id` / `x-phoenix-span-id` headers and answer response fields.
JSON logs carry the active OpenTelemetry trace/span IDs through
[app/core/logging.py](app/core/logging.py).

[app/core/observability.py](app/core/observability.py) keeps bounded process-local
latency/token counters and attaches versioned source prompts to OpenInference
context. Context is scoped to a call and restored after failures. No external
collector is needed for these counters or offline tests.

`PHOENIX_CAPTURE_CONTENT=false` masks input/output content, retrieved documents,
prompt variables and metadata. Embedding vectors and invocation parameters stay
hidden. Enable content capture only for approved synthetic data. Raw drafts may
appear in traces before application validation.

## One answer request

1. [app/api/answer.py](app/api/answer.py) validates the payload and applies limits.
2. [app/services/answer.py](app/services/answer.py) checks explicit instruction overrides, redacts the question, tracks
   token usage and calls the shared answer chain.
3. [app/chains/retrieval.py](app/chains/retrieval.py) applies scope and expands
   parent/amendment evidence through storage adapters.
4. [app/chains/answer.py](app/chains/answer.py) assembles a bounded context,
   generates a draft and checks schema, PII, exact quotes and numeric markers.
   One citation repair is allowed. Unsupported results abstain.
5. If configured, one bounded OpenAI fallback reuses the retrieved evidence and
   validation. Provenance identifies the returned model and fallback reason.
6. The service returns citations, timings, prompt/model provenance and the
   Phoenix server trace/span IDs when an instrumented request is active.

## Evaluation

[app/services/evaluation.py](app/services/evaluation.py) generates once and scores
the same assembled context. [app/evaluation/live.py](app/evaluation/live.py) returns
explicit metric states. Missing references, absent evidence and provider errors
remain distinct from measured zero scores.

[app/evaluation/profiles.py](app/evaluation/profiles.py) isolates the judge and
metric embedding settings from the candidate chat/retrieval configuration.
[app/evaluation/run.py](app/evaluation/run.py) saves batch reports and applies
unchanged gates. Its local trace summaries are not automatically published.

[app/evaluation/phoenix_export.py](app/evaluation/phoenix_export.py) attaches a
saved `/answer/evaluated` response to its exact HTTP span. It retries only HTTP
404 while batched trace ingestion catches up; other failures and exhaustion
return a nonzero exit. This explicit publication does not create native online
evaluators. See [the Phoenix guide](app/observability/README.md).

## Prompts and configuration

[app/chains/prompts/answer.py](app/chains/prompts/answer.py) contains the serving
prompt and version/fingerprint. The application loads this local source; saving
a version in Phoenix's prompt registry does not deploy it.

[app/core/config.py](app/core/config.py) loads private `.env` settings. Query and
stored embeddings must have matching model/profile/dimensions. A custom endpoint
requires its explicit credential; it cannot inherit an OpenAI key implicitly.
Use [runtime.md](app/operations/README.md) for local/cloud/gateway profiles.

## Feedback and stored data

[app/services/feedback.py](app/services/feedback.py) saves feedback with stable
submission IDs, checks review state and exports an explicitly curated golden
case. User corrections are signals, not authenticated ground truth.
[app/database/feedback.py](app/database/feedback.py) reads older response snapshots
through the current field projection without rewriting stored data. HTTP payloads
retain strict unknown-field rejection. Reviewer routes require a bearer token.

## Verification

Run the commands in [README.md](README.md#testing). Meaningful checks cover:

- HTTP/header/body/log trace identity and independent concurrent prompt contexts.
- Actual SDK model tokens, privacy masking and annotation serialization.
- Ragas state handling, exact generation evidence, quality gates and CLI exits.
- Feedback authorization, retry safety, older stored snapshots and golden export.
- Guardrail rejection, bounded fallback, missing evidence and context budgets.

The [earlier live validation report](docs/debug/closing-validation-gaps-20261025/REPORT.md)
records measured model results and limits. Unit tests do not establish semantic
quality or production capacity; live scores remain subject to the existing gates.
