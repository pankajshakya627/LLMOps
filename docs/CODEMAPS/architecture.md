<!-- Generated: 2026-11-20 | Files scanned: 79 | Token estimate: ~231 -->
# Application architecture

```text
Trainer browser → Streamlit → FastAPI → retrieval and answer chains
                                  ├→ PostgreSQL / pgvector
                                  ├→ Guardrails AI (validation)
                                  └→ private LiteLLM → OpenAI / optional direct Anthropic
Ingestion CLI → source register and checksum checks → embeddings → pgvector
GitHub Actions → tested images → ECR → SSM → one EC2 host
EC2 stdout → CloudWatch Logs                 Scheduler → Lambda → EC2 stop
```

`app/main.py` creates FastAPI. `app/streamlit_app.py` launches the trainer interface. `infra/aws/lab.py` provisions the stack, packages the release and controls its power state. A stopped host keeps its release directory and Docker volume on encrypted EBS. Explicit destroy removes the stack.

[Backend](backend.md) · [Frontend](frontend.md) · [Data](data.md) · [Dependencies](dependencies.md)
