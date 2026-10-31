# Application gateway

LiteLLM runs as a separate Python 3.13 service. Direct proxy calls bypass the application PII/injection/citation checks. Keep the
gateway key private; policy clients should call FastAPI. The application uses its existing
OpenAI-compatible clients in [llm.py](../chains/llm.py) and
[embeddings.py](../chains/embeddings.py). No second router is implemented in FastAPI.

| Alias | Provider | Use |
|---|---|---|
| `nexa-chat` | Ollama `qwen3.5:9b-mlx` | Primary chat; one configured fallback model group |
| `nexa-chat-openai` | `OPENAI_LITELLM_CHAT_MODEL` | Approved OpenAI chat model |
| `nexa-embed-local` | Ollama `qwen3-embedding:0.6b` | Local query/document embeddings; verify expected 1024 dimensions |
| `nexa-embed-openai` | OpenAI `text-embedding-3-small` | 1536-dimensional embeddings for a separate corpus |

## Configuration

- [litellm.yaml](litellm.yaml): chat fallback, embeddings and no response cache.
- [litellm_cache.yaml](litellm_cache.yaml): the same routes with a five-minute,
  chat-only exact response cache in one worker's memory.
- [litellm_balanced.yaml](litellm_balanced.yaml): `nexa-chat-balanced` distributes
  calls between two independent Ollama deployments and falls back to OpenAI.

Gateway retries are capped at one, fallback depth at one, and timeout at 30 seconds.
The application client also has its existing bounded retry. Gateway profiles
clear the separate application fallback setting to avoid stacking cloud routing.
A provider error can trigger routing; a low Ragas score does not trigger routing.

`OLLAMA_BASE_URL` configures local chat. `OLLAMA_OPENAI_BASE_URL` independently
configures local embeddings. Embedding routes have no cross-family fallback.
API keys are supplied through the environment, not embedded in these YAML files.

## Docker

Prepare the root private `.env` and local pgvector schema (or optional Atlas indexes) as described in
[README.md](../../README.md), then run from the repository root:

```bash
docker compose --env-file .env -f app/compose.yaml up -d --build
```

Ollama runs natively on the host. Container defaults use `host.docker.internal`.
The MLX backend remains outside Docker; a model tag alone does not prove the
runtime/backend. On Linux, configure a host endpoint reachable from the container
network; a host service bound only to loopback is not reachable via host-gateway.

## Show provider-error fallback

Use the standard, uncached route and make only the chat endpoint unreachable.
The embedding endpoint stays available, so retrieval can still succeed:

```bash
LITELLM_CONFIG=litellm.yaml OLLAMA_BASE_URL=http://host.docker.internal:11439 \
  docker compose --env-file .env -f app/compose.yaml up -d --force-recreate gateway
```

Send `POST /answer` in Swagger. Inspect `provenance.observed_chat_model` and the
model span in Phoenix. This makes real cloud calls with the selected evidence;
use the synthetic course corpus and approved credentials. A failed retrieval
cannot be repaired by chat fallback. Restore the standard endpoint afterward:

```bash
docker compose --env-file .env -f app/compose.yaml up -d --force-recreate gateway
```

## Show caching

```bash
LITELLM_CONFIG=litellm_cache.yaml \
  docker compose --env-file .env -f app/compose.yaml up -d --force-recreate gateway
```

Send the same scoped `/answer` request twice. Inspect
`provenance.gateway_cache_hit` and the reported model in the response/Phoenix
spans. An absent cache header remains null. A faster response alone does not
establish a cache hit or a measured saving.

The application hashes its credential, access/corpus/embedding scope, model and
prompt version into the cache namespace. LiteLLM also keys on request content.
Changed evidence, scope or prompt should miss. Generated drafts still pass the
current PII/schema/citation/Guardrails checks on every call, including cache hits.
Only LLM generation is cached; retrieval and independent evaluation still run.

The cache is exact, process-local, single-worker and cleared on restart. It does
not cache embeddings or provide individual-user authorization. Use shared Redis
and an authorization design before scaling gateway workers or tenants.

## Show load balancing

Start two independent deployments with the same Qwen model tag. Replace the
example replica addresses with your actual endpoints:

```bash
LITELLM_CONFIG=litellm_balanced.yaml GATEWAY_CHAT_MODEL=nexa-chat-balanced \
OLLAMA_REPLICA_A_BASE_URL=http://host.docker.internal:11434 \
OLLAMA_REPLICA_B_BASE_URL=http://host.docker.internal:11435 \
  docker compose --env-file .env -f app/compose.yaml up -d --force-recreate gateway api
```

Repeat requests and inspect gateway deployment IDs/logs. The same model name in
Phoenix does not establish which replica served it. A second URL pointing at the
same daemon is not independent capacity. This config has caching disabled.

## Choose OpenAI embeddings

For pgvector, use separate OpenAI namespaces and the initialized local schema.
Only Atlas deployments need a queryable 1536-dimensional index named `policy_openai_gateway_v1`.
Select the profile for both ingestion and serving:

```bash
docker compose --env-file .env --env-file app/gateway/openai-embeddings.env.example \
  -f app/compose.yaml up -d --force-recreate api

docker compose --env-file .env --env-file app/gateway/openai-embeddings.env.example \
  -f app/compose.yaml run --rm api \
  python -m app.services.ingestion /data/document_register.json
```

This uses separate OpenAI chunk/parent collections. It does not reinterpret
existing Qwen vectors. Keep the profile selected for subsequent API recreation
and ingestion commands; changed model aliases/profile identities require matching
stored metadata.

## Native services and offline checks

For native startup use the commands in [README.md](../../README.md#native-services).
[service.env.example](service.env.example) provides native Ollama URLs;
[application.env.example](application.env.example) configures both chat and embedding routes. The smaller
[gateway.env.example](gateway.env.example) remains a chat-only overlay for an
existing direct-Ollama retrieval corpus.

Run the real LiteLLM router/cache code with labelled synthetic responses:

```bash
LITELLM_LOCAL_MODEL_COST_MAP=True OTEL_SDK_DISABLED=true \
uv run --no-project --python 3.13 --with-requirements app/gateway/requirements.txt \
  python -m app.gateway.selfcheck
```

The checks also cover the proxy authentication error handler dependency.
They assert that both fixture replicas are selected, forced provider failure
uses the backup, and cache scope/message changes miss. They make no live model
calls. Protocol examples are in [gateway.http](../examples/gateway.http).

Official references: [routing](https://docs.litellm.ai/docs/routing),
[fallbacks](https://docs.litellm.ai/docs/proxy/reliability),
[caching](https://docs.litellm.ai/docs/proxy/caching).


## View the actual provider in Phoenix

All three gateway profiles enable the official `arize_phoenix` callback. Compose
sets `LITELLM_OTEL_V2=true` and exports to the local collector project
**nexaassist-gateway**. Inspect `litellm.provider.model` and `llm.provider` there for
provider-level evidence rather than interpreting the API's `ChatOpenAI` class
or `nexa-chat` alias as an actual model identity.

Gateway raw message capture is disabled (`no_content`). The application project
**nexaassist-training** shows final responses when its synthetic content capture
is enabled; `/answer/evaluated` publishes Ragas annotations automatically. These
can be separate traces; do not infer fallback linkage from nearby timestamps.

The gateway has no configured `DATABASE_URL`, so LiteLLM UI request-history and
stored response content are not enabled. Phoenix remains this application's
observability store. Enabling gateway tracing does not enable UI spend-log
persistence. Native gateway launches should load `service.env.example` as shown
in the root README.
