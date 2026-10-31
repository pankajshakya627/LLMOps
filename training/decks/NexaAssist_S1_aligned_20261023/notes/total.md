# 01_Discover

NexaAssist / LLMOps engineering workshop Session 1 of 5 · 16-slide teaching edition Introduce the running project: a synthetic banking-policy assistant. By the end, each pair will have a use-case manifest, a data access decision and measurable proposed targets. This revised deck follows the course lesson sequence; exact lesson URLs appear in section notes and the coverage map.

---

# 02_LLMOps manages behavior under real constraints

Correctness and safety are part of the product. Latency shapes whether people can use the service. Token consumption determines variable cost. Start with a staff policy assistant that gives fluent but unsupported advice. Ask which operational signal reveals each problem. A fast HTTP response, cheap model or well-written prompt does not establish all three dimensions at once. Source lesson: https://www.educative.io/courses/llmops/what-is-llmops-and-why-does-it-exist.

---

# 03_From models to operated applications

AI → ML → GenAI → LLMs: a scope relationship. The application owns data, prompts and integration. Hosted-model behavior still needs measured evidence. AI also includes non-learning systems; this is not a deployment pipeline. Research, the 2022 interface shift and the integration era explain the changing operating burden. Prompts, embeddings and knowledge change independently. These themes consolidate the longer lesson-2 reference pages. Source lesson: https://www.educative.io/courses/llmops/how-we-reached-llmops.

---

# 04_What changes from MLOps to LLMOps

Data: Features → documents + vectors Tuning: Parameters → prompts + retrieval Artifacts: Weights → coupled runtime assets Evaluation: Labels → semantic criteria These are parallel comparison dimensions, not an ordered pipeline. Traditional ML still uses data and LLM systems can still be fine-tuned. This view highlights the primary levers in an API-backed RAG application. Source lesson: https://www.educative.io/courses/llmops/mlops-to-llmops-what-changes-and-what-stays.

---

# 05_Four phases, four decisions

Discover: Problem + permitted data Distill: Prove retrieval and generation Deploy: Validate the serving envelope Deliver: Observe and improve The stages form a recurring lifecycle; the drawing shows one pass. Reviewed failures feed the next discovery and experimentation cycle. A phase gate needs a named artifact and an explicit decision. Source lesson: https://www.educative.io/courses/llmops/the-4d-framework-discover-distill-deploy-deliver.

---

# 06_C4 / system context

People ask, review and maintain policy knowledge. NexaAssist depends on models, Atlas and optional telemetry. Read the system as a black box. Staff ask scoped questions, the reviewer reviews feedback using a bearer credential, and the operator runs registered-file ingestion. The external model provider embeds and generates via HTTPS. Atlas supplies managed storage through the MongoDB protocol. Datadog receives ddtrace/LLMObs telemetry only when enabled. This working-copy view is not a production deployment or proof of user-level authorization. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application. The implementation or concept reference is docs/architecture/c4-context.md.

---

# 07_C4 / containers and ownership

Streamlit renders; FastAPI coordinates the answer path. The ingestion CLI maintains Atlas knowledge collections. Inside NexaAssist, Streamlit, FastAPI and the ingestion CLI are separate running applications. LangChain runs inside API/CLI processes and is not a separate service. Atlas stores child vectors, parent sections and feedback; these are logical collections, not separate database servers. The CLI embeds changed text through the model provider and upserts chunks/parents. The API reads scoped evidence, embeds queries, generates answers and optionally exports telemetry. The UI calls the API using JSON HTTP. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application. The implementation or concept reference is docs/architecture/c4-containers.md.

---

# 08_Two paths share one knowledge contract

