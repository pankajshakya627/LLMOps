# 01_Operate Bedrock safely

This is an 18-slide AWS deployment design based on the repository. It does not claim that Bedrock or Bedrock Guardrails is already configured or running. The current local Compose stack still uses Ollama. NexaBank and its loan policy are synthetic. The application explains policy and does not approve credit. Use the linked AWS deployment guide for detailed migration checks and commands.

---

# 02_Separate the owners

Ask: can Phoenix block an unsafe query? No. Phoenix records execution and annotated outcomes after instrumentation. Bedrock Guardrails and the application enforce policy. LiteLLM gives current OpenAI-compatible clients a route to managed Bedrock inference. Ragas measures selected quality properties. These responsibilities are the target design, not evidence of current AWS deployment.

---

# 03_AWS target architecture

Staff enters the API through authenticated HTTPS. The API applies local input policy and planned Bedrock guardrail checks before embedding. LiteLLM sends embedding and chat requests to Bedrock. RDS pgvector supplies scoped evidence. API and gateway export spans to Phoenix with separate storage. Ragas annotations attach to evaluated API requests. S3 stages corpus documents and batch reports. The diagram shows target placement, not current Compose wiring.

---

# 04_Deploy in dependency order

Create private network access and scoped task roles first. Publish immutable images to ECR. Provision separate application and Phoenix PostgreSQL databases, then select the packaged Bedrock gateway configuration. Stage the S3 corpus in a one-off ingestion task. ECS health does not prove model access, corpus completeness or policy correctness. No infrastructure template or deployed stack is asserted.

---

# 05_Qualify each Bedrock model

Select concrete chat and judge routes only after testing the repository’s strict structured-output calls through its pinned LiteLLM version. A Llama route is conditional on account/Region and schema support. Titan V2 defaults to 1024 dimensions. The current custom embedding client verifies the returned length rather than requesting a dimension. No Bedrock model has passed the application contract here yet.

---

# 06_Rebuild the vector corpus

The pgvector backend stores immutable model, dimension and profile identity for each namespace. Qwen and Titan can both return 1024 numbers but their spaces are different. Set a new EMBEDDING_PROFILE and new chunk/parent namespaces, stage the original versioned documents, and ingest again. Keep old Qwen data for rollback until the Bedrock corpus is qualified. Verify /retrieve before judging generation.

---

# 07_Route through LiteLLM

The fragment is illustrative and is not current runnable gateway YAML. The Bedrock chat and judge routes need qualified model or inference-profile IDs supported in the selected account/Region. Keep LiteLLM master-key authentication and the Phoenix callback. The gateway ECS task role authenticates to Bedrock. Test both chat completions and embeddings through this exact pinned gateway image before cutover.

---

# 08_Switch one API profile

This is a partial target setting example, not a complete ECS task definition. The custom gateway still requires explicit CHAT_API_KEY, EMBEDDING_API_KEY and evaluator endpoint keys from its master-key secret. The gateway itself uses an IAM task role. Set institution, jurisdiction and scoped PostgreSQL DSN; clear unsupported Qwen reasoning options and disable the Ollama reranker. Changing only .env cannot switch the current Compose gateway from Ollama to Bedrock.

---

# 09_Enforce at each boundary

Current answer, evaluated-answer and batch paths call scrub_request before downstream model work. A future ApplyGuardrail INPUT call must finish before embedding. Query-only inspection cannot detect malicious instructions added by retrieved documents; inspect the assembled prompt or use a compatible invocation guardrail. Check OUTPUT even on a cached completion. Keep Pydantic, exact citations, output PII and abstention. Fail closed on a guardrail outage. Current Bedrock guardrail calls and their dedicated traces are not implemented.

---

# 10_Two synthetic safety drills

