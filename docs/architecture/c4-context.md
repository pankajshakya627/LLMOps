# System context — NexaAssist

Current training implementation, inspected 2026-10-23. The folder has no Git metadata, so this is a working-copy view, not a commit-pinned architecture. The source course's support assistant is adapted to synthetic banking policy.

```mermaid
C4Context
  title System Context diagram for NexaAssist
  Person(staff, "Staff member", "Asks synthetic policy questions")
  Person(reviewer, "Reviewer", "Reviews feedback with bearer credential")
  Person(operator, "Operator", "Runs registered-document ingestion")
  System(nexa, "NexaAssist", "Cited policy explanations and safe abstention")
  System_Ext(models, "Model provider", "Embedding and chat APIs")
  SystemDb_Ext(atlas, "MongoDB Atlas", "Vectors, parents and feedback")
  System_Ext(phoenix, "Phoenix", "Optional traces and LLM evaluations")
  Rel(staff, nexa, "Submits question and scope", "Browser / JSON HTTP")
  Rel(reviewer, nexa, "Reviews feedback", "Bearer / JSON HTTP")
  Rel(operator, nexa, "Starts registered-file ingestion", "Python CLI")
  Rel(nexa, models, "Embeds text and generates answers", "HTTPS")
  Rel(nexa, atlas, "Reads evidence and persists records", "MongoDB wire protocol")
  Rel(nexa, phoenix, "Exports telemetry when enabled", "OpenTelemetry / OpenInference")
```

Evidence: `app/ui/app.py`, `app/api/answer.py`, `app/api/auth.py`, `app/services/ingestion.py`, `app/chains/llm.py`, `app/chains/embeddings.py`, `app/database/mongo.py`, `app/database/feedback.py`, `app/phoenix_main.py`, `app/services/evaluation.py`.

The app does not execute credit decisions. Phoenix is conditional; live dependencies were not exercised. End-user identity, authorization and production deployment controls need a separate design decision. Context-view external services are black boxes; these are not additional in-process modules.
