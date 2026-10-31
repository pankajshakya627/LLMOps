# 01_Discover

NexaAssist / LLMOps engineering workshop Session 1 of 5 · 3 hours · Python + REST prerequisite Introduce the running project: a synthetic banking-policy assistant. By the end, each pair will have a use-case manifest, a data access decision and measurable proposed targets.

---

# 02_Five sessions. One release file.

Discover → scope and data contract Distill → retrieval, prompts and evaluation Deploy + Deliver → secure service and operations This five-session grouping is our teaching design. It adapts the course lifecycle to the existing LangChain, MongoDB Atlas, FastAPI and Streamlit layers.

---

# 03_Today’s measurable outcomes

Trace one question across the application layers. Verify that trusted documents match the register. Propose a gate and explain who approves it. Ask learners to explain what each deliverable would change in a release decision. A running API alone does not demonstrate a correct answer.

---

# 04_Three hours with time to build

25 min concepts + 20 min code walkthrough 90 min pair labs, including a 10 min break 25 min gate review + 20 min recap Pairs alternate driver and reviewer roles. Use the handout to capture predictions, observed results and evidence for each gate.

---

# 05_A successful request can still be wrong

HTTP 200 tells us the service returned a response. A valid quote can accompany an unsupported claim. Measure retrieval and meaning alongside availability. Use a policy fee example: the text can be grammatical and contain a real quote while applying the wrong effective date. Ask which test would detect each failure.

---

# 06_The deployable unit has several artifacts

Code + dependency lock + container Prompt ID/version/hash + model configuration Corpus register + embedding schema + golden dataset A prompt or policy update can change answers without a code change. The release file needs enough identity to reproduce and restore behavior.

---

# 07_The 4D loop has explicit gates

Discover → permitted data and defined problem Distill → measured evidence and answer quality Deploy → measured SLOs; Deliver → rollback decisions Paraphrase the lifecycle as a sequence of engineering decisions. Our local gate numbers are teaching placeholders rather than approved production targets. The implementation or concept reference is Educative: 4D framework.

---

# 08_Keep ingestion outside the request path

Register → parse → chunk → redact → Atlas Question → scoped retrieval → context → generation Answer → validation → API → staff interface The offline path maintains knowledge assets; the online path consumes them. Explain why a document parsing failure should not become request-time work. The implementation or concept reference is app/chains/ingestion.py; app/chains/answer.py.

---

# 09_Use the existing layer boundaries

chains/ owns pure LangChain runnables. database/ owns MongoDB client and retrieval setup. services/ coordinates; api/ validates; ui/ renders. Open CLAUDE.md and trace app/api/answer.py through app/services/answer.py into app/chains/answer.py. No model logic belongs in the UI.

---

# 10_A thin route delegates to the service

Dependency injection supplies settings; the service owns the workflow. Open app/api/answer.py and locate @router.post("/answer"). Read the displayed excerpt in context; it is taken directly from the application. Dependency injection supplies settings; the service owns the workflow. The implementation or concept reference is app/api/answer.py.

---

# 11_The use-case contract is intentionally narrow

Explain synthetic policy clauses for staff. Ask for missing scope or abstain when unsupported. Never approve credit or execute account actions. Ask learners to write two allowed questions and two disallowed actions. Domain authority and organizational approvals remain decisions for the real data owner. The implementation or concept reference is training/use_case_manifest.md.

---

# 12_A trusted source needs an identity

Register: doc_id, version, effective dates and hash. Authority and amendment relationships affect retrieval. A changed file must fail source verification. A hash checks integrity against the register; it does not establish legal permission, correctness or authority by itself. The implementation or concept reference is nexa_synthetic_data/document_register.json.

---

# 13_Practical 1 / inspect the baseline

Run: uv run --no-sync pytest -q tests Locate the missing architecture-document failure. Record it separately; do not delete or skip the test. The handoff reports one missing documentation artifact. Use the actual result in this copy rather than memorizing a historical test count. Keep the failure visible.

---

# 14_Practical 2 / tamper with a safe copy

Run: python -m training.session1.tamper Predict which document hash will fail. Expected: 8 originals verify; changed PDF is refused. Prefix Python with uv run --no-sync. The lab works in a temporary directory and protects the original corpus. Explain why failure occurs before embeddings are created. The implementation or concept reference is training/session1/tamper.py.

---

# 15_Practical 3 / inspect the gate contract

Run: python -m training.session1.check_gates app/evaluation/gates.json Change a copied faithfulness minimum to 1.5. Expected: validation rejects a value outside [0, 1]. Use a copy in /tmp and rerun check_gates with that path. A syntactically valid threshold still needs business approval and a measured baseline.

---

# 16_Thresholds are typed data

Status distinguishes placeholder numbers from owner-confirmed targets. Open app/evaluation/gates.py and locate class Gates. Read the displayed excerpt in context; it is taken directly from the application. Status distinguishes placeholder numbers from owner-confirmed targets. The implementation or concept reference is app/evaluation/gates.py.

---

# 17_Data permission is a release dependency

Identify who owns and may access the source. Decide whether content may leave for embeddings or generation. Set freshness and retention before using real documents. These are workshop decisions to document, not claims that synthetic data grants permission to process real customer records. Use the manifest as the review artifact.

---

# 18_Security begins before embeddings

Remove detected identifiers before sending text out. Apply metadata scope to retrieval, including dates. Keep secrets in approved environment configuration. PII detection is pattern based and incomplete. Embeddings and provider disclosure make source hygiene a design responsibility, not an output formatting detail. The implementation or concept reference is app/chains/redaction.py; app/services/retrieval.py.

---

# 19_Proposed targets need a rationale

Quality: source-grounded answers and correct status. Operations: latency, error rate and priced cost. Safety: a measured rollback signal and named owner. Do not turn the shipped numbers into an organizational promise. Ask what user impact and traffic evidence would justify each proposed threshold. The implementation or concept reference is app/evaluation/gates.json.

---

# 20_Exit gate / are we ready to experiment?

Hand in the manifest and data-access decision. Name source owner, restrictions and must-abstain cases. Keep unresolved approvals visible in the release file. Pass the class exercise when the scope and unresolved decisions are explicit. A production data-governance gate remains blocked until the real owners approve.

---

# 21_Check your understanding

Does a SHA-256 match prove that a policy is correct? Can a healthy API answer from the wrong clause? Which artifacts must be restored together? Answers: a hash proves correspondence to the registered bytes, not correctness; yes, liveness does not judge meaning; restore compatible code, prompts, models, knowledge stores and configuration.

---

# 22_Next / prove retrieval before generation

Read app/chains/chunking.py. Bring a table question and an effective-date trap. Carry the manifest into Session 2. The next class measures the evidence path without asking an answer model to hide retrieval faults. Required exercises stay offline; optional Atlas work is separately marked.
