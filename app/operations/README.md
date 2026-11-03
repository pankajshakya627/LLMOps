# Runtime configuration and operations

For the **1–2 hour, $3–$8 disposable AWS lab**, use the implemented
[AWS session deployment and GitHub Actions runbook](../../infra/aws/README.md).
It defaults to OpenAI chat/judging and `text-embedding-3-small` embeddings;
Bedrock inference and Guardrails are disabled unless explicitly enabled.

This runbook describes the current local routes. The proposed managed-model
deployment is in [AWS Bedrock deployment design](AWS_DEPLOYMENT.md); it uses
Arize AX enterprise SaaS for observability and is not enabled by the local
commands below. Local demonstrations still use self-hosted Phoenix.

The default local stack now uses **PostgreSQL/pgvector** and does not require
Atlas. Follow the [pgvector setup](../database/PGVECTOR.md) first. Atlas-specific settings below apply only
to `STORAGE_BACKEND=mongodb`.

The application now supports explicit OpenAI, Ollama and LiteLLM endpoint profiles.
Existing OpenAI defaults remain available. Phoenix spans, PII redaction, strict
answer schemas, citation checks and one citation-repair attempt are retained.

`OPENAI_FALLBACK_MODEL` optionally names an approved cloud model in `.env`.
When enabled, a provider failure or non-answered result with evidence can make
one bounded OpenAI attempt using the same retrieval. Inspect fallback provenance;
clear this setting for pure-local benchmarks. See [observability runbook](../observability/README.md)
for the exact behavior and limits.

Use the [Datadog runbook](../observability/README.md) for tracing, logs, metrics
and Ragas scores. Start `app.datadog_main:app`; `/answer/evaluated` publishes
scores automatically. Use `python -m app.evaluation.datadog_export` for recovery.

## 1. Configure and prepare

Copy `.env.example` to your private `.env` using the existing secrets workflow.
Keep real keys out of the example files. Model endpoints and credentials are
independent; a custom endpoint cannot inherit `OPENAI_API_KEY`. A local-only
answer/retrieval deployment needs no real OpenAI key. An explicitly requested
OpenAI evaluation still needs one.

