# Session 2 — LLMOps Core: Observability, Evaluation & Security

Use the actual application during the demonstration: FastAPI endpoints, the
LiteLLM proxy and the application evaluation runner. Commands run from the
repository root. Phoenix, Ragas, LiteLLM and Guardrails AI are the worked tools;
use the [collector, tracing and score-export guide](../../app/observability/README.md).
DeepEval, Portkey and NeMo are comparison options.

## Prepare and start

Complete [runtime preparation](../../app/operations/README.md) before class: configure private `.env`
settings, confirm the requested Ollama models run, verify embedding dimensions,
create a compatible Atlas index and ingest the synthetic documents. The Qwen
profile uses separate collections from the OpenAI profile. Prepare the judge,
metric embeddings and Phoenix collector independently.

```bash
uv run --no-sync --env-file .env \
  --env-file app/gateway/ollama.env.example \
  python -m app.services.ingestion nexa_synthetic_data/document_register.json

uv run --no-sync --env-file .env \
  --env-file app/gateway/ollama.env.example \
  python -m uvicorn app.datadog_main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` and use **Try it out**. Equivalent curl
requests below run in another terminal. These calls use actual prepared
services; do not label them successful until you inspect their responses.

| Time | Demonstration | Evidence |
|---:|---|---|
| 15 min | `/retrieve` and `/answer` | Retrieved evidence, answer and citations |
| 15 min | Phoenix and `/metrics*` | Trace/log correlation, timings, tokens and failures |
| 15 min | `/answer/evaluated` and `app.evaluation.run` | Metric statuses, actual scores and gate decision |
| 10 min | Break | |
| 20 min | LiteLLM endpoints and routed `/answer` | Requested/served model, fallback, cache and deployment evidence |
| 15 min | Adversarial `/answer` and validator `/validate` | Expected versus observed protection behavior |

## 1. Retrieve evidence and generate an answer

Save one request for reuse throughout the session:

```bash
cat > /tmp/session2-question.json <<'JSON'
{"query":"What is the maximum loan amount for a NexaHome Loan?","as_of":"2026-10-01","product_id":"NEXA-HL","top_k":5}
JSON

curl --fail --silent --show-error http://127.0.0.1:8000/retrieve \
  -H 'Content-Type: application/json' --data-binary @/tmp/session2-question.json

curl --fail --silent --show-error http://127.0.0.1:8000/answer \
  -H 'Content-Type: application/json' --data-binary @/tmp/session2-question.json
```

Open `app/api/answer.py`, `app/services/answer.py` and `app/chains/answer.py`.
Compare retrieved text, returned `status`, `citations`, `generation_ms` and
`provenance`. Explain why a plausible sentence without supported evidence is
insufficient. Ingestion and serving are separate processes that share stores.

Keep the supporting RAGOps checks tied to this same application:

| Foundation topic | Application exercise | Inspect |
|---|---|---|
| Clause/table chunking | Open `app/chains/chunking.py` and ingest the real document register | Clause boundaries and preserved table text in retrieved evidence |
| Incremental ingestion | Rerun the same `app.services.ingestion` command against the same profile | Embedded/unchanged counts and stable chunk/parent identities |
| Policy dates | Repeat `/retrieve` and `/answer` with explicit June/July lookup and sanction dates | Effective policy/circular citations and applicability conditions |
| Embedding migration | Prepare separate Qwen and OpenAI corpora/indexes using their profiles | Model, actual dimensions and compatible chunk/parent store identities |

Record actual outcomes; do not substitute fixed fixture counts for the live
ingestion or retrieval results. Keep the old compatible corpus available while
validating a new embedding profile.

## 2. Observe one request and diagnose failure