Use synthetic identifiers only. The local scrubber redacts supported email and PAN patterns and logs counts. The planned Bedrock guardrail should add a separate decision; it is not yet in the app. Do not assume Bedrock built-in PII types cover PAN/Aadhaar—test the configured policy. The current injection rule detects specific normalized English overrides, not every attack. Keep raw Phoenix content capture off for private data because ingress spans may see pre-redaction text.

---

# 11_Ask one policy question

After the Bedrock services and Titan corpus are deployed, send this JSON to /answer. The synthetic maximum NexaHome loan amount is ₹7,50,00,000 under POL-HL-V3 clause 4.1. Require answered status with exact cited evidence. An HTTP 200 insufficient_evidence is a safe abstention, not a pass for this known case. The response gives model aliases and a Phoenix trace/span ID; inspect gateway provider attributes for the actual route. No live Bedrock answer is claimed.

---

# 12_Read Phoenix correctly

Find the returned phoenix_span_id in the API Phoenix project. API Output is captured only when synthetic content capture is explicitly enabled; the private default masks it. Gateway spans may show the real Bedrock route when its callback emits provider metadata. Guardrail decisions need new safe attributes/spans. /answer/evaluated schedules Ragas annotation publication after the answer. Batch reports do not automatically produce matching API annotations. Correlate by IDs rather than timestamp alone.

---

# 13_Score the exact answer

Use /answer/evaluated with an explicit reference answer for context metrics. This makes a fresh generation and scores that answer, not a previous /answer response. Fix judge and metric embedding routes for a fair comparison. Ragas metrics can be scored, unavailable or error. Abstention makes faithfulness and relevancy unavailable; context metrics need reference facts. Scoring adds Bedrock calls and latency. Phoenix receives annotations only if publication succeeds.

---

# 14_Diagnose no evidence

A branch employee gets insufficient_evidence for a known policy. Start with /retrieve using the same product and date. Empty hits point to corpus, embedding or scope. With evidence, inspect generation_ms, strict JSON failures, evidence_refs and exact quote validation. A citation failure gets one repair attempt then abstention. A missing Ragas value may be legitimately unavailable or an evaluator error. A missing Phoenix span can mean exporter failure even if the model ran. Do not relax filters or gates merely for a demo.

---

# 15_Handle a Bedrock incident

In a real incident, inspect Bedrock access, quotas and gateway error spans. A throttled model is not the same as a guardrail block. If a fallback is permitted, prove which route answered and still validate its output. A guardrail block should return a safe decision, record its policy version and avoid raw PII in traces. Bad JSON or uncited content is a generation-quality failure with safe abstention. No fallback is automatic in the proposed Bedrock-only profile until configured and measured.

---

# 16_Release on measured evidence

Before cutover, test strict answer/judge schemas through pinned LiteLLM, Titan vector length, PII and injection cases, guardrail block/outage behavior, Ragas metrics, Phoenix spans and representative latency/cost. Keep image, gateway YAML, prompt SHA and corpus namespace as one rollback unit. Repository quality gates are placeholders until owners set measured thresholds. ECS service health and /ready do not establish answer quality. No AWS test is claimed by this slide.

---

# 17_Open the owning code

Start at the API entry, then the shared input policy. The current gateway YAML still points to Ollama; the proposed new Bedrock YAML has no code anchor yet. The PostgreSQL profile refuses a mismatched corpus. The answer chain asks for strict AnswerDraft and enforces exact citations. Phoenix export attaches Ragas annotations to the request span. Bedrock ApplyGuardrail integration has no current code anchor. These one-based line numbers are a 27 October 2026 snapshot; function names are the durable map.

---

# 18_Prove each boundary

Ask three exit questions: What blocks an unsafe request? Bedrock Guardrails plus application checks, not Phoenix. What changes with Titan embeddings? New profile, namespaces and full re-ingestion. What proves Bedrock answered? Gateway provider evidence plus validated API result, not an alias label. Open app/operations/AWS_DEPLOYMENT.md for the full deployment sequence and code map. This deck is a proposed AWS plan; current local Compose remains on Ollama.
