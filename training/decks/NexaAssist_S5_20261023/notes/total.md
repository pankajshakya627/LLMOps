# 01_Deliver

Observability, human review and rollback Session 5 of 5 · 3 hours · complete the release file The final session uses synthetic incidents and actual checkers. Learners must distinguish an exercise decision from a production deployment action.

---

# 02_What the final release file must explain

What changed and which artifacts produced the answer. Which measured gates passed, failed or remain unknown. Who can approve release and who can restore service. A release file is evidence for a decision, not a decorative checklist. Any missing identifier or unmeasured target stays visible.

---

# 03_The last three-hour workshop

25 min operating loop + 20 min trace walkthrough 90 min labs, including a 10 min break 25 min incident review + 20 min final debrief The practicals cover incident metrics, reviewed feedback and a rollback tabletop. Keep time for each pair to defend its release hold or approval recommendation.

---

# 04_Use two kinds of observation

System health: latency, failures, tokens and priced cost. Answer quality: grounding, relevance and correct scope. A healthy system can still produce a harmful answer. APM spans diagnose infrastructure; semantic evaluation and human review diagnose meaning. Neither substitutes for the other.

---

# 05_Trace one answer to its artifacts

Prompt ID, version and content fingerprint. Chat/embedding model and retrieval configuration. Evidence references and optional Datadog span ID. The response carries provenance, and feedback preserves the submitted response. Client-supplied provenance is useful context but is not tamper-proof attestation. The implementation or concept reference is app/models/answer.py.

---

# 06_Sampled judging is an explicit choice

The sample rate is configurable; zero disables sampled judging. Open app/services/evaluation.py and locate def should_sample. Read the displayed excerpt in context; it is taken directly from the application. The sample rate is configurable; zero disables sampled judging. The implementation or concept reference is app/services/evaluation.py.

---

# 07_Know what sampled faithfulness measures

Sampling answered requests adds model cost. The current judge uses cited quotes as its context. This is a grounding proxy with limited observation. A low sample count can miss failures. A quoted passage may omit other retrieved context, so do not call the proxy an exhaustive hallucination detector. The implementation or concept reference is app/services/evaluation.py.

---

# 08_Practical 1 / run an incident safely

Run: python -m training.session5.incident No traffic → every required SLO is not_measured. Scenario failures: p95 latency and hallucination proxy. The scenario sets p95 to 2500 ms and the proxy to 0.15 under the shipped placeholder gates. Nothing is deployed and no database is changed.

---

# 09_A regression needs a comparable baseline

Scenario faithfulness changes from 0.95 to 0.70. Delta −0.25 exceeds the placeholder tolerance. Investigate cases and configuration before interpreting it. These are visibly scenario values, not observed model scores. The helper compares aggregate metrics but does not verify identical datasets. The implementation or concept reference is app/evaluation/compare.py.

---

# 10_Exercise / remove an observation

Set sampled_count=0 and the proxy to None. Predict not_measured rather than pass. Explain what evidence is needed before clearing an incident. Learners should preserve the incident until relevant observations support recovery. Operational latency recovery alone does not prove restored semantic quality.

---

# 11_Human feedback is a signal

A thumbs-down may mean wrong scope or poor wording. Review source, context and answer before accepting it. Never turn raw feedback directly into a golden answer. The feedback queue has pending, accepted and rejected states. Reviewer authentication and idempotent submission support workflow, while domain verification supplies truth. The implementation or concept reference is app/models/feedback.py; app/services/feedback.py.

---

# 12_The human review loop has owners

Signal → triage → source-supported correction Review → proposed golden case → regression replay Approved fix → measured release → observation This is our workshop interpretation of the course feedback loop. Each transition needs evidence and an owner, especially where policy meaning changes.

---

# 13_Practical 2 / inspect feedback behavior

Run feedback, sampling and comparison tests. Follow reviewer authentication and review transitions. Explain why accepted feedback still needs a verified reference. The existing API stores client-submitted response data. The class should not treat a submitted provenance object as a trusted replay of server execution. The implementation or concept reference is training/session5/handout.md.

---

# 14_Promote a correction manually

Copy a golden case and verify the policy clause. Write expected status and answer; validate load_golden. Keep reviewer, feedback reference and rationale in a memo. The practical is a manual promotion exercise. An automatic feedback export service is not implemented by this delivery, and no category mapping is silently chosen.

---

# 15_Governance follows the change’s meaning

Engineering reviews code and operational behavior. A domain expert reviews policy meaning and golden answers. The designated owner approves real data use and risk. These are proposed workshop responsibilities. Record actual names and approval dates for a real release instead of inventing an organization-specific approval matrix.

---

# 16_Practical 3 / rehearse rollback

Hold candidate → preserve evidence → restore known-good set Replay failing and golden cases → measure representative traffic Document owner decision and follow-up regression case This is a tabletop, not a deployment script. Restore compatible code, prompts, models and retrieval stores; rehearse the exact operational switch before any real release.

---

# 17_A new index name is not a data snapshot

Ingestion mutates the configured chunk collection. Parent sections must also match the candidate corpus. Blue/green requires isolated compatible stores and a tested switch. Do not imply that changing VECTOR_INDEX_NAME alone performs safe rollback. Separate parent data matters because generation uses those sections after retrieval. The implementation or concept reference is app/database/mongo.py; app/chains/ingestion.py.

---

# 18_What belongs in the release file

Prompt/model/retrieval identities and dataset hash. Offline quality report and representative SLO evidence. Approver, rollback owner, known limits and incident links. This workspace copy has no Git metadata. Do not invent a commit or release tag; use actual identifiers from the environment where the release is built. The implementation or concept reference is training/session5/handout.md.

---

# 19_Agents add actions and new failure modes

Tool access needs permissions and an allowlist. Loops need iteration, time and cost bounds. Side effects need isolation, audit and recovery. Agents are future scope here. The existing read-only RAG assistant does not become an agent merely because the course discusses tool loops. The implementation or concept reference is Educative: Future Directions in LLMOps.

---

# 20_Multimodality and smaller models need evidence

New input types expand ingestion and privacy work. Distillation adds a versioned training-data lifecycle. Add capability only with a concrete use case and evaluation. Treat these as future directions rather than promises about latency, privacy or cost. Each new capability changes the evaluation and operational contract.

---

# 21_Final gate / defend the decision

Submit manifest, retrieval experiment and golden review. Attach quality/SLO reports and an incident write-up. State release, hold or unmeasured with supporting evidence. A successful class demonstrates engineering judgment and reproducible exercises. It does not certify a real production environment that has not been tested.

---

# 22_Operate the loop, not just the endpoint

Version the artifacts that change answers. Measure evidence, meaning and operations separately. Turn reviewed failures into durable regression cases. Close by asking each pair what they would investigate first after an incorrect fee answer. Point learners to the source course and local handouts for continued practice.
