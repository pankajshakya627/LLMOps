# Container view — NexaAssist

Logical runtime and persistence view of the current working copy. A C4 container is a running application or data store; LangChain and service modules run inside the API/CLI and are not separate deployable services.

```mermaid
C4Container
  title Container diagram for NexaAssist
  Person(staff, "Staff member", "Reads cited policy explanations")
  Person(operator, "Operator", "Runs corpus maintenance")
  System_Boundary(nexa, "NexaAssist") {
    Container(ui, "Staff interface", "Streamlit / Python", "Renders answers and feedback")
    Container(api, "Policy API", "FastAPI / LangChain / Python", "Validates, retrieves and answers")
    Container(ingest, "Ingestion CLI", "LangChain / Python", "Parses and upserts changed content")
    ContainerDb(chunks, "Knowledge collections", "MongoDB Atlas Vector Search", "Child vectors and parent sections")
    ContainerDb(feedback, "Feedback collection", "MongoDB", "Pending and reviewed submissions")
  }
  System_Ext(models, "Model provider", "Embedding and chat APIs")
  System_Ext(phoenix, "Phoenix", "Optional operational telemetry")
  Rel(staff, ui, "Asks questions and submits feedback", "Browser")
  Rel(ui, api, "Requests answers and review actions", "JSON HTTP")
  Rel(operator, ingest, "Loads the document register", "CLI / local files")
  Rel(ingest, chunks, "Upserts changed chunks and parents", "PyMongo / integration")
  Rel(ingest, models, "Embeds changed child text", "HTTPS")
  Rel(api, chunks, "Searches scoped evidence and loads parents", "PyMongo / integration")
  Rel(api, feedback, "Stores and reviews feedback", "PyMongo")
  Rel(api, models, "Embeds queries, generates and judges", "HTTPS")
  Rel(api, phoenix, "Exports when configured", "OpenTelemetry / OpenInference")
```

The collections are logical stores in the configured database, not a claim that each is a separate database server. The ingestion CLI is a separate process. API services/chains are internal components. Optional hybrid search and reranking are configuration branches. Conversation persistence, automatic dataset promotion, semantic cache and blue/green promotion are not implemented by this training revision.

Code evidence: `app/main.py`, `app/ui/app.py:19`, `app/services/answer.py:21`, `app/services/retrieval.py:33`, `app/services/retrieval.py:65`, `app/chains/ingestion.py:38`, `app/database/mongo.py`, `app/database/feedback.py` and `app/services/evaluation.py`.

The API now exposes authenticated reviewer-curated golden export. The service reads accepted institution-scoped feedback and returns a strict case plus audit metadata. The Streamlit reviewer form offers JSONL and review-bundle downloads. No application server writes the golden dataset.
