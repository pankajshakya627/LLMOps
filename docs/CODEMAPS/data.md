<!-- Generated: 2026-11-20 | Files scanned: 79 | Token estimate: ~223 -->
# Data and persistence

| PostgreSQL table | Purpose |
|---|---|
| nexa_corpora | Namespace and immutable embedding identity |
| nexa_documents | Composite namespace/document key, text, metadata, optional child embedding |
| nexa_feedback | Institution and feedback ID with validated JSON payload |

`app/database/postgres.py:initialize` provisions the pgvector extension and tables. The document register carries source paths, dates, versions and checksums. Ingestion compares chunk identities and embeds changed content. Retrieval scopes evidence by institution, jurisdiction, confidentiality, product and date.

OpenAI chat and direct Claude share `openai-3-small-gateway-v1` and its 1,536-dimensional index. Bedrock uses separate Titan namespaces. The Compose project name fixes the volume identity across releases. Source and reports live in the release directory and session S3 bucket.
