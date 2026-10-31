# Sessions 1–2 aligned to LLMOps_Syllabus.md

Updated 24 October 2026. The supplied [platform-agnostic syllabus](../../LLMOps_Syllabus.md) is the primary topic authority for this revision. Session 1 remains **Discover**; Session 2 is **LLMOps Core**, incorporating the earlier Distill I RAGOps foundation. Session 1 contains **16 editable slides**; Session 2 contains **19**, with instructor notes throughout. NexaAssist supplies a worked example and runnable offline exercises; the operating controls apply across platforms.

Each three-hour class allocates 25 minutes to concepts, 20 to the architecture/code walkthrough, 90 to practicals including a 10-minute break, 25 to the exit review and 20 to recap. Commands run from the repository root in the existing environment; the core labs need no provider, Atlas or Datadog credentials.

## Session 1 — lifecycle, release evidence and governance

| Slide | Operating topic | Syllabus sections | Learner action or evidence |
|---:|---|---|---|
| 1 | Outcomes and practical contract | 01, 03, 09–11 | Identify the four submission artifacts |
| 2 | Quality, latency, cost and release responsibility | 01, 03, 08, 14 | Define model-selection criteria and a comparable baseline |
| 3 | Model inventory and lifecycle | 01, 10, 11 | Record ID/provider, owner, purpose, approval state and compatibility checks |
| 4 | Versioned release bundle | 01–03, 10, 11 | Name corpus, prompt, runtime and evaluation owners |
| 5 | Discover → Distill → Deploy → Deliver | 01, 03, 11, 14 | Distinguish configuration validity from release approval |
| 6 | System context and operational ownership | 10, 15 | Assign dependency and data responsibilities |
| 7 | Containers and telemetry responsibility | 04, 10, 12 | Identify the processes and evidence boundaries |
| 8 | Ingestion/answer contract | 01, 04, 12 | Connect source, embedding, retrieval and release identities |
| 9 | Request path and failure classification | 03–05, 09 | Mark validation, retrieval, model and output failures |
| 10 | Freshness, permissions and auditability | 09, 10, 12 | Record disclosure, retention/residency and access-review decisions |
| 11 | Frozen evaluation baseline | 03, 05, 11 | Select normal, refusal and date-boundary cases; propose an adversarial case |
| 12 | Gate-validation practical | 01, 03, 10, 11 | Capture valid-placeholder and invalid-threshold outputs |
| 13 | Source-integrity code boundary | 09, 10, 12 | Explain what a SHA-256 comparison establishes |
| 14 | Source-tamper practical | 09–11 | Capture document ID/error and a HOLD decision |
| 15 | Provider-change review tabletop | 01–03, 10, 11, 14 | Submit inventory, missing checks, approver and rollback/retirement plan |
| 16 | Release-readiness assessment | 01, 03, 10, 11, 14 | Defend an evidence-based release decision |