Before local calls, follow the tag/digest, dimension and hardware checks in
[gateway preflight](../gateway/README.md#configuration). No models
were downloaded by the offline preparation checks. Later live results are
recorded separately in the validation reports. The `-mlx` tag does not by itself
establish which hardware/backend runs a deployment.

| Mode | Chat | Embeddings | Stores |
|---|---|---|---|
| Existing OpenAI | Repository model; Responses API | `text-embedding-3-small`, 1536 | Existing matching OpenAI corpus |
| Local overlay | `qwen3.5:9b-mlx`; Chat Completions | `qwen3-embedding:0.6b`; expected length verified against runtime | Separate Qwen chunks, parents and index |
| Gateway overlay | `nexa-chat` through LiteLLM | Keeps the selected embedding profile | Keeps that profile's compatible corpus |

The example local profile declares 1024 dimensions. Check the returned vector
length before creating the index. The exact example JSON is in
[app/database/indexes.md](../database/indexes.md). Use new store names and
keep the existing OpenAI corpus intact. The app refuses incompatible or unknown
stored profiles before query embedding or ingestion mutation. Profile labels
declare deployment identity; the app does not infer a model digest from an alias.

The local Qwen profile sets `CHAT_REASONING_EFFORT=none`. A live run showed the
model defaulting to thinking and exhausting the 2,000-token output cap before
returning structured JSON. Ollama's documented `reasoning_effort: none` control
was verified against this deployment; the cap stays in place. The independent
judge does not inherit this candidate setting. Gateway overlays clear the client
override and apply the setting only to local Qwen deployments in LiteLLM, so the
cloud fallback retains its own model policy.

After preparing the **new**, queryable Qwen index, ingest synthetic documents:

```bash
uv run --no-sync --env-file .env --env-file app/gateway/ollama.env.example \
  python -m app.services.ingestion nexa_synthetic_data/document_register.json
```

Start the API with the same overlay and a running Phoenix collector:

```bash
uv run --no-sync --env-file .env --env-file app/gateway/ollama.env.example \
  python -m uvicorn app.datadog_main:app --host 127.0.0.1 --port 8000
```

`/health` checks the process; `/ready` retains the database ping contract. Neither
claims model availability or index readiness. Stored-profile checks scan metadata
with a two-second deadline. Ingestion remains non-transactional across collections;
concurrent profile migration is not supported.

## 2. Route through LiteLLM

Set `LITELLM_MASTER_KEY` in the shell/secrets manager, plus `OPENAI_API_KEY` and
`OPENAI_LITELLM_CHAT_MODEL=openai/<approved-model-id>` for the explicitly configured
cloud fallback. Starting this configuration permits local-to-cloud fallback for
chat; embeddings have no model-family fallback.

```bash
uvx --python 3.13 --from 'litellm[proxy]==1.106.2' litellm \
  --config app/gateway/litellm.yaml --host 127.0.0.1 --port 4000

CHAT_API_KEY="$LITELLM_MASTER_KEY" uv run --no-sync --env-file .env \
  --env-file app/gateway/ollama.env.example \
  --env-file app/gateway/gateway.env.example \
  python -m uvicorn app.datadog_main:app --host 127.0.0.1 --port 8000
```

For independent gateway embedding routes, configure `EMBEDDING_BASE_URL`,
`EMBEDDING_API_KEY`, `EMBEDDING_MODEL` and `EMBEDDING_PROFILE` consistently for both
ingestion and query. Switching route aliases changes stored model metadata; use
the same route for the selected corpus, or build another isolated corpus.

`litellm_balanced.yaml` is an optional alternative. Its
`OLLAMA_REPLICA_A_BASE_URL` and `OLLAMA_REPLICA_B_BASE_URL` must name two genuinely
independent running deployments. Select `CHAT_MODEL=nexa-chat-balanced`; keep the
same compatible embedding profile. Each configuration bounds retries, timeout and
fallback depth. See the existing live guide for primary-down and both-down drills.

`Provenance.chat_model` records the requested model or alias.
`observed_chat_model` records the model reported by the provider; it is not proof
of a physical deployment. `gateway_cache_hit` records the gateway header when
available. Missing fields remain null. These fields remain visible in answer provenance and saved feedback. JSON token logs retain reported model identity.
For custom/gateway endpoints, `/metrics/answers` reports cost as null; one static
price pair cannot price mixed routes. Tokens and latency are still counted.

### Opt-in exact response cache

Use `litellm_cache.yaml` in a **dedicated single-worker local reference gateway** with a
private gateway key. Set `CHAT_CACHE_NAMESPACE=class-private-v1` on the application.
The client hashes that namespace, its credential, institution/access scope, corpus,
embedding identity and prompt version into LiteLLM's cache namespace. Native cache
keys additionally cover the request messages, including retrieved evidence.
Changing scope, evidence, prompt or model causes a separate lookup. Cached model
drafts still undergo current PII, schema, guardrail and citation checks.

The default gateway has caching off. The optional cache is memory-only, chat-only
and has a 300-second TTL. Restarting the gateway clears it. This lab configuration
does not provide a shared cache for replicas or user-level authorization; the app
serves one configured access scope. Verify reported hits/upstream calls rather
than inferring hits from latency. A gateway client bypassing the application must
maintain its own cache-isolation contract.

## 3. Guardrails AI output validation

Guardrails AI 0.11 requires Python below 3.14. Run its local validation process in
an isolated Python 3.13 tool environment; the application stays on Python 3.14.
The service shares the real `AnswerDraft` JSON Schema, uses no LLM reasks, disables
Guardrails metrics collection and explicitly disables remote Guardrails execution.

```bash
LITELLM_LOCAL_MODEL_COST_MAP=True OTEL_SDK_DISABLED=true \
uv run --no-project --python 3.13 \
  --with-requirements app/security/requirements.txt \
  python -m uvicorn app.security.guardrails_service:app \
  --host 127.0.0.1 --port 8101
```

Open `http://127.0.0.1:8101/docs` to exercise `POST /validate` directly. The
[security guide](../security/README.md#run-guardrails-ai) supplies the valid and
invalid request bodies; a response body with `validation_passed: false` is a
rejection even though the service returned HTTP 200.

Set `GUARDRAILS_BASE_URL=http://127.0.0.1:8101` for the application process.
With it configured, validation rejection, malformed responses and an unavailable
service fail closed; the API returns its sanitized failure response. Generated
PII is rejected before sending a draft to the validation process. The service
binds loopback and is not an authenticated public endpoint; remote deployment
needs an authenticated TLS boundary. Without the setting, current Pydantic and
citation rails remain active.

Prompt role separation and escaped data remain the injection defenses. Exact
citations and output validation catch additional failure classes. Neither regex
PII detection nor schema validation proves comprehensive semantic injection
resistance; keep the existing adversarial exercises and human review.

## 4. Fixed evaluation profiles

`EVAL_JUDGE_MODEL`, `EVAL_JUDGE_BASE_URL`, `EVAL_JUDGE_API_KEY` and
`EVAL_JUDGE_API_MODE` configure the judge independently. If no judge model is set,
the repository's fixed default `gpt-6-luna` is used rather than inheriting a new
candidate. `EVAL_EMBEDDING_MODEL`, `EVAL_EMBEDDING_DIMENSIONS`,
`EVAL_EMBEDDING_BASE_URL`, `EVAL_EMBEDDING_API_KEY` and
`EVAL_EMBEDDING_PROFILE` configure Ragas metric embeddings independently from
retrieval. Custom evaluator endpoints need explicit credentials, too.

After preparing services, compare candidate **chat** models against the same Qwen
corpus and frozen cases. Keep judge and metric embedding settings unchanged:

```bash
CHAT_API_KEY="$LITELLM_MASTER_KEY" uv run --no-sync --env-file .env \
  --env-file app/gateway/ollama.env.example \
  --env-file app/gateway/gateway.env.example \
  python -m app.evaluation.run --dataset app/evaluation/datasets/answer.jsonl \
  --output /tmp/qwen-candidate.json

CHAT_MODEL=nexa-chat-openai CHAT_API_KEY="$LITELLM_MASTER_KEY" \
uv run --no-sync --env-file .env --env-file app/gateway/ollama.env.example \
  --env-file app/gateway/gateway.env.example \
  python -m app.evaluation.run --dataset app/evaluation/datasets/answer.jsonl \
  --output /tmp/openai-candidate.json

uv run --no-sync python -m app.evaluation.compare \
  /tmp/qwen-candidate.json /tmp/openai-candidate.json
```

Inspect observed responding models: a cloud fallback is not a pure Qwen sample.
Reports preserve the exact supplied contexts, per-case provenance, evaluator
settings. Phoenix publication uses the separate live-response annotation exporter. The comparator refuses differing
evaluator profiles in new reports. Batch queries and reference answers are
redacted before judging and recording them. Existing gates remain placeholders
and are not lowered by this implementation. Evals may exit nonzero on a gate
failure while still saving their report.

## 5. Classroom entry points and offline verification

Use the actual FastAPI application during class:

| Topic | Entry point or endpoint | Inspect |
|---|---|---|
| Start serving | `python -m uvicorn app.main:app` under the configured launcher above | `/docs`, process and dependency readiness |
| Retrieve and answer | `POST /retrieve`, `POST /answer` | Evidence, status, citations and provenance |
| Observability | `GET /metrics`, `/metrics/latency`, `/metrics/answers` and Phoenix | Timings, model tokens, errors and trace identity |
| Score one answer | `POST /answer/evaluated` | Answer and explicit per-metric statuses |
| Evaluate a dataset | `python -m app.evaluation.run` | Saved per-case results and release gates |
| Compare reports | `python -m app.evaluation.compare` | Metric deltas and comparable evaluator profiles |
| Route requests | LiteLLM `/v1/chat/completions` and routed `/answer` | Requested versus responding model |
| Validate a draft | Validator `POST /validate` on port 8101 | Valid/invalid schema decisions |

Use the [gateway HTTP examples](../examples/gateway.http) and
[security HTTP examples](../examples/security.http) for executable requests.
Keep offline fixture evidence separate from live service verification.

The app tests use HTTP mock transports and in-memory stores:

```bash
uv run --no-sync pytest -q tests/test_model_access.py tests/test_embedding_profiles.py \
  tests/test_eval_profiles.py tests/test_gateway.py tests/test_gateway_config.py \
  tests/test_guardrails_integration.py tests/test_guardrails_sidecar.py
uv run --no-sync ruff check .
uv run --no-sync mypy .
uv run --no-sync pytest -q tests
```

These tests do not establish live model quality, GPU performance, Atlas index
readiness, physical replica balancing, production cache security or cloud trace
receipt. Previous isolated framework-check evidence remains recorded in
[application validation](VALIDATION.md).

Official references: [Ollama compatibility](https://docs.ollama.com/api/openai-compatibility),
[LiteLLM routing](https://docs.litellm.ai/docs/proxy/load_balancing),
[LiteLLM fallback](https://docs.litellm.ai/docs/proxy/reliability),
[LiteLLM cache](https://docs.litellm.ai/docs/proxy/caching),
[Guardrails Python requirement](https://github.com/guardrails-ai/guardrails/blob/main/pyproject.toml).
