# NexaAssist architecture explorer

Open [nexaassist-architecture.html](nexaassist-architecture.html) in a browser.
It is self-contained and needs no server, CDN, model credentials or network access.
Keep it inside `C4-Documentation/` for its relative source links to work.

- **Runtime containers:** UI, FastAPI, configured models, the separate ingestion
  process, Atlas and optional Phoenix telemetry.
- **Answer request:** HTTP validation, service orchestration, scoped retrieval,
  structured generation and output validation.
- **Document ingestion:** source loading, parsing, chunking, metadata/checksums
  and incremental publication into compatible Atlas stores.

Use the view selector and Previous/Next buttons to follow a narrated path.
Click a component, or focus it with Tab and press Enter, to inspect its source
files and responsibilities. Highlighted paths animate unless your browser's
reduced-motion preference is enabled. Hover an arrow to read its relationship.

The embedded `architecture-data` JSON is the component and walkthrough source.
`tests/test_architecture_document.py` checks its file paths, node/edge identities
and walkthrough references. Edit that data alongside implementation changes.

This map describes the repository; it is not a record of live service health.
Atlas index creation is manual, embedding profiles must match their corpus,
and ingestion writes across collections are not atomic. The optional Guardrails
AI process uses Python 3.13 while the main application uses Python 3.14.
Evaluation judges and metric embeddings have independent profiles.

Use [the Session 2 runtime guide](../app/operations/README.md) to run services
and evaluation reports, and [the README](../README.md#1-architecture) for the
larger static C4 diagrams. LangGraph and FastMCP remain future layers.
