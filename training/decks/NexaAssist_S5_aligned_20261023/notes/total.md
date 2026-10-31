# 01_Deliver

Observability, human review and rollback Session 5 of 5 · 3 hours · source-aligned workshop The final session uses synthetic incidents and actual checkers. Learners must distinguish an exercise decision from a production deployment action. This revised deck follows the course lesson sequence; exact lesson URLs appear in section notes and the coverage map.

---

# 02_What the final release file must explain

What changed and which artifacts produced the answer. Which measured gates passed, failed or remain unknown. Who can approve release and who can restore service. A release file is evidence for a decision, not a decorative checklist. Any missing identifier or unmeasured target stays visible.

---

# 03_The last three-hour workshop

25 min operating loop + 20 min trace walkthrough 90 min labs, including a 10 min break 25 min incident review + 20 min final debrief The practicals cover incident metrics, reviewed feedback and a rollback tabletop. Keep time for each pair to defend its release hold or approval recommendation.

---

# 04_Showcase / a complaint becomes a test

A staff member flags an unhelpful answer. A reviewer checks sources and accepts the signal. A separate curated answer becomes a golden case. Acceptance does not authenticate the client response or certify the correction. Export requires the same input, explicit expected status/output and source references for an answered target. Detected PII is blocked.

---

# 05_Run the reviewed-feedback demonstration

python -m training.showcase --session 5 No token: 401; pending: 409; curated export: 200. Validate JSONL, keep the review, rehearse recovery. Allow 25 minutes. Actual API/services and institution-scoped database logic run with a Mongo fake. Validate the exported case via load_golden, inspect the audit bundle, then run the incident check. Nothing is deployed.

Code walkthrough: app/services/feedback.py
    record = await asyncio.to_thread(database.get_feedback, feedback_id, settings)
    if record is None:
        raise LookupError("Feedback not found")
    if record.status != "accepted" or not record.reviewer or not record.review_note.strip():
        raise ValueError("Accepted feedback with a reviewer and review note is required")
    if case.input != record.request:
        raise ValueError("Golden input must match the reviewed feedback request")
    if case.expected_status == "answered" and not case.context:
        raise ValueError("An answered golden case requires source references")
    if redact(case.model_dump_json())[1]:

Signal → reviewed case → failing replay → fix. Keep the case and audit bundle under review. Release after quality and operational checks agree. The workflow does not automate dataset promotion, training or deployment. An SME verifies policy meaning. Blue/green, memory and existing category mapping decisions remain outside this change.

---

# 06_Orchestration and Application Logic

Educative lesson 14 Concept → worked example → NexaAssist application This section follows the lesson Orchestration and Application Logic. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/orchestration-and-application-logic.

---

# 07_Follow-up questions change retrieval requirements

A query such as “Does that fee apply earlier?” lacks scope alone. Conversation history can resolve the subject and date. Memory adds privacy, latency and correctness obligations. NexaAssist currently asks a standalone policy question per request. Teach the source’s orchestration design without claiming that persistence, rewriting or session authentication exists in production. Source lesson: https://www.educative.io/courses/llmops/orchestration-and-application-logic.

---

# 08_Keep API workers stateless; store conversation state

Request: Session + user scope Load history: Authorized durable turns Rewrite: Standalone search query Retrieve / answer: Generate, validate, persist This is the course reference design, not an implemented NexaAssist workflow. A real implementation must authorize session access and isolate users. A worker-local list loses context across replicas and restarts. Source lesson: https://www.educative.io/courses/llmops/orchestration-and-application-logic.

---

# 09_A sliding window is a budget approximation

Load a bounded recent history instead of all turns. Message count is simple but ignores varying token length. Reserve tokens for instructions, evidence and output. The source illustrates six recent messages. That is a heuristic, not a recommended universal setting. Production history requires deterministic ordering, retention, deletion and a token-aware budget appropriate to the selected model. Source lesson: https://www.educative.io/courses/llmops/orchestration-and-application-logic.

---

# 10_Rewriting must preserve the user’s meaning

Resolve references using only authorized recent history. Keep original question and rewritten search query separate. Validate output; time out or fall back when rewriting fails. A cheap rewriter is another model call and failure surface. It can change a fee date or invent a product. A fallback to the original question preserves availability but may retrieve poorly; asking for clarification can be safer depending on the contract. Source lesson: https://www.educative.io/courses/llmops/orchestration-and-application-logic.

---

# 11_New state needs multi-turn evaluation

Capture history, current input and expected source. Test incorrect rewrites, missing history and cross-user access. Recheck retrieval and answer quality before rollout. The source expands its single-turn golden set when adding memory. Existing single-turn success does not demonstrate conversational quality. Use explicit reference identities rather than evaluating fluency alone. Source lesson: https://www.educative.io/courses/llmops/orchestration-and-application-logic.

---

# 12_Practical / model the memory contract offline

