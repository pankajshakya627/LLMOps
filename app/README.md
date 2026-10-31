# NexaAssist application

An enterprise policy intelligence reference application with scoped retrieval,
validated answers, model routing, observability, evaluation and reviewed feedback.
NexaBank and its reference data are fictional. The application does not make
credit decisions or claim production security certification.

## Runtime ownership

Application code, service dependencies, operational configuration and default
quality fixtures live under `app/`. Root `pyproject.toml` / `uv.lock` describe the
Python package, and the private root `.env` supplies deployment secrets. Tests
and documentation authoring remain outside the application runtime.

```text
app/
  api/              HTTP contracts, authorization, rate limits and operational routes
  services/         Retrieval, answers, ingestion, evaluation and feedback workflows
  chains/           Parsing, chunking, prompts, generation and validation
  models/           Strict application schemas and provenance
  database/         PostgreSQL/pgvector and Atlas adapters, scope and profile checks
  core/             Settings, structured logging, counters and trace correlation
  gateway/          LiteLLM profiles, dependency set, container and protocol checks
  security/         Input policy and isolated Guardrails AI validator
  observability/    Phoenix collector/client requirements and observability runbook
  evaluation/       Ragas adapters, quality/SLO gates, datasets and report commands
  operations/       Runtime configuration and validation evidence
  examples/         Executable HTTP request examples
  ui/               Streamlit client and feedback review
  compose.yaml      Local service orchestration
  Dockerfile        API/UI image built from app-owned runtime resources
```

## Service entry points

| Service | Entry point | Runtime |
|---|---|---|
| Instrumented API | `app.phoenix_main:app` | Python 3.14; FastAPI/OpenInference |
| Offline API factory | `app.main.create_app()` | Shared routers without an exporter |
| User interface | `app/streamlit_app.py` | Python 3.14; Streamlit |
| Gateway | LiteLLM with `app/gateway/litellm.yaml` | Separate Python 3.13 service |
| Output validator | `app.security.guardrails_service:app` | Separate Python 3.13 service |
| Trace collector | `phoenix serve` | Separate Python 3.13 service |

Start the Docker stack from the repository root after configuring `.env`, native
Ollama and local PostgreSQL credentials:

```bash
docker compose --env-file .env -f app/compose.yaml config --quiet
docker compose --env-file .env -f app/compose.yaml up -d --build
docker compose --env-file .env -f app/compose.yaml exec api python -m app.database.postgres init
docker compose --env-file .env -f app/compose.yaml run --rm api \
  python -m app.services.ingestion /data/document_register.json
```

The private `.env` can override host ports. Keep service-to-service addresses as
configured in Compose. Do not run overlapping Compose operations or remove older
services/volumes merely to clear an orphan warning.

For a standalone Phoenix collector:

```bash
PHOENIX_HOST=127.0.0.1 PHOENIX_PORT=6006 PHOENIX_GRPC_PORT=4317 \
PHOENIX_WORKING_DIR=/tmp/nexaassist-phoenix PHOENIX_TELEMETRY_ENABLED=false \
uv run --no-project --python 3.13 \
  --with-requirements app/observability/requirements-server.txt phoenix serve
```

Reuse an existing collector when port 6006 is already occupied.

## Operational runbooks

- [Disposable AWS deployment](../infra/aws/README.md): OpenAI chat, judging and
  embeddings by default, with optional Bedrock instructions and automatic teardown.
- [Optional AWS Bedrock deployment](operations/AWS_DEPLOYMENT.md):
  managed chat/embeddings, Bedrock Guardrails, Phoenix/Ragas roles, service placement
  and the migration checks required before replacing the local Ollama stack.
- [AWS Bedrock deployment presentation](presentations/NexaAssist_AWS_Bedrock_20261027/README.md):
  18 editable slides with speaker notes, architecture, migration and incident exercises.
- [Deployment and LLMOps operations presentation](presentations/NexaAssist_Deployment_Operations_20261027/README.md):
  24 editable slides, speaker notes, deployment commands and incident exercises.
- [Gateways and guardrails training guide](operations/GATEWAYS_AND_GUARDRAILS_GUIDE.md):
  architecture, source-line maps, request flow, mechanism selection and demonstrations.
- [Runtime configuration](operations/README.md): compatible endpoint profiles,
  credentials, ingestion, independent evaluator settings and API operations.
- [Observability](observability/README.md): collector deployment, trace
  correlation, masking, prompt versions, automatic evaluated-request annotations and manual recovery.
- [Gateway](gateway/README.md): local/cloud routes, bounded fallback, independent
  embedding families, balancing and exact response caching.
- [Security](security/README.md): PII handling, explicit injection checks, schema
  validation, exact citations and validator-outage behavior.
- [Evaluation](evaluation/README.md): golden cases, batch quality gates, retrieval
  comparison and SLO checks.
- [Local pgvector](database/PGVECTOR.md): Atlas-free startup, schema and retrieval.
- [Storage/index contract](database/indexes.md): scope filters, dimensions and
  separate corpus/index requirements.
- [Validation](operations/VALIDATION.md): verified behavior and limits.

## Data and credentials

The synthetic PDF corpus is an external ingestion input, mounted read-only at
`/data` by Compose. It is separate from application code and is never downloaded
implicitly. PostgreSQL schema creation is explicit; Atlas deployments create
their search indexes explicitly before ingestion. An ingestion
command writes to its selected collections; no model-family fallback is allowed
for embeddings.

Default quality fixtures are owned by
[evaluation/datasets](evaluation/datasets/). The current gate configuration is
[evaluation/gates.json](evaluation/gates.json). Placeholder thresholds are not a
production release policy and must not be lowered to clear a failed evaluation.

Do not put credentials in service images, examples or logs. Keep Phoenix content
capture disabled for private data. Preserve the existing Phoenix project name
when inspecting earlier traces; the default identifier remains
`nexaassist-training` for continuity and can be configured for new deployments.

## Verification

```bash
RAGAS_DO_NOT_TRACK=true uv run --locked --no-sync python -m pytest -q tests
uv run --locked --no-sync ruff check app tests
uv run --locked --no-sync mypy app
```

The dependency-isolated SDK self-checks and real service commands are documented
in their runbooks. Offline fixture results establish software behavior, not live
model correctness, database/index readiness or production capacity.