With the Phoenix collector and application tracing configured as in the
[instructor guide](instructor.md#2-observability-and-tracing), send the saved
answer request. Find its trace in Phoenix and correlate it with JSON logs.
Inspect reported model identity, prompt version, tokens, available operation
durations and errors.

```bash
curl --fail --silent --show-error http://127.0.0.1:8000/health
curl --fail --silent --show-error http://127.0.0.1:8000/ready
curl --fail --silent --show-error http://127.0.0.1:8000/metrics
curl --fail --silent --show-error http://127.0.0.1:8000/metrics/latency
curl --fail --silent --show-error http://127.0.0.1:8000/metrics/answers

curl --silent --show-error -i http://127.0.0.1:8000/answer \
  -H 'Content-Type: application/json' -d '{}'
```

The last request should return HTTP 422 before model work. `/health` is process
liveness; `/ready` pings MongoDB, not the model or vector index. The two latency
endpoints summarize different operations. Explain which stage needs action.
Percentiles need multiple samples; this buffered API does not measure TTFT/TPOT.
Custom/gateway cost is `null`, not a measured zero.

## 3. Evaluate one answer and run a dataset

```bash
curl --fail --silent --show-error http://127.0.0.1:8000/answer/evaluated \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is the maximum loan amount for a NexaHome Loan?","as_of":"2026-10-01","product_id":"NEXA-HL","top_k":5,"reference_answer":"The maximum loan amount is 7.5 crore."}' \
  -o /tmp/session2-evaluated.json

uv run --no-sync python -m json.tool /tmp/session2-evaluated.json
```

Inspect `answer` and `quality.metrics`. Distinguish `scored`, `unavailable` and
`error`; never convert unavailable/error values to zero. Explain faithfulness,
answer relevancy, context precision and context recall using the actual context,
answer and reference. Judge reliability still requires human review.

For dataset evaluation using the same local candidate/corpus:

```bash
uv run --no-sync --env-file .env \
  --env-file app/gateway/ollama.env.example \
  python -m app.evaluation.run --dataset app/evaluation/datasets/answer.jsonl \
  --limit 3 --output /tmp/session2-evaluation.json
```

Inspect `records`, `ragas`, `evaluation_profiles` and `gate`. This runner
applies gates; `/answer/evaluated` returns scores without a release gate decision.
Thresholds in `app/evaluation/gates.json` remain placeholders. A failed gate may
save a completed report and exit nonzero. Use the
[instructor comparison commands](instructor.md#3-evaluation-and-llm-as-a-judge)
to compare Qwen and OpenAI chat with fixed cases, corpus and evaluator profiles.

## 4. Route through the actual gateway

Prepare the gateway key, OpenAI key and approved OpenAI model in the gateway
terminal using the existing secrets workflow:

```bash
uvx --python 3.13 --from 'litellm[proxy]==1.106.2' litellm \
  --config app/gateway/litellm.yaml --host 127.0.0.1 --port 4000
```

In another terminal with the gateway key available:

```bash
curl --fail --silent --show-error http://127.0.0.1:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"

curl --fail --silent --show-error -i http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"nexa-chat","messages":[{"role":"user","content":"Synthetic probe: reply READY."}]}'
```

Stop the original API process and start it with the gateway chat overlay:

```bash
CHAT_API_KEY="$LITELLM_MASTER_KEY" uv run --no-sync --env-file .env \
  --env-file app/gateway/ollama.env.example \
  --env-file app/gateway/gateway.env.example \
  python -m uvicorn app.datadog_main:app --host 127.0.0.1 --port 8000
```

Reuse `/answer` and inspect `provenance.chat_model`, `observed_chat_model` and
`gateway_cache_hit`. A missing cache header stays null. The default gateway
keeps caching off and uses Qwen-to-OpenAI chat fallback. Query embeddings keep
the compatible Qwen profile; there is no cross-family embedding fallback.

Perform the [routing matrix](instructor.md#4-gateways-routing-fallback-balancing-and-caching):
normal route, isolated primary failure, all targets unavailable, independent
replicas, repeated cached request and changed cache namespace. Use the provided
balanced/cache configurations. Record upstream calls and deployment evidence;
neither speed alone nor duplicate entries pointing to one server proves the
requested behavior. OpenAI embeddings require a separately ingested compatible
corpus/index; demonstrate that as a separate experiment.

## 5. Exercise security controls through endpoints

Send a synthetic personal identifier through the real application:

```bash
curl --fail --silent --show-error http://127.0.0.1:8000/answer \
  -H 'Content-Type: application/json' \
  -d '{"query":"My email is learner@example.com and PAN is ABCDE1234F. What is the maximum NexaHome loan amount?","as_of":"2026-10-01","product_id":"NEXA-HL","top_k":5}'
```

Inspect the `query_pii_redacted` log event and scrubbed model input at the service
boundary. The endpoint returns an answer, not a redaction report. Inspect
actual exported attributes before claiming the complete trace is sanitized.

Use the injection request in the [instructor guide](instructor.md#b-prompt-injection-boundaries)
and inspect its returned answer/citations. The desired behavior is supported
policy information or abstention, without obeying the injected approval request.
Record any unsafe response as a failed case. Escaping protects prompt structure;
a successful single request does not prove comprehensive injection resistance.

Start the actual validator FastAPI application separately:

```bash
LITELLM_LOCAL_MODEL_COST_MAP=True OTEL_SDK_DISABLED=true \
uv run --no-project --python 3.13 \
  --with-requirements app/security/requirements.txt \
  python -m uvicorn app.security.guardrails_service:app \
  --host 127.0.0.1 --port 8101
```

Validator implementation: [app.security.guardrails_service](../../app/security/guardrails_service.py).
Open `http://127.0.0.1:8101/docs` and call `POST /validate`. The
[instructor guide](instructor.md#d-guardrails-ai-service) supplies valid/invalid
JSON requests and an isolated validator-outage drill. Valid draft shape returns
`validation_passed: true`; an invalid status returns false. Enable the application
integration by restarting it with `GUARDRAILS_BASE_URL=http://127.0.0.1:8101`.
Schema validation supplements the separate PII/citation controls and does not
establish factual correctness or user authorization.

## Offline preparation and submission

Required offline verification uses existing tests and captured/mocked services:

```bash
uv run --no-sync pytest -v tests/test_training_labs.py tests/test_answer.py \
  tests/test_readiness_timeout.py tests/test_telemetry.py tests/test_redaction.py \
  tests/test_gateway.py tests/test_guardrails_integration.py
```

These checks contact no live model, Atlas or Phoenix service. They remain
preparation evidence; classroom endpoint calls require separately prepared live
services. Existing fixture sources remain available for code inspection.

Submit the request, observed response/status, trace or report identity, relevant
source file, failure classification and operational decision. Label evidence
**fixture**, **observed live**, **prediction** or **not measured**. Do not lower
thresholds or disguise a missing service as a successful demonstration.
