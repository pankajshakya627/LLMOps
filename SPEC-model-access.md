# Specification: model-access

Status: Approved for implementation by the user on 24 October 2026 ("yes go with
the plan create the code implementation"). Implementation and offline verification
are complete; live model/Atlas/Phoenix preflight remains unperformed. See
[verification](training/session2/IMPLEMENTATION_VERIFICATION.md) and
[runtime configuration](app/operations/README.md).

## Objective

Let the existing NexaAssist ingestion, retrieval and answer paths use explicitly
configured OpenAI or Ollama endpoints. Support the requested Ollama chat model
`qwen3.5:9b-mlx` and embedding model `qwen3-embedding:0.6b` alongside the current
OpenAI configuration. Preserve citations, input/output protections, bounded model
calls and Phoenix instrumentation.

This module provides the model configuration contract consumed by
`gateway-routing`, `security-guardrails` and `evaluation-profiles` in
[CAPABILITY_MAP.md](CAPABILITY_MAP.md).

## Accepted scope

- Existing OpenAI settings and stored OpenAI vectors remain usable without a
  migration. Changing the answer model does not require changing embeddings.
- Local and OpenAI embedding corpora use separate chunk collections, vector
  indexes and parent collections. No automatic conversion of an existing corpus.
- Endpoint selection belongs to server configuration, not user-supplied API input.
- The current LangChain OpenAI integration can carry the required standard API
  fields; unsupported runtime features produce explicit failures.
- Requested model tags are configuration inputs. Their availability, model
  digests, output dimensions and hardware behavior require live verification.

## Scope and current evidence

`app/chains/llm.py` forces Responses API calls. `app/chains/embeddings.py` shares
one OpenAI embedding configuration between ingestion and retrieval. Neither
factory accepts a separately configured endpoint. `app/core/config.py` contains
the current defaults: `gpt-6-luna`, `text-embedding-3-small`, and 1536 dimensions.
These are repository defaults, not recommendations about current provider models.

`app/chains/ingestion.py` fingerprints model and dimensions and upserts stable
chunk IDs. This triggers re-embedding when settings change but does not prevent
replacing or mixing embeddings in the configured collection. Parent sections
also use stable IDs. Both stores need profile isolation.

`app/evaluation/run.py` and `app/evaluation/live.py` derive the judge by copying
candidate settings and replacing its model. An added candidate endpoint must not
silently redirect the judge or send its credentials to that endpoint.

This module extends shared factories and their consumers. LiteLLM routing policy,
response caching, Guardrails AI integration and comparative Ragas experiments
belong to the other approved modules. Existing checks remain active throughout.

## Tech stack

Python 3.14+, LangChain LCEL, `langchain-openai`, `langchain-mongodb`, Pydantic v2,
`pydantic-settings`, PyMongo, structlog, OpenInference and pytest. The inspected local
environment has `langchain-openai` 1.6.7, `langchain-core` 1.6.6,
`langchain-mongodb` 0.12.1 and Pydantic 2.13.5. These are observations, not new pins.
Reuse installed integrations; this specification requires no new dependency.

## Provider and data contracts

| Contract | Required behavior |
|---|---|
| Answer chat | Explicit model, endpoint, credential and API mode. Existing OpenAI Responses behavior is the default. The local profile uses Chat Completions at `http://127.0.0.1:11434/v1` with the requested tag. |
| Embeddings | Explicit model, endpoint, credential, expected dimensions and corpus identity. Ingestion and query use exactly the same profile. Local requests carry text without OpenAI-specific tokenization. |
| Judge | Model, endpoint, credential and API mode resolve independently from the candidate. Existing OpenAI evaluation remains compatible; choosing local chat does not redirect an OpenAI judge. No judge client is created when evaluation is unused. |
| Credentials | Settings hold `SecretStr` values. Custom endpoints use explicitly configured endpoint credentials; an OpenAI key is never inherited by an unrelated endpoint. Ollama's documented dummy key is explicit. Local generation/retrieval must not require a real OpenAI key. |
| Endpoint validation | Accept configured HTTP(S) endpoints; reject credentials embedded in URLs and invalid API modes. Document plaintext loopback endpoints for local use and TLS for remote endpoints. Ambient SDK endpoint variables cannot override the selected application profile. |
| Corpus identity | Bind the collection/index/parent selection to embedding model, dimensions and declared deployment/profile identity. An equal vector length does not make different embedding models compatible. Gateway aliases must declare their underlying embedding identity. |

Logical configuration fields above are the boundary contract. Exact setting names
are documented in `.env.example` and the runtime guide, following existing flat
settings conventions. No provider registry or separate application router was added.

Ollama documents OpenAI-compatible Chat Completions and embedding endpoints, with
partial API compatibility. LangChain exposes custom base URLs but preserves only
standard response fields. Accordingly, the requested local contract must be
checked explicitly rather than inferred from a model tag. See
[Ollama compatibility](https://docs.ollama.com/api/openai-compatibility) and
[LangChain ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai).

### Embedding integrity

- Before ingestion mutates either store, reject an incompatible, mixed or
  unidentifiable existing embedding profile. The failed request leaves chunks,
  parent sections and stale-chunk deletions unchanged.
- Before a query embedding/search, reject a corpus whose embedding identity does
  not match the configured query profile. Never answer from a partial match.
- Existing documents with the current model/dimension metadata remain readable
  under the matching legacy OpenAI profile. Unknown deployments cannot be adopted
  by guessing that model names or equal dimensions imply equivalence.
- Verify returned vectors have the configured finite dimensions before writing
  or querying Atlas. Index definitions must use the same dimensions.
- A new embedding family uses an empty, separately named chunk collection and
  parent collection with a separate manually created vector index. Demonstrations
  must not delete, re-embed or rename the existing OpenAI corpus.
- Preserve existing document checksums, date/institution scope, parent expansion
  and failed-document retention guarantees. Document the current limitation that
  ingestion writes are not a multi-collection transaction; concurrent ingestion
  is outside this change's guarantees.

### Failure and observability behavior

Preserve the configured answer output cap, current 60-second chat timeout,
one-retry limit, token callback and workflow/prompt annotations. Retain sanitized
API errors. Do not introduce application-level provider fallback in this module.
Unsupported structured output, exhausted calls and malformed responses cannot
bypass Pydantic validation, citation checks or PII rejection. Missing usage or
responding-model metadata must not be invented.

## Commands

Run from the repository root. The `.venv` commands use the inspected environment
without downloading packages or resolving dependencies during verification.

```sh
# Focused existing behavior, then the new offline contracts once implemented
.venv/bin/python -m pytest -q tests/test_output_cap.py tests/test_ingestion.py tests/test_retrieval.py tests/test_input_rail.py tests/test_live_evaluation.py tests/test_evaluation.py
.venv/bin/python -m pytest -q tests/test_model_access.py

# Required constraints and regression reporting
.venv/bin/python -m pytest -q tests/test_training_labs.py tests/test_answer.py tests/test_readiness_timeout.py
.venv/bin/ruff check .
.venv/bin/mypy .
.venv/bin/python -m pytest -q tests

# Existing API entry point; live services require separately configured settings
.venv/bin/.venv/bin/uvicorn app.phoenix_main:app --reload
```

`tests/test_model_access.py` now implements the provider contract checks. The
verification report records executed commands and the known regression baseline.

## Project structure and consumers

| Existing location | Responsibility in this module |
|---|---|
| `app/core/config.py`, `.env.example` | Validated endpoint, credential and profile configuration; documented OpenAI/local examples. |
| `app/chains/llm.py`, `app/chains/embeddings.py` | Shared model clients; pure LangChain, no FastAPI/Streamlit imports. |
| `app/database/`, `app/database/indexes.md` | Corpus identity checks and exact manual index definitions for declared dimensions. |
| `app/services/ingestion.py`, `app/services/retrieval.py` | Check profile compatibility before mutations or query embedding; preserve async boundaries. |
| `app/services/answer.py`, `app/services/evaluation.py` | Consume shared clients while preserving answer and telemetry contracts. |
| `app/evaluation/run.py`, `app/evaluation/live.py`, `app/evaluation/rag_failure_examples.py` | Consume explicit candidate/judge profiles without creating independent selection logic. |
| `tests/` | Offline request, configuration, corpus-integrity and regression coverage. |

No new UI flow, API request field, LangGraph layer or MCP server is required.

## Code style

Follow the current typed Python and Pydantic conventions. This existing validator
from `app/core/config.py` illustrates explicit validation:

```python
@model_validator(mode="after")
def valid_overlap(self) -> Settings:
    if self.chunk_overlap_characters >= self.chunk_max_characters:
        raise ValueError("CHUNK_OVERLAP_CHARACTERS must be smaller than CHUNK_MAX_CHARACTERS")
    return self
```

Use `from __future__ import annotations`, async I/O or safe thread offloading,
structlog and existing LCEL runnables. Keep shared factories small. Apply
`code-simplification` only to changed code after behavior is covered; separate
pure refactors from feature changes.

## Testing strategy and success criteria

Use pytest, existing fixtures, fake stores and HTTP mock transports. New behavior
gets a failing test before implementation; no required offline test contacts a
provider, Atlas or Phoenix.

| ID | Observable acceptance condition |
|---|---|
| MA-01 | Existing OpenAI configuration produces the same API mode, model, cap and callbacks; existing tests remain valid. |
| MA-02 | A local chat request uses the configured tag and Chat Completions endpoint, keeps its cap/timeout/retry limits and parses a valid cited answer. Invalid structured output follows the existing rejection contract. |
| MA-03 | Both document and query embedding requests use the same local profile and text input. Mismatched dimensions, non-finite or malformed vectors are rejected before Atlas writes/search. |
| MA-04 | Incompatible, mixed or unknown corpus identities fail before query embedding or ingestion mutation. Matching legacy OpenAI metadata remains supported. Separate local/cloud stores retain their own chunks and parents. |
| MA-05 | Switching candidate chat does not change explicit judge endpoint/key/API mode. Endpoint credentials cannot leak between profiles, including through ambient SDK variables. |
| MA-06 | Local generation/retrieval works with explicit local credentials and no real OpenAI key. Missing credentials for a requested cloud operation fail explicitly. |
| MA-07 | Existing PII redaction, citation validation, scope filters, parent expansion, safe abstention, telemetry and failed-ingestion retention remain covered. |
| MA-08 | Required focused tests, Ruff and mypy pass. The full suite is run and all failures reported, including the known missing architecture HTML baseline. Constraints and evaluation thresholds remain unchanged. |

Live evidence is separate: verify model availability/digest, structured output,
actual embedding length and Atlas index readiness against synthetic data in an
isolated corpus. Offline success does not establish local hardware performance,
cloud receipt of traces or production security. No live execution is part of
this specification review.

## Boundaries

- **Always:** Read `CONSTRAINTS.md`; preserve application layers and current
  safeguards; validate trust boundaries; keep secrets out of logs; report failed
  checks without weakening them.
- **Ask first:** Changes to this approved scope, new dependencies, changes to CI,
  destructive migration of existing collections or new external publication.
  Explicitly approved implementation actions do not need repeated permission.
- **Never:** Mix embedding families, silently route a local request to cloud,
  expose credentials, lower quality gates, add suppressions to hide new errors,
  remove/skip tests, or claim fake results as live measurements.

## Implementation status and open evidence

No additional model-name or database-cluster assumptions are required for offline
implementation. Collection names in examples must be labelled examples; the
operator chooses actual names without changing the existing corpus. Local model
availability, deployment identity, dimensions and structured-output compatibility
remain live preflight evidence to collect later.

The user's explicit implementation instruction authorized execution of
`tasks/plan.md` and `tasks/todo.md` without another planning-only approval turn.
The original System Design DOCX/PDF remain proposal snapshots; the runtime guide
and verification report describe the delivered implementation and its limits.

## References

- [Approved capability map](CAPABILITY_MAP.md) — stable module ids and build order.
- [Constraints](CONSTRAINTS.md) and [component boundaries](APP_COMPONENT_GUIDE.md) — quality bar and implementation map.
- [System Design DOCX](training/decks/system_design/Model_Access_Design.docx) and
  [PDF](training/decks/system_design/Model_Access_Design.pdf) — template-based review companion; this specification owns acceptance criteria.
- [LangChain OpenAI embeddings](https://docs.langchain.com/oss/python/integrations/embeddings/openai) — client configuration and document/query embedding interface.
- [Requested embedding tag](https://ollama.com/library/qwen3-embedding:0.6b) — model catalogue entry; not proof of local availability.

Reconnaissance used current files. This workspace has no Git metadata and no
available context0 connector; history, ownership and checkpoint claims are absent.