Run: python -m training.session5.memory_design Inspect a bounded fixture and a failed-rewrite fallback. Explain why the simulation is not a durable session service. This educational simulation uses no LLM or database and does not add conversation memory to the API. Learners submit an implementation plan naming storage, authorization, token budgeting and multi-turn tests. Source lesson: https://www.educative.io/courses/llmops/orchestration-and-application-logic.

---

# 13_Quality, Human-in-the-Loop, and Governance Systems

Educative lesson 15 Concept → worked example → NexaAssist application This section follows the lesson Quality, Human-in-the-Loop, and Governance Systems. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 14_Use two kinds of observation

System health: latency, failures, tokens and priced cost. Answer quality: grounding, relevance and correct scope. A healthy system can still produce a harmful answer. APM spans diagnose infrastructure; semantic evaluation and human review diagnose meaning. Neither substitutes for the other. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 15_Trace one answer to its artifacts

Prompt ID, version and content fingerprint. Chat/embedding model and retrieval configuration. Evidence references and optional Datadog span ID. The response carries provenance, and feedback preserves the submitted response. Client-supplied provenance is useful context but is not tamper-proof attestation. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems. The implementation or concept reference is app/models/answer.py.

---

# 16_Sampled judging is an explicit choice

The sample rate is configurable; zero disables sampled judging. Open app/services/evaluation.py and locate def should_sample. Read the displayed excerpt in context; it is taken directly from the application. The sample rate is configurable; zero disables sampled judging. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems. The implementation or concept reference is app/services/evaluation.py.

---

# 17_Know what sampled faithfulness measures

Sampling answered requests adds model cost. The current judge uses cited quotes as its context. This is a grounding proxy with limited observation. A low sample count can miss failures. A quoted passage may omit other retrieved context, so do not call the proxy an exhaustive hallucination detector. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems. The implementation or concept reference is app/services/evaluation.py.

---

# 18_Quality is maintained in three layers

Automated gates catch known regressions. Human review assesses context and newly observed failures. Governance controls changes to meaning and risk. The layers complement each other. LLM-based evaluations can vary even in an offline run; do not call them deterministic simply because the dataset is fixed. Preserve judge versions and compare a sample to reviewed human assessments. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 19_The review queue needs the exact interaction

Link the input, evidence references, output and versions. Prioritize explicit complaints and representative samples. Review the source before accepting the correction. The stored response is client supplied and does not prove server execution. The authenticated export reads the accepted institution-scoped review and requires a separately curated GoldenAnswer. It returns an audit bundle without changing the shipped dataset or establishing semantic truth. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 20_Human feedback is a signal

A thumbs-down may mean wrong scope or poor wording. Review source, context and answer before accepting it. Never turn raw feedback directly into a golden answer. The feedback queue has pending, accepted and rejected states. Reviewer authentication and idempotent submission support workflow, while domain verification supplies truth. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems. The implementation or concept reference is app/models/feedback.py; app/services/feedback.py.

---

# 21_The human review loop has owners

Signal → triage → source-supported correction Review → proposed golden case → regression replay Approved fix → measured release → observation This is our workshop interpretation of the course feedback loop. Each transition needs evidence and an owner, especially where policy meaning changes. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 22_Practical 2 / inspect feedback behavior

Run feedback, sampling and comparison tests. Follow reviewer authentication and review transitions. Explain why accepted feedback still needs a verified reference. The existing API stores client-submitted response data. The class should not treat a submitted provenance object as a trusted replay of server execution. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems. The implementation or concept reference is training/session5/handout.md.

---

# 23_Export a reviewed regression case

Run: python -m training.session5.feedback_loop Accepted review + curated answer → golden case. Keep the review bundle beside the validated JSONL. POST /feedback/{feedback_id}/golden requires reviewer authentication, an accepted server-side review and a separate GoldenAnswer for the same input. Submitted answers/corrections are never copied automatically. The API returns the case and audit data without editing datasets. The SME verifies source accuracy; existing category mappings remain unchanged. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 24_Governance follows the change’s meaning

Engineering reviews code and operational behavior. A domain expert reviews policy meaning and golden answers. The designated owner approves real data use and risk. These are proposed workshop responsibilities. Record actual names and approval dates for a real release instead of inventing an organization-specific approval matrix. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 25_Watch both semantic and operational drift

Topic shifts can expose gaps in the golden set. Policy updates can invalidate otherwise stable answers. Judge changes can move scores without application changes. NexaAssist has comparison functions and sampled judging, not a complete semantic drift detector. Treat changing scores as evidence to investigate, aligning datasets and judge configuration before assigning cause. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 26_Practical 1 / run an incident safely

Run: python -m training.session5.incident No traffic → every required SLO is not_measured. Scenario failures: p95 latency and hallucination proxy. The scenario sets p95 to 2500 ms and the proxy to 0.15 under the shipped placeholder gates. Nothing is deployed and no database is changed. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 27_A regression needs a comparable baseline

