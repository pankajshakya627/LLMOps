# NexaAssist architecture source map

These references point to the working tree. This workspace has no Git commit metadata, so they are not commit-pinned.

## Current local architecture

- **Staff browser**: `app/ui/app.py:423`–`455`
- **Streamlit UI**: `app/ui/app.py:190`–`219`, `app/ui/app.py:24`–`35`
- **FastAPI**: `app/main.py:28`–`41`, `app/api/answer.py:27`–`76`, `app/api/feedback.py:20`–`64`
- **Arize Phoenix**: `app/phoenix_main.py:29`–`75`, `app/evaluation/phoenix_export.py:36`–`80`, `app/compose.yaml:18`–`26`
- **Ollama host**: `app/gateway/litellm.yaml:3`–`17`, `app/compose.yaml:40`–`44`
- **Input policy**: `app/services/retrieval.py:23`–`32`, `app/security/input_policy.py:13`–`32`
- **RAG answer chain**: `app/services/answer.py:20`–`49`, `app/services/retrieval.py:35`–`64`, `app/chains/answer.py:97`–`208`
- **LiteLLM gateway**: `app/compose.yaml:28`–`58`, `app/gateway/litellm.yaml:1`–`37`
- **Ragas evaluation**: `app/services/evaluation.py:29`–`80`, `app/evaluation/live.py:18`–`84`
- **Guardrails AI**: `app/chains/guardrails.py:9`–`21`, `app/security/guardrails_service.py:19`–`30`, `app/compose.yaml:60`–`64`
- **PostgreSQL + pgvector**: `app/compose.yaml:3`–`16`, `app/database/mongo.py:69`–`78`, `app/database/feedback.py:23`–`27`
- **OpenAI**: `app/gateway/litellm.yaml:8`–`12`, `app/gateway/litellm.yaml:23`–`30`
- **Ingestion job**: `app/services/ingestion.py:29`–`59`, `app/services/ingestion.py:71`–`108`, `app/compose.yaml:72`–`72`

## Proposed AWS and Claude deployment

- **Staff browser**: `app/operations/AWS_DEPLOYMENT.md:24`–`30`
- **HTTPS entry**: `app/operations/AWS_DEPLOYMENT.md:24`–`30`, `app/operations/AWS_DEPLOYMENT.md:71`–`73`
- **Streamlit on ECS**: `app/operations/AWS_DEPLOYMENT.md:57`–`61`, `app/ui/app.py:190`–`219`
- **FastAPI on ECS**: `app/operations/AWS_DEPLOYMENT.md:57`–`61`, `app/phoenix_main.py:29`–`75`, `app/api/answer.py:27`–`76`
- **Bedrock Claude + Titan**: `app/operations/AWS_DEPLOYMENT.md:5`–`5`, `app/operations/AWS_DEPLOYMENT.md:75`–`83`
- **Phoenix on ECS**: `app/operations/AWS_DEPLOYMENT.md:63`–`71`, `app/phoenix_main.py:42`–`53`, `app/evaluation/phoenix_export.py:55`–`80`
- **App safety controls**: `app/operations/AWS_DEPLOYMENT.md:53`–`55`, `app/services/retrieval.py:23`–`32`, `app/chains/answer.py:169`–`208`
- **RAG answer chain**: `app/operations/AWS_DEPLOYMENT.md:27`–`42`, `app/services/retrieval.py:35`–`64`, `app/chains/answer.py:101`–`133`
- **LiteLLM on ECS**: `app/operations/AWS_DEPLOYMENT.md:59`–`63`, `app/operations/AWS_DEPLOYMENT.md:83`–`103`
- **Phoenix PostgreSQL**: `app/operations/AWS_DEPLOYMENT.md:64`–`71`, `app/operations/AWS_DEPLOYMENT.md:107`–`115`
- **Bedrock Guardrails**: `app/operations/AWS_DEPLOYMENT.md:13`–`20`, `app/operations/AWS_DEPLOYMENT.md:53`–`55`, `app/operations/AWS_DEPLOYMENT.md:115`–`117`
- **RDS PostgreSQL**: `app/operations/AWS_DEPLOYMENT.md:16`–`18`, `app/operations/AWS_DEPLOYMENT.md:65`–`69`, `app/database/mongo.py:69`–`78`
- **Ragas in FastAPI**: `app/operations/AWS_DEPLOYMENT.md:15`–`17`, `app/evaluation/live.py:18`–`84`, `app/evaluation/phoenix_export.py:36`–`80`
- **Versioned S3 corpus**: `app/operations/AWS_DEPLOYMENT.md:66`–`68`, `app/operations/AWS_DEPLOYMENT.md:116`–`124`
- **One-off ECS ingest**: `app/operations/AWS_DEPLOYMENT.md:116`–`124`, `app/services/ingestion.py:29`–`59`, `app/services/ingestion.py:71`–`108`

