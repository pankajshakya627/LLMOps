# 01_Discover

NexaAssist / LLMOps engineering workshop Session 1 of 5 · 3 hours · source-aligned workshop Introduce the running project: a synthetic banking-policy assistant. By the end, each pair will have a use-case manifest, a data access decision and measurable proposed targets. This revised deck follows the course lesson sequence; exact lesson URLs appear in section notes and the coverage map.

---

# 02_Today’s measurable outcomes

Trace one question across the application layers. Verify that trusted documents match the register. Propose a gate and explain who approves it. Ask learners to explain what each deliverable would change in a release decision. A running API alone does not demonstrate a correct answer.

---

# 03_Three hours with time to build

25 min concepts + 20 min code walkthrough 90 min pair labs, including a 10 min break 25 min gate review + 20 min recap Pairs alternate driver and reviewer roles. Use the handout to capture predictions, observed results and evidence for each gate.

---

# 04_Showcase / can we trust this policy?

Staff need the approved policy explanation. A file changes while its register hash stays fixed. The ingestion boundary must reject that file. Open the synthetic register. Ask learners to predict whether a plausible PDF remains authoritative when its bytes change. Inspect source verification before discussing models.

---

# 05_Run the evidence-integrity demonstration

python -m training.showcase --session 1 Original: 8 documents verified. Tampered copy: hash mismatch; ingestion refused. Allow 12 minutes. Run from the root using the existing environment. The script changes a temporary copy. Retain the document ID and mismatch, then name the release artifact needing review.

