# NexaAssist teaching use-case manifest

Status: teaching draft; targets and organizational approvals require owner confirmation.

Users: staff learning to retrieve and explain synthetic NexaBank policy clauses. Output is a cited explanation, safe abstention or scope question. No credit decision or action execution is authorized.

Sources: `nexa_synthetic_data/document_register.json`; registered authoritative documents, hashes, effective dates and amendments. Read access and provider disclosure must be approved for any replacement real corpus. Synthetic training data does not grant permission to send real customer data.

Pipeline: PDF/Markdown → parse → clause chunks → redact → deterministic checksum → MongoDB Atlas chunks and parent sections. Online: validated request → query rail → scoped retrieval → parent context → LCEL structured draft → output PII rail and citation checks → API → Streamlit.

Quality targets: `app/evaluation/gates.json`, currently placeholder. Data owner, product owner, SME, operational owner and approval dates: Requires clarification before a real release. Freshness/re-ingestion interval: Requires owner decision. Test fixtures are not live performance evidence.

Risks: stale amendments, missed context, unsupported claims with valid quotes, regex PII misses/false positives, unmeasured cost, per-process quotas, and client-submitted feedback. Controls are implemented and exercised in `training/`; remaining controls need separate release decisions.

Release evidence: dataset hash, prompt fingerprint, model/retrieval configuration, quality report, load/SLO results, reviewer decision, known-good rollback configuration. Training pass is separate from production approval.

Teaching implementation update: prompt 1.1.0 includes escaped data boundaries. Evaluation runs identify the scoped cases and reviewed expectations; incompatible comparisons are refused. Accepted feedback can be exported with an explicit curated target and review bundle through an authenticated API and reviewer screen. Export does not automatically validate policy meaning or promote a dataset.
