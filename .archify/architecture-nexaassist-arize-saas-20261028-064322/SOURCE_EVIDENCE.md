# AWS Arize AX architecture source map

Working-tree references only; this workspace has no Git commit metadata.

- **Deployment scope and current-state warning:** `app/operations/AWS_DEPLOYMENT.md:3-5`
- **Staff HTTPS entry and ECS services:** `app/operations/AWS_DEPLOYMENT.md:20-29`, `:54-66`
- **Claude and Titan V2:** `app/operations/AWS_DEPLOYMENT.md:5`, `:74-83`
- **Application safety and Bedrock Guardrails:** `app/services/retrieval.py:23-32`, `app/chains/answer.py:97-208`, `app/operations/AWS_DEPLOYMENT.md:52`, `:116`
- **RAG and pgvector:** `app/services/answer.py:20-49`, `app/database/mongo.py:69-78`, `app/operations/AWS_DEPLOYMENT.md:64`
- **LiteLLM route and Arize callback migration:** `app/gateway/litellm.yaml:3-37`, `app/operations/AWS_DEPLOYMENT.md:102`
- **Arize AX SaaS and outbound OTLP:** `app/operations/AWS_DEPLOYMENT.md:63`, `:68-70`, `:106`
- **Current tracing migration gap:** `app/phoenix_main.py:29-75`, `app/operations/AWS_DEPLOYMENT.md:70`
- **Ragas and evaluation export migration:** `app/evaluation/live.py:18-84`, `app/evaluation/phoenix_export.py:36-80`, `app/operations/AWS_DEPLOYMENT.md:70`
- **Application RDS and S3 ingestion:** `app/operations/AWS_DEPLOYMENT.md:64-65`, `:108`, `:117-123`

Official product sources: [Arize OTel registration](https://arize.com/docs/ax/integrations/opentelemetry/opentelemetry-arize-otel), [Arize span evaluations](https://arize.com/docs/ax/evaluate/run-evals-on-traces), [LiteLLM Arize callback](https://docs.litellm.ai/docs/observability/opentelemetry_v2).