Code walkthrough: app/services/ingestion.py
def requests_from_register(register_path: Path, settings: Settings) -> list[IngestRequest]:
    """One IngestRequest per authoritative document in document_register.json.

    Each source file must match the register's sha256 before it can be ingested.
    """
    return [
        IngestRequest(
            source_path=_verify_source(register_path.parent / entry["file"], entry),
            doc_id=entry["doc_id"],
            title=entry["title"],

Input: registered file and expected SHA-256. Failure: mismatch before parsing or embedding. Decision: hold ingestion and review the source. Submit a transcript, source ID and owner decision. Byte identity does not establish permission or semantic correctness.

---

# 06_What Is LLMOps, and Why Does It Exist?

Educative lesson 01 Concept → worked example → NexaAssist application This section follows the lesson What Is LLMOps, and Why Does It Exist?. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/what-is-llmops-and-why-does-it-exist.

---

# 07_LLMOps manages behavior under real constraints

Correctness and safety are part of the product. Latency shapes whether people can use the service. Token consumption determines variable cost. Start with a staff policy assistant that gives fluent but unsupported advice. Ask which operational signal reveals each problem. A fast HTTP response, cheap model or well-written prompt does not establish all three dimensions at once. Source lesson: https://www.educative.io/courses/llmops/what-is-llmops-and-why-does-it-exist.

---

# 08_From a convincing demo to an operated service

A demo tests a few questions in a controlled setting. Production introduces changing data, users and traffic. The remedy is a repeatable evaluation and release loop. Use a new original example: a policy amendment changes a fee while the old corpus remains indexed. The application code is unchanged, yet the answer becomes stale. Grounding, data refresh, traceability and reviewed release evidence belong in the system design. Source lesson: https://www.educative.io/courses/llmops/what-is-llmops-and-why-does-it-exist.

---

# 09_A successful request can still be wrong

HTTP 200 tells us the service returned a response. A valid quote can accompany an unsupported claim. Measure retrieval and meaning alongside availability. Use a policy fee example: the text can be grammatical and contain a real quote while applying the wrong effective date. Ask which test would detect each failure. Source lesson: https://www.educative.io/courses/llmops/what-is-llmops-and-why-does-it-exist.

---

# 10_How We Reached LLMOps

Educative lesson 02 Concept → worked example → NexaAssist application This section follows the lesson How We Reached LLMOps. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/how-we-reached-llmops.

---

# 11_AI, ML, GenAI and LLMs describe different scopes

AI: Goal-directed systems ML: Learns patterns from data GenAI: Creates new artifacts LLMs: Language-generating models Read these as a conceptual subset chain, not a deployment pipeline. AI also includes approaches that do not learn. LLMs are one kind of generative model, while RAG is an application pattern around a model. Source lesson: https://www.educative.io/courses/llmops/how-we-reached-llmops.

---

# 12_The operational burden moved toward integration

Research focused on building and training models. Interactive interfaces broadened access to generation. Applications now coordinate data, APIs and model behavior. The source illustrates a research period, a major interface shift in 2022, and a subsequent integration era. These are historical teaching phases, not a claim that training disappeared. In an API-backed app the team owns orchestration and data even when it does not own weights. Source lesson: https://www.educative.io/courses/llmops/how-we-reached-llmops.

---

# 13_The artifact gap and the closed-box problem

Prompts, embeddings and knowledge can change separately. Remote model internals are usually outside our control. Debug using observed inputs, evidence, outputs and versions. Do not claim that all classical models are explainable or that replay is impossible. The practical limitation is that hosted generation can vary and model internals are unavailable. Capture the surrounding artifacts so regressions can be localized empirically. Source lesson: https://www.educative.io/courses/llmops/how-we-reached-llmops.

---

# 14_MLOps to LLMOps: What Changes and What Stays

Educative lesson 03 Concept → worked example → NexaAssist application This section follows the lesson MLOps to LLMOps: What Changes and What Stays. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/mlops-to-llmops-what-changes-and-what-stays.

---

# 15_Keep the software-engineering foundation

Version control and CI still coordinate changes. Containers and reproducible dependencies still matter. Infrastructure configuration still needs review and rollback. LLMOps extends existing engineering practice. Unit tests remain useful for deterministic logic; semantic evaluations add a different form of evidence. The current project has a lock file, Docker packaging and tests; CI and infrastructure-as-code are separate gaps. Source lesson: https://www.educative.io/courses/llmops/mlops-to-llmops-what-changes-and-what-stays.

---

# 16_What changes from MLOps to LLMOps

Data: Features → documents + vectors Tuning: Parameters → prompts + retrieval Artifacts: Weights → coupled runtime assets Evaluation: Labels → semantic criteria These are parallel comparison dimensions, not an ordered pipeline. Traditional ML still uses data and LLM systems can still be fine-tuned. This view highlights the primary levers in an API-backed RAG application. Source lesson: https://www.educative.io/courses/llmops/mlops-to-llmops-what-changes-and-what-stays.

---

# 17_Semantic drift needs meaning-aware evidence

Different words can express the same request. Similar words can refer to different domains. Replay representative cases and review emerging topics. Use banking versus river-bank questions as a conceptual ambiguity example. Distribution statistics alone do not establish equivalent meaning. NexaAssist currently compares golden-run scores and collects feedback; it does not implement a topic-drift detector. Source lesson: https://www.educative.io/courses/llmops/mlops-to-llmops-what-changes-and-what-stays.

---

# 18_The 4D Framework (Discover, Distill, Deploy, Deliver)

Educative lesson 04 Concept → worked example → NexaAssist application This section follows the lesson The 4D Framework (Discover, Distill, Deploy, Deliver). Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/the-4d-framework-discover-distill-deploy-deliver.

---

# 19_Four phases, four decisions

Discover: Problem + permitted data Distill: Prove retrieval and generation Deploy: Validate the serving envelope Deliver: Observe and improve The stages form a recurring lifecycle; the drawing shows one pass. Reviewed failures feed the next discovery and experimentation cycle. A phase gate needs a named artifact and an explicit decision. Source lesson: https://www.educative.io/courses/llmops/the-4d-framework-discover-distill-deploy-deliver.

---

# 20_Discover produces an operating contract

Define who asks what and which outcomes are excluded. Identify sources, freshness, permissions and disclosure. Name proposed quality, latency and cost criteria. The data-governance decision can stop development even when a model demo works. Document who owns approval rather than inventing risk ratings or assuming an internal document may be sent to a provider. Source lesson: https://www.educative.io/courses/llmops/the-4d-framework-discover-distill-deploy-deliver.

---

# 21_Distill produces evidence, not a favorite prompt

Tune chunking, retrieval, prompt and model together. Use reviewed cases and capture per-case failures. Separate a missing source from unsupported generation. The source places golden evaluation before deployment. In this workshop the deterministic labs run without network access; optional pre-release evaluation may call real providers. Neither a single good answer nor a valid schema is sufficient. Source lesson: https://www.educative.io/courses/llmops/the-4d-framework-discover-distill-deploy-deliver.

---

# 22_Deploy and Deliver require different evidence

Deploy: representative traffic within approved budgets. Deliver: quality signals, reviewed failures and recovery. Missing measurements remain unknown, not successful. The course includes example quality and SLO numbers. They are not universal targets. In this repository gates.json explicitly labels its values as placeholders; the business and operational owners must confirm them. Source lesson: https://www.educative.io/courses/llmops/the-4d-framework-discover-distill-deploy-deliver.

---

# 23_Proposed targets need a rationale

Quality: source-grounded answers and correct status. Operations: latency, error rate and priced cost. Safety: a measured rollback signal and named owner. Do not turn the shipped numbers into an organizational promise. Ask what user impact and traffic evidence would justify each proposed threshold. Source lesson: https://www.educative.io/courses/llmops/the-4d-framework-discover-distill-deploy-deliver. The implementation or concept reference is app/evaluation/gates.json.

---

# 24_Architecture of a Retrieval-Augmented Generation Application

Educative lesson 05 Concept → worked example → NexaAssist application This section follows the lesson Architecture of a Retrieval-Augmented Generation Application. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

---

# 25_RAG separates knowledge preparation from answering

Sources: Registered policy documents Ingestion: Parse, redact, embed, upsert Knowledge: Vectors + parent sections Inference: Retrieve, prompt, generate Ingestion optimizes throughput, repeatability and data integrity. Online inference optimizes request latency and answer quality. Traceability links an answer back through the exact source version. The full interactive reference architecture is supplied alongside the deck. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

---

# 26_Freshness, permission and traceability are separate

A fresh document can still be unauthorized. A permitted document can still be obsolete. An answer needs a recoverable source identity. Data divergence is the gap between expected knowledge and what the index contains. In NexaAssist, effective-date and metadata filters constrain retrieval and provenance preserves source references. Corpus freshness approvals are still owner decisions. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

---

# 27_Repeated ingestion needs three guarantees

Stable identities prevent duplicate accumulation. Compatible versions prevent mixed embedding spaces. Failure isolation preserves progress and exposes bad files. The project has deterministic checksums and per-document failure isolation. The source discusses immutable candidate indexes and dead-letter handling; automatic blue/green promotion and a durable dead-letter queue are not implemented here. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

---

# 28_Budget the online path before adding hops

Scenario: 2,000 ms total minus 1,500 ms generation. That leaves 500 ms for queueing, retrieval and overhead. Parallelism, caching and model choice require measurement. The numbers are scenario data, not a measured NexaAssist SLO. Retrieval caching must include permissions, corpus version and freshness. A cache hit is not inherently free or safe, and no semantic cache is added by these slides. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

---

# 29_Use the existing layer boundaries

chains/ owns pure LangChain runnables. database/ owns MongoDB client and retrieval setup. services/ coordinates; api/ validates; ui/ renders. Open CLAUDE.md and trace app/api/answer.py through app/services/answer.py into app/chains/answer.py. No model logic belongs in the UI. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

---

# 30_A thin route delegates to the service

Dependency injection supplies settings; the service owns the workflow. Open app/api/answer.py and locate @router.post("/answer"). Read the displayed excerpt in context; it is taken directly from the application. Dependency injection supplies settings; the service owns the workflow. Source lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application. The implementation or concept reference is app/api/answer.py.

---

# 31_Scoping and Planning a Production RAG Application

Educative lesson 06 Concept → worked example → NexaAssist application This section follows the lesson Scoping and Planning a Production RAG Application. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

---

# 32_The source course builds an internal support assistant

Staff search internal policies and tool instructions. The response must be grounded and cite its documentation. A use-case manifest keeps later scope changes reviewable. The source uses a fictional Halluli support project with HR and internal-tool documents. NexaAssist applies the same operating principles to synthetic banking policy. Do not mix the two corpora or pretend their contracts are identical. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

---

# 33_Translate the stack without losing the lesson

Course: FastAPI, PostgreSQL/pgvector, LiteLLM, Docker. NexaAssist: FastAPI, MongoDB Atlas, LangChain, Docker. Preserve responsibilities, validation and evaluation gates. The database and model interface are explicit adaptations required by CLAUDE.md. The course uses a single database for converged operational data. NexaAssist uses Atlas collections for vectors, parents and feedback. No PostgreSQL migration or extra framework is introduced. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

---

# 34_The use-case contract is intentionally narrow

Explain synthetic policy clauses for staff. Ask for missing scope or abstain when unsupported. Never approve credit or execute account actions. Ask learners to write two allowed questions and two disallowed actions. Domain authority and organizational approvals remain decisions for the real data owner. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application. The implementation or concept reference is training/use_case_manifest.md.

---

# 35_A trusted source needs an identity

Register: doc_id, version, effective dates and hash. Authority and amendment relationships affect retrieval. A changed file must fail source verification. A hash checks integrity against the register; it does not establish legal permission, correctness or authority by itself. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application. The implementation or concept reference is nexa_synthetic_data/document_register.json.

---

# 36_Data permission is a release dependency

Identify who owns and may access the source. Decide whether content may leave for embeddings or generation. Set freshness and retention before using real documents. These are workshop decisions to document, not claims that synthetic data grants permission to process real customer records. Use the manifest as the review artifact. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

---

# 37_Map the interface boundary honestly

Course examples describe /ingest and /chat. NexaAssist uses an ingestion CLI and /answer routes. Operational traces and feedback retain answer context. Endpoint names are not the architectural principle. Administrative ingestion stays outside public user serving, and the exact NexaAssist paths come from the API modules. The source lesson itself varies between HR and technical-support examples; our manifest consistently uses policy lookup. Source lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

---

# 38_Practical 2 / tamper with a safe copy

Run: python -m training.session1.tamper Predict which document hash will fail. Expected: 8 originals verify; changed PDF is refused. Prefix Python with uv run --no-sync. The lab works in a temporary directory and protects the original corpus. Explain why failure occurs before embeddings are created. The implementation or concept reference is training/session1/tamper.py.

---

# 39_Practical 3 / inspect the gate contract

Run: python -m training.session1.check_gates app/evaluation/gates.json Change a copied faithfulness minimum to 1.5. Expected: validation rejects a value outside [0, 1]. Use a copy in /tmp and rerun check_gates with that path. A syntactically valid threshold still needs business approval and a measured baseline.

---

# 40_Thresholds are typed data

Status distinguishes placeholder numbers from owner-confirmed targets. Open app/evaluation/gates.py and locate class Gates. Read the displayed excerpt in context; it is taken directly from the application. Status distinguishes placeholder numbers from owner-confirmed targets. The implementation or concept reference is app/evaluation/gates.py.

---

# 41_Exit gate / are we ready to experiment?

Hand in the manifest and data-access decision. Name source owner, restrictions and must-abstain cases. Keep unresolved approvals visible in the release file. Pass the class exercise when the scope and unresolved decisions are explicit. A production data-governance gate remains blocked until the real owners approve.

---

# 42_Check your understanding

Does a SHA-256 match prove that a policy is correct? Can a healthy API answer from the wrong clause? Which artifacts must be restored together? Answers: a hash proves correspondence to the registered bytes, not correctness; yes, liveness does not judge meaning; restore compatible code, prompts, models, knowledge stores and configuration.

---

# 43_Next / prove retrieval before generation

Read app/chains/chunking.py. Bring a table question and an effective-date trap. Carry the manifest into Session 2. The next class measures the evidence path without asking an answer model to hide retrieval faults. Required exercises stay offline; optional Atlas work is separately marked.