Offline: prepare and publish trusted searchable evidence. Online: retrieve, generate and validate a scoped answer. The offline path runs registered files through verification, parse, clause chunking, configured PII redaction, metadata/checksum comparison, changed-chunk embedding and upsert. Child vectors and unembedded parent sections live in Atlas. Online, validated scope and a scrubbed query drive retrieval; parents and complete linked amendments feed the answer prompt. The provider drafts a strict response and local citation/output checks accept it, ask for clarification or abstain. The two paths share document identity, effective dates and embedding compatibility. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application. The implementation or concept reference is app/chains/ingestion.py; app/services/retrieval.py; app/chains/answer.py.

---

# 09_One answer / request and failure flow

Validate → retrieve scoped evidence → build the prompt. Generate → check output → return answer or abstention. The route validates the request and rate limit, then delegates. The service scrubs query identifiers. Retrieval applies institution, dates, jurisdiction, confidentiality and optional product filters, expands parents and resolves linked amendments. Missing evidence or an amendment that cannot fit ends in safe abstention without generation. Otherwise the strict draft is checked for PII and exact citations. Citation failure permits one repair, then abstention. A scope clarification becomes a fixed safe question. Returned provenance identifies prompt/model/retrieval/evidence. Sampling is optional background work, not streaming. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application. The implementation or concept reference is app/api/answer.py; app/services/answer.py; app/chains/answer.py.

---

# 10_Freshness, permission and traceability are separate

A fresh document can still be unauthorized. A permitted document can still be obsolete. An answer needs a recoverable source identity. Data divergence is the gap between expected knowledge and what the index contains. In NexaAssist, effective-date and metadata filters constrain retrieval and provenance preserves source references. Corpus freshness approvals are still owner decisions. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

---

# 11_Code / pure chain, strict draft

The same LCEL chain is callable from the service and evaluation. Open app/chains/answer.py and locate generation = ANSWER_PROMPT. Read the displayed excerpt in context; it is taken directly from the application. The same LCEL chain is callable from the service and evaluation. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application. The implementation or concept reference is app/chains/answer.py.

---

# 12_Scope the policy assistant before release

Staff receive cited explanations or safe non-answers. Credit decisions and account actions are outside scope. The manifest names permitted sources and unresolved owners. The Educative project is a fictional internal support assistant. NexaAssist adapts its principles to synthetic banking policy, retaining MongoDB Atlas and LangChain rather than PostgreSQL/pgvector and LiteLLM. Read training/use_case_manifest.md. Distinguish source permission from document freshness. Actual data, SME, product and operational approvers remain owner decisions. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

---

# 13_Code / reject changed source bytes

A source must match the register before parsing or embedding. Open app/services/ingestion.py and locate def _verify_source. Read the displayed excerpt in context; it is taken directly from the application. A source must match the register before parsing or embedding. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application. The implementation or concept reference is app/services/ingestion.py.

---

# 14_Practical / prove the source boundary

python -m training.showcase --session 1 Observe: 8 original documents verify. Tampered copy: hash mismatch; ingestion is refused. Allow 20 minutes of the practical block. Predict the failing document, run the demonstration and inspect requests_from_register/_verify_source. Only a temporary copy is modified. Record the ID, verification error and release decision. Byte identity alone does not prove permission or correct policy meaning. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

---

# 15_The release file is more than application code

Record prompt, model, corpus and embedding identities. Attach golden results and measured operating evidence. Keep placeholder targets and missing approvals visible. Use app/evaluation/gates.json and training/use_case_manifest.md. Thresholds and token prices remain placeholders; no live service or capacity evidence is established by offline fakes. CI, durable memory and blue/green promotion remain separate work. A compatible rollback includes chunk and parent collections, not only an index name. Read the longer handout for the gate-schema exercise. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

---

# 16_Session 1 / architecture exit gate

Trace one staff question across the real layers. Explain which source or output failure stops an answer. Submit the scope manifest and source-verification evidence. Use the diagrams and literal code excerpts as the assessment. Ask why LangChain is inside the API process, why lookup date differs from sanction date, and why missing measurement is not a pass. Supporting detail remains in the Session 1 handout and archived expanded deck. Next, prove the retrieval evidence before changing generation.
