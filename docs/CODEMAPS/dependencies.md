<!-- Generated: 2026-11-20 | Files scanned: 79 | Token estimate: ~223 -->
# Runtime dependencies

| Component | Connection |
|---|---|
| FastAPI and LangChain | OpenAI-compatible private LiteLLM API for chat, judging and embeddings |
| LiteLLM 1.106.2 | OpenAI HTTPS API; optional direct Anthropic Messages or separate Bedrock deployment |
| Guardrails AI | Python 3.13 validation sidecar on port 8101 |
| PostgreSQL 17 and pgvector | Primary AWS corpus, vectors and feedback |
| Streamlit | Server-side HTTP requests to FastAPI |
| CloudWatch Logs | EC2 Docker log driver and application request correlation |
| Optional Datadog | Agentless telemetry and a session-owned log forwarder |
| AWS control plane | GitHub OIDC, CloudFormation, EC2, SSM, Secrets Manager, ECR, S3, Scheduler and Lambda |

The application image uses Python 3.14 and a locked environment. The gateway runs separately on Python 3.13. Local Compose can use Ollama and local training profiles.