Practical block: inventory and baseline worksheet **20 min**; gate validation **15 min**; source tamper **20 min**; provider-change review **25 min**; break **10 min**. See the [Session 1 worksheet](../session1/handout.md#syllabus-delivery--required-practical-block-90-minutes).

## Session 2 — LLMOps Core: Observability, Evaluation & Security

Revised at the user's request to **19 pages, under 20**, retaining the RAGOps foundation and adding full core sections with practicals. Primary worked tools are Datadog, Ragas, LiteLLM and Guardrails AI; Phoenix, DeepEval, Portkey and NeMo Guardrails are alternatives.

| Slide | Topic / practical | Syllabus sections |
|---:|---|---|
| 1 | LLMOps Core | 03, 04, 05, 07, 09, 12 |
| 2 | Four operating questions / one evidence pack | 03, 04, 07, 09, 12 |
| 3 | RAGOps recap / publish verifiable evidence | 04, 09, 12 |
| 4 | Practical / chunking and repeat ingestion | 01, 03, 08, 12 |
| 5 | Retrieve scoped and complete evidence | 03, 04, 09, 12 |
| 6 | Practical / keep the policy regression baseline | 03, 05, 09, 12 |
| 7 | Observability / follow one request across stages | 04, 12, 14 |
| 8 | Measure latency, usage and failure signals | 04, 05, 08, 14 |
| 9 | Practical / inspect a correlated Datadog trace | 04, 05, 14 |
| 10 | EvalOps / build the evaluation harness | 02, 03, 05, 11 |
| 11 | Evals / separate coverage from supported claims | 03, 05, 12 |
| 12 | Practical / score candidates and enforce gates | 03, 05, 11, 12 |
| 13 | Gateway / Ollama and OpenAI behind stable aliases | 07, 08, 09, 12, 14 |
| 14 | LiteLLM / explicit routing and bounded failure | 07, 08, 09, 14 |
| 15 | Practical / fail over, balance and cache | 07, 08, 09, 14 |
| 16 | Guardrails / validate at each trust boundary | 07, 09, 10, 12 |
| 17 | Practical / PII and prompt injection defenses | 03, 09, 10, 12 |
| 18 | Practical / strict output with Guardrails AI | 03, 09, 11 |
| 19 | Session 2 / operating-readiness exit gate | 03, 04, 05, 07, 08, 09, 11, 12, 14 |

Required practical block: RAGOps **15 min**; observability **15 min**; evals **15 min**; gateway **20 min**; security **15 min**; break **10 min**. The existing three-hour schedule is retained. Core offline exercises use real local controls and labeled fixtures; gateway policy predictions are a design worksheet. The [live guide](../session2/live_practicals.md) adds prepared-service exercises with the requested Ollama `qwen3.5:9b-mlx` and `qwen3-embedding:0.6b`, plus OpenAI chat and embeddings. The [four-alias gateway YAML](../session2/litellm.yaml) keeps chat fallback separate from embedding profiles and leaves cache off initially.

Submit the trace/diagnostic, evaluation, routing/cache and guardrail evidence packs alongside versioned RAGOps cases. For unavailable services record `not_measured`; no offline fixture or worksheet establishes a live gateway, model-quality or security claim.

## Coverage depth and continuation

These two decks do not claim to exhaust all 15 syllabus areas. “Introduced” means a concept, worksheet or boundary is taught; it does not imply a deployed capability.

| Syllabus area | Depth in Sessions 1–2 | Continuation in the existing five-session structure |
|---|---|---|
| 01 Lifecycle/release | Inventory, candidate comparison, compatibility, rollback and retirement tabletop | Session 3 quality comparison; Sessions 4–5 deployment and recovery |
| 02 PromptOps | Introduced: owner, template/parameters, tests, release/rollback identity | Session 3 experiments, regression and prompt lifecycle |
| 03 EvalOps | Frozen datasets, retrieval scoring, harness flow, Ragas metric definitions, offline gates and live candidate-comparison exercise | Session 3 deeper judge calibration, prompt experiments and human review |
| 04 Tracing/observability | Session 2 core section: trace map, latency/token/error signals, offline Datadog capture and prepared live Datadog/Phoenix work | Session 5 deeper monitoring; token-stream timing needs a streaming endpoint |
| 05 Production quality | Introduced: grounded evidence, refusal, structured/citation validity and incident classification | Sessions 3 and 5 answer evaluation, sampling, feedback, drift and dashboards |
| 06 Inference endpoints | Operating limits introduced; provisioning, scaling, batching and capacity outside these two sessions | Session 4 |
| 07 Gateway operations | Session 2 core section: four-alias LiteLLM config, chat fallback, balancing, cache/invalidation and fault experiments | Session 4 deployment policies; classroom gateway is not integrated into the application factories |
| 08 FinOps | Token/cost selection criteria and avoided re-embedding introduced | Session 4 cost/capacity; budget/allocation enforcement requires additional work |
| 09 Security operations | Session 2 core section: PII/prompt/output controls, negative cases, Guardrails AI schema exercise and defense boundaries | Session 4 deeper authentication, tool permissions, deployment hardening and incidents |
| 10 Governance/audit | Owners, provenance, source access, approval evidence, retention/residency and retirement review | Session 5 human review and governance |
| 11 CI/CD/release validation | Manual evidence/reproducibility, gates and compatibility review | Sessions 3–5; no automated PR, canary or shadow pipeline is claimed |
| 12 RAGOps | Main Session 2 focus; freshness, versions, embedding migration design, retrieval evaluation and triage | Live readiness/quality/latency/cost require separately approved measurement |
| 13 AgentOps | Deferred | Session 5; stateful/agent capabilities follow project layer rules |
| 14 Reliability/incidents | HOLD/rollback tabletop and retrieval incident/recovery worksheet | Sessions 4–5 SLOs, outages, runbooks and recovery |
| 15 Platform capabilities | Ownership boundaries introduced | Session 5; shared registries/services are design extensions |

The continuation column is a teaching placement, not a claim that the unchanged later decks cover every syllabus bullet.

## Delivery sources and limits

Current authoring workspaces are `NexaAssist_S1_syllabus_20261024/` and `NexaAssist_S2_core_20261024/`, using `authoring-svg-flat/` and `notes/`. Session 2 uses `page_plan.json` for 19 `core_NN.svg` copies; the preceding 16-page version is retained in its source package. Original decks are preserved inside their `sources/source.pptx`. Session 1 retains its order; Session 2 maps source skeletons to its 19-page topic sequence. Notes are updated, narration stays off and source motion policy is preserved. The [machine-readable map](syllabus_alignment.json) and `course_manifest.json` identify all 35 slides. Earlier Educative lesson links remain in notes as supporting references; their historical map is not the current syllabus authority.

Offline scores are constructed fixture observations, not live model quality, search recall, security coverage or service capacity. NDCG is a manual extension; the existing scorer reports recall and reciprocal rank, including its documented full-amendment convention. Thresholds remain placeholders, and live embedding migration, index promotion, provider switching, trace capture and CI automation were not performed by these exercises. See [current delivery verification](session_1_2_verification.md).
