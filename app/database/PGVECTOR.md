# Local PostgreSQL and pgvector

Use this backend when Atlas is unavailable. Policy chunks, parent sections,
linked circulars, evaluation source lookups and feedback all use PostgreSQL.
Phoenix remains the trace collector and Ragas remains the evaluator.

## Configuration

The private root `.env` needs a URL-safe `POSTGRES_PASSWORD`,
`STORAGE_BACKEND=pgvector` and a native `POSTGRES_DSN`:

```dotenv
STORAGE_BACKEND=pgvector
POSTGRES_PASSWORD=<URL-safe password>
POSTGRES_DSN=postgresql://nexaassist:${POSTGRES_PASSWORD}@127.0.0.1:5433/nexaassist
```

Keep password and DSN assignments in the same file for variable expansion.
Compose supplies the API's internal DSN automatically. No `MONGODB_URI` is
required in this mode. The existing `MONGODB_COLLECTION` and
`MONGODB_PARENT_COLLECTION` names identify PostgreSQL corpus namespaces; the
application reuses these settings to keep ingestion and query profiles aligned.

## Docker startup

Run from the repository root:

```bash
docker compose --env-file .env -f app/compose.yaml up -d --build
docker compose --env-file .env -f app/compose.yaml exec api \
  python -m app.database.postgres init
docker compose --env-file .env -f app/compose.yaml run --rm api \
  python -m app.services.ingestion /data/document_register.json
```

`init` provisions the extension, corpus manifest, document and feedback tables;
request paths do not perform schema migrations. Schema setup is repeatable and
does not delete existing rows. The local owner account provisions the extension;
production deployments should separate migration and runtime roles.

The PostgreSQL host port defaults to **5433** to avoid existing PostgreSQL
services. The volume `postgres-data` persists the corpus. Never use `down -v`
unless you intend to delete the local database. Atlas data is not copied or
modified; ingestion reads the checked synthetic source register again.

## Native API with existing Docker services

Install the locked application dependencies with `uv sync --locked --extra ui
--extra evaluation`. Reuse the running Docker database, gateway, Guardrails and
Phoenix. The following commands assume the gateway host port is **4001**:

```bash
docker compose --env-file .env -f app/compose.yaml up -d postgres
uv run --no-sync --env-file .env python -m app.database.postgres init

CHAT_BASE_URL=http://127.0.0.1:4001/v1 \
EMBEDDING_BASE_URL=http://127.0.0.1:4001/v1 \
uv run --no-sync --env-file .env --env-file app/gateway/application.env.example \
  python -m app.services.ingestion nexa_synthetic_data/document_register.json

CHAT_BASE_URL=http://127.0.0.1:4001/v1 \
EMBEDDING_BASE_URL=http://127.0.0.1:4001/v1 OTEL_SDK_DISABLED=false \
uv run --no-sync --env-file .env --env-file app/gateway/application.env.example \
  python -m uvicorn app.datadog_main:app --host 127.0.0.1 --port 8000
```

Stop an older native API before restarting it on port 8000. A process started
before changing `.env` retains its old backend until restarted. Docker normally
publishes the API on `API_PORT` (currently 8001 in the local private settings).
Gateway key aliases in `.env` must point to `LITELLM_MASTER_KEY` as documented
in the root README.

## Check retrieval before generation

Open FastAPI `/docs` at the selected API port and call `POST /retrieve`:

```json
{
  "query": "What is the maximum loan amount for a NexaHome Loan?",
  "as_of": "2026-10-01",
  "product_id": "NEXA-HL",
  "top_k": 5
}
```

Confirm evidence is returned before calling `/answer` and `/answer/evaluated`.
The reference limit is ₹7.5 crore; inspect citations rather than relying on HTTP
200. `/ready` checks the selected database and schema, not model availability or
a nonempty corpus. Use the response trace ID in Phoenix and inspect the automatically published
Ragas annotations using the [observability runbook](../observability/README.md).

## Retrieval and safety contract

- Vectors use pgvector's cosine distance operator, with similarity `1 - distance`.
- Exact search filters by institution, jurisdiction, confidentiality, product and
  inclusive policy dates before returning `top_k`. No manual vector index is
  required for this small corpus.
- Namespaces have immutable model/dimension/profile manifests. Different models
  or embedding families require new chunk and parent namespaces and re-ingestion.
- Zero, non-finite or dimensionally invalid vectors fail validation before writes.
- SQL values and metadata field names are bound parameters. Unknown filter
  operators fail closed. Circular completeness checks remain enabled.
- Feedback submission is idempotent; institution scope and pending-only review
  transitions are enforced in PostgreSQL.

The initial implementation supports **dense** retrieval. Hybrid mode is rejected
instead of silently changing search behavior. Exact scans and per-operation
connections suit this reference corpus; benchmark indexed search and a bounded
connection pool before production scale. Multi-stage ingestion retains the
existing per-document commit behavior, not an all-corpus transaction.

## Checks

See the [verified local deployment](../operations/PGVECTOR_VALIDATION.md) for
software results, live answers, Ragas outcomes and Phoenix trace IDs.

```bash
uv run --no-sync python -m pytest -q tests/test_pgvector.py
uv run --no-sync --env-file .env python -m pytest -q \
  tests/runtime/pgvector_profile_check.py
```

The second command needs the real local service and uses temporary namespaces.
It does not call Atlas or model providers.

Sources: [pgvector operators and exact search](https://github.com/pgvector/pgvector),
[Psycopg bound parameters](https://www.psycopg.org/psycopg3/docs/basic/params.html).