Scenario faithfulness changes from 0.95 to 0.70. Delta −0.25 exceeds the placeholder tolerance. Investigate cases and configuration before interpreting it. These are scenario scores. Comparison now requires matching dataset fingerprints, unique case IDs, judge model/version and Ragas version, with identical finite metric sets. Regenerate legacy reports. Per-case flips can block a release even when averages hide them. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems. The implementation or concept reference is app/evaluation/compare.py.

---

# 28_Exercise / remove an observation

Set sampled_count=0 and the proxy to None. Predict not_measured rather than pass. Explain what evidence is needed before clearing an incident. Learners should preserve the incident until relevant observations support recovery. Operational latency recovery alone does not prove restored semantic quality. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 29_Practical 3 / rehearse rollback

Hold candidate → preserve evidence → restore known-good set Replay failing and golden cases → measure representative traffic Document owner decision and follow-up regression case This is a tabletop, not a deployment script. Restore compatible code, prompts, models and retrieval stores; rehearse the exact operational switch before any real release. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems.

---

# 30_A new index name is not a data snapshot

Ingestion mutates the configured chunk collection. Parent sections must also match the candidate corpus. Blue/green requires isolated compatible stores and a tested switch. Do not imply that changing VECTOR_INDEX_NAME alone performs safe rollback. Separate parent data matters because generation uses those sections after retrieval. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems. The implementation or concept reference is app/database/mongo.py; app/chains/ingestion.py.

---

# 31_What belongs in the release file

Prompt/model/retrieval identities and dataset hash. Offline quality report and representative SLO evidence. Approver, rollback owner, known limits and incident links. This workspace copy has no Git metadata. Do not invent a commit or release tag; use actual identifiers from the environment where the release is built. Source lesson: https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems. The implementation or concept reference is training/session5/handout.md.

---

# 32_Future Directions in LLMOps

Educative lesson 16 Concept → worked example → NexaAssist application This section follows the lesson Future Directions in LLMOps. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/future-directions-in-llmops.

---

# 33_Agents add actions and new failure modes

Tool access needs permissions and an allowlist. Loops need iteration, time and cost bounds. Side effects need isolation, audit and recovery. Agents are future scope here. The existing read-only RAG assistant does not become an agent merely because the course discusses tool loops. Source lesson: https://www.educative.io/courses/llmops/future-directions-in-llmops. The implementation or concept reference is Educative: Future Directions in LLMOps.

---

# 34_Bound an agent before granting actions

Limit steps, time, token spend and tool permissions. Isolate side effects and preserve an audit trail. Evaluate tool choice, arguments and recovery behavior. A read-only assistant becomes materially different when it can modify a record. The source names iteration caps, allowlists and sandboxed execution. These are design requirements for a future layer, not controls implemented by the current chain. Source lesson: https://www.educative.io/courses/llmops/future-directions-in-llmops.

---

# 35_Multimodal inputs expand the ingestion boundary

OCR or vision extraction introduces interpretation errors. Images and audio can carry identifiers or instructions. Queue expensive processing and evaluate the extracted evidence. A text-first index can simplify downstream retrieval but still needs modality-specific validation and privacy review. Adding image input is not merely changing an embedding model. Source lesson: https://www.educative.io/courses/llmops/future-directions-in-llmops.

---

# 36_Model distillation introduces a training lifecycle

Curate teacher traces into reviewed training data. Evaluate a smaller student on quality and safety cases. Version the dataset, model and rollback decision. The 4D phase named Distill is broader than knowledge distillation. Keep those two meanings distinct. A smaller model can reduce resource use, but improvement must be measured for the task. Source lesson: https://www.educative.io/courses/llmops/future-directions-in-llmops.

---

# 37_Edge execution shifts the operational trade-off

Local inference can reduce network disclosure and round trips. Device differences affect performance and version consistency. Telemetry, updates and recovery need a new design. Avoid the source’s absolute “near-zero latency” phrasing. On-device models can be slow or constrained, and local processing does not guarantee that every feature avoids external calls. Source lesson: https://www.educative.io/courses/llmops/future-directions-in-llmops.

---

# 38_The lifecycle survives a change in capabilities

Define the new permission and data boundaries. Evaluate before deployment and version the artifacts. Observe failures and close the reviewed feedback loop. Agents, multimodality, distillation and edge execution introduce different engineering work. The operating principles continue to apply; capability should follow a concrete use case and a measurable acceptance plan. Source lesson: https://www.educative.io/courses/llmops/future-directions-in-llmops.

---

# 39_Final gate / defend the decision

Submit manifest, retrieval experiment and golden review. Attach quality/SLO reports and an incident write-up. State release, hold or unmeasured with supporting evidence. A successful class demonstrates engineering judgment and reproducible exercises. It does not certify a real production environment that has not been tested.

---

# 40_Operate the loop, not just the endpoint

Version the artifacts that change answers. Measure evidence, meaning and operations separately. Turn reviewed failures into durable regression cases. Close by asking each pair what they would investigate first after an incorrect fee answer. Point learners to the source course and local handouts for continued practice.
