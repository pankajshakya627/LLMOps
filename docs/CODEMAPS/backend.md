<!-- Generated: 2026-11-20 | Files scanned: 80 | Token estimate: ~295 -->
# Backend

| Request | Handler and downstream work |
|---|---|
| POST /retrieve | Retrieval service → input policy and redaction → query embedding → scoped child search → parent evidence |
| POST /answer | Answer service → retrieval → generation → schema, exact-quote and citation checks |
| POST /answer/evaluated | Same answer path → evaluation with separate judge and embedding settings |
| POST /feedback | Validate the request and response → institution-scoped persistence |
| GET /feedback and POST /feedback/{id}/review or /golden | Reviewer bearer authentication → list, review, or export a golden example |
| GET /health and /ready | Liveness and database readiness |
| GET /metrics, /metrics/http, /metrics/answers and /metrics/latency | Process-level counters, HTTP monitoring and timing |

FastAPI routers live in `app/api/`, service orchestration in `app/services/`, and retrieval and model chains in `app/chains/`. The HTTP middleware records timings and request IDs. The ingest entry point is a CLI, `python -m app.services.ingestion`.

On AWS, LiteLLM applies the output limit for each configured chat or judge route. `app/gateway/output_limit.py` rejects oversized requests before forwarding them. Claude allows 4,096 output tokens. OpenAI and Bedrock allow 2,000.
