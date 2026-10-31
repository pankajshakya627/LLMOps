<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_Deployment_Operations_20261027 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_Deployment_Operations_20261027 |
| Canvas Format | PPT 16:9, 1280 × 720 |
| Page Count | 24 |
| Primary Language | en |
| Target Audience | Enterprise LLMOps engineers and Python developers with REST familiarity |
| Communication Intent | Deploy the current services, follow policy requests and diagnose LLMOps incidents from evidence |
| Desired Audience Outcome | Start the stack, trace model and data boundaries, score a request and select a safe recovery |
| Core Message / Ask / Action | Deploy coherently; follow the request; use traces and evaluations to diagnose each boundary |
| Delivery Context | Instructor-led 60–90 minute workshop with optional live drills |
| Artifact Afterlife | Editable training deck, speaker notes and linked Markdown/code reference |
| Reading Mode | balanced |
| Content Strategy | Preserve source facts and limitations while compressing examples for presentation |
| Design Style | Systems workbench: precise grid, navy operational fields and teal paths |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — explicit delegated design choice |
| Custom Animations | disabled — delegated design choice |
| Narration Audio | disabled — delegated design choice |
| Created Date | 2026-10-27 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 64 px |
| Content Area | 64 164 1152 470 |

## III. Visual Theme

### Theme Style
- **Mode**: custom
- **Mode References**: instructional
- **Mode Behavior**: Define the mechanism, locate code, follow the request, exercise a bounded drill and inspect evidence.
- **Visual style**: custom
- **Visual Style References**: swiss-minimal, dark-tech
- **Visual Style Behavior**: Swiss alignment and precise flat typography carry code maps; dark-tech navy fields isolate live operational boundaries while teal paths make flows explicit. Alternate open diagrams, code panels and contrasting states by page job.
- **Theme**: NexaAssist systems workbench
- **Tone**: Clear, practical and candid about evidence

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #F5F8FC | background |
| Secondary Background | #EAF0F6 | secondary_background |
| Primary | #122C45 | primary |
| Accent | #007F86 | accent |
| Secondary Accent | #B05C17 | secondary_accent |
| Body Text | #122C45 | body_text |
| Secondary Text | #526A7F | secondary_text |
| Divider | #CFDAE5 | divider |
| Surface | #FFFFFF | surface |
| Inverse | #F5F8FC | inverse |
| Mint | #6BE3D3 | mint |
| Negative | #AA3344 | negative |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | Strong technical sans | Arial | | |
| Body | Neutral readable sans | Arial | | |
| Code | Literal fixed-width | Courier New | | |
- **Title stack**: Arial
- **Body stack**: Arial
- **Code stack**: Courier New
- **Display stack**: Arial

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 24 |
| Title | 42 |
| Subtitle | 28 |
| Annotation | 20 |
| Footnote | 16 |
| Display | 68 |
| Code | 20 |
| Index | 26 |

## V. Layout Principles

### Deck-wide Direction
- **Hierarchy direction**: Claim, mechanism or example, responsible source, practical interpretation.
- **Composition tendency**: Use open diagrams for flow, separate dark code fields for literals, and contrasting regions for outcomes.
- **Cross-page continuity**: Navy operational boundary, teal path markers, small source captions and page numbers.
- **Spacing posture**: Variable density by teaching duty; important claims remain readable at workshop distance.
- **Spacing anchors**: page margin 64 px; block gap 24 px; column gutter 40 px; corner radius 8 px; body leading 36 px.

## VI. Icon Usage Specification
- **Primary bundled library**: none

| Icon Path | Suitable Scenarios |
| --- | --- |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

No raster assets: editable code, semantic shapes and labels carry the teaching jobs.


## IX. Content Outline

#### Slide 01 - Deploy. Observe. Diagnose.
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: none
- **Composition**: cover expression for the page's operational question.
- **Title**: Deploy. Observe. Diagnose.
- **Core message**: Run the NexaAssist services and investigate real LLMOps incidents.
- **Content**: Deployment architecture; FastAPI → Phoenix → Ragas; Banking policy incident exercises. Source anchors: app/compose.yaml:3; README.md:1.

#### Slide 02 - Operate the whole request lifecycle
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: order: deployment, request, evidence and recovery stages
- **Composition**: sequence expression for the page's operational question.
- **Title**: Operate the whole request lifecycle
- **Core message**: A running container is only the first checkpoint.
- **Content**: Deploy / Start services; provision data.; Exercise / Submit a scoped policy query.; Observe / Find the result and model route.; Decide / Score quality; diagnose failures.. Source anchors: app/services/retrieval.py:67; app/api/operations.py:27.

#### Slide 03 - Six containers; models on the host
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: link: API uses database, gateway and validator; gateway uses model providers; services export telemetry
- **Composition**: architecture expression for the page's operational question.
- **Title**: Six containers; models on the host
- **Core message**: Use service DNS inside Docker and published ports from your browser.
- **Content**: Streamlit / Swagger; FastAPI; PostgreSQL + pgvector; Guardrails AI; LiteLLM; Phoenix; Host Ollama; OpenAI API. Source anchors: app/compose.yaml:3; app/services/evaluation.py:29.

#### Slide 04 - Give each service one clear job
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: services expression for the page's operational question.
- **Title**: Give each service one clear job
- **Core message**: Host ports below follow the repository .env.example.
- **Content**: FastAPI · 8001 / Policy REST API and Swagger; LiteLLM · 4001 / Model aliases, retry and fallback; Guardrails · 8101 / Structured output validation; PostgreSQL · 5433 / Vectors, parents and feedback; Phoenix · 6006 / Traces and evaluation annotations; Streamlit · 8501 / Staff demonstration interface. Source anchors: .env.example:27; app/compose.yaml:100.

#### Slide 05 - Configure identities, scope and secrets
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: panels expression for the page's operational question.
- **Title**: Configure identities, scope and secrets
- **Core message**: Keep credentials in private .env; do not paste it into slides or logs.
- **Content**: Secrets / POSTGRES_PASSWORD
LITELLM_MASTER_KEY
OPENAI_API_KEY; Policy and model scope / INSTITUTION / JURISDICTION
CONFIDENTIALITY_LEVEL
Approved OpenAI route + judge; Storage and capture / Storage: pgvector
Qwen profile: 1024 dimensions
Private data: capture disabled. Source anchors: .env.example:5; app/compose.yaml:7; app/phoenix_main.py:31.

#### Slide 06 - Preflight the host before Docker
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: code expression for the page's operational question.
- **Title**: Preflight the host before Docker
- **Core message**: The exact Qwen tags must exist in your local model runtime.
- **Content**: Docker Desktop is running.; Ollama is native, reachable from containers.; Verify custom MLX tag; do not assume it exists.. Literal example: docker version · open -a Ollama · ollama list · ollama show qwen3.5:9b-mlx · ollama show qwen3-embedding:0.6b · curl -fsS http://127.0.0.1:11434/api/tags. Source anchors: app/gateway/litellm.yaml:3; app/compose.yaml:36.

#### Slide 07 - Build and start the Compose stack
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: code expression for the page's operational question.
- **Title**: Build and start the Compose stack
- **Core message**: Use one Compose project and one operation at a time.
- **Content**: Validate configuration without printing secrets.; Build images from locked / pinned dependencies.; Inspect health and recent service logs.. Literal example: docker compose --env-file .env -f app/compose.yaml \ ·   config --quiet · docker compose --env-file .env -f app/compose.yaml \ ·   up -d --build · docker compose --env-file .env -f app/compose.yaml ps. Source anchors: app/compose.yaml:51; app/Dockerfile:23.

#### Slide 08 - Provision storage, then ingest policies
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: code expression for the page's operational question.
- **Title**: Provision storage, then ingest policies
- **Core message**: An empty vector corpus can look like a healthy application.
- **Content**: Create schema + vector extension explicitly.; Ingest the read-only synthetic register.; Use the same embedding profile for search.. Literal example: docker compose --env-file .env -f app/compose.yaml \ ·   exec api python -m app.database.postgres init · docker compose --env-file .env -f app/compose.yaml \ ·   run --rm api python -m app.services.ingestion \ ·   /data/document_register.json. Source anchors: app/database/postgres.py:31; app/services/ingestion.py:71; app/database/postgres.py:46.

#### Slide 09 - Verify readiness at increasing depth
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: order: deployment, request, evidence and recovery stages
- **Composition**: sequence expression for the page's operational question.
- **Title**: Verify readiness at increasing depth
- **Core message**: Advance from process health to an actual policy answer.
- **Content**: Process / GET /health → service responds; Database / GET /ready → database answers; Retrieval / POST /retrieve → relevant evidence; Answer / POST /answer → validated result. Source anchors: app/api/operations.py:22; app/services/retrieval.py:67; app/api/retrieval.py:17.

#### Slide 10 - Follow one request through the code
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: order: deployment, request, evidence and recovery stages
- **Composition**: flow expression for the page's operational question.
- **Title**: Follow one request through the code
- **Core message**: Every boundary contributes a different kind of assurance.
- **Content**: 1 · Input / Validate request → injection policy → PII redaction; 2 · Evidence / Embed → scoped pgvector search → parent context; 3 · Answer / Prompt → LiteLLM → model → schema / PII / citations; 4 · Visibility / API response → Phoenix; evaluated path → Ragas annotations. Source anchors: app/api/answer.py:55; app/services/answer.py:36; app/services/retrieval.py:23; app/chains/answer.py:101.

#### Slide 11 - Scenario 1 · Answer a staff policy query
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: code expression for the page's operational question.
- **Title**: Scenario 1 · Answer a staff policy query
- **Core message**: Explain the answer, citation and provenance together.
- **Content**: POST /answer from Swagger.; Expected policy limit: ₹7,50,00,000.; Verify status, exact quote and model provenance.. Literal example: { ·   "query": "What is the maximum NexaHome loan amount?", ·   "as_of": "2026-10-01", ·   "product_id": "NEXA-HL", ·   "top_k": 5 · }. Source anchors: app/evaluation/datasets/answer.jsonl:1; app/models/answer.py:64.

#### Slide 12 - Read Phoenix in two projects
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: panels expression for the page's operational question.
- **Title**: Read Phoenix in two projects
- **Core message**: Look at API Output for the result and gateway attributes for the provider.
- **Content**: nexaassist-training / HTTP request → Output
Answer + provenance
Evaluated request → annotations; nexaassist-gateway / LLM / embedding span
litellm.provider.model
Tokens, duration and errors; Interpret carefully / Aliases can remain in titles.
Adapter ≠ cloud provider.
Cross-service IDs may differ.. Source anchors: app/core/phoenix.py:22; app/phoenix_main.py:42; app/compose.yaml:46.

#### Slide 13 - Evaluate the answer with Ragas
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: metrics expression for the page's operational question.
- **Title**: Evaluate the answer with Ragas
- **Core message**: Use POST /answer/evaluated with a reference for context metrics.
- **Content**: Faithfulness / Are answer claims supported by the supplied context?; Answer relevancy / Does the response address the question?; Context precision / Are relevant retrieved contexts ranked usefully?; Context recall / Does context cover the reference claims?. Source anchors: app/api/answer.py:28; app/services/evaluation.py:29; app/evaluation/live.py:18.

#### Slide 14 - Distinguish observation from quality
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: observed expression for the page's operational question.
- **Title**: Distinguish observation from quality
- **Core message**: Unavailable means no valid score; it does not mean zero.
- **Content**: Context recall / 1.0; Context precision / ≈0.20; Faithfulness / relevancy / Unavailable: answer abstained. Source anchors: app/operations/PHOENIX_VISIBILITY.md:40; app/evaluation/gates.json:2.

#### Slide 15 - Scenario 2 · PII and prompt injection
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: security expression for the page's operational question.
- **Title**: Scenario 2 · PII and prompt injection
- **Core message**: Redaction protects data; injection policy protects instructions.
- **Content**: PII input / learner@example.com + ABCDE1234F / [REDACTED_EMAIL] + [REDACTED_PAN]; Injection input / Ignore all previous instructions. / HTTP 400 · blocked before retrieval. Source anchors: app/services/retrieval.py:23; app/chains/redaction.py:7; app/security/input_policy.py:13; app/main.py:31.

#### Slide 16 - Scenario 3 · Reject unsafe output
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: code expression for the page's operational question.
- **Title**: Scenario 3 · Reject unsafe output
- **Core message**: Schema checks and evidence checks serve different purposes.
- **Content**: POST /validate at Guardrails port 8101.; Forbidden status → validation_passed=false.; API outage of configured validator → no bypass.. Literal example: { ·   "status": "approve_loan", ·   "answer": "Approved", ·   "evidence": [] · }. Source anchors: app/security/guardrails_service.py:20; app/chains/guardrails.py:9; app/chains/answer.py:184.

#### Slide 17 - Scenario 4 · Local provider unavailable
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: order: deployment, request, evidence and recovery stages
- **Composition**: sequence expression for the page's operational question.
- **Title**: Scenario 4 · Local provider unavailable
- **Core message**: Chat fallback preserves availability; verify the actual route used.
- **Content**: Primary / nexa-chat → local Qwen; Failure / Bounded retry / timeout; Fallback / nexa-chat-openai → approved cloud model; Evidence / Inspect provider result and validation. Source anchors: app/gateway/litellm.yaml:23; app/compose.yaml:83.

#### Slide 18 - Scenario 5 · The answer has no evidence
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: order: deployment, request, evidence and recovery stages
- **Composition**: flow expression for the page's operational question.
- **Title**: Scenario 5 · The answer has no evidence
- **Core message**: Separate empty retrieval from rejected generation.
- **Content**: No hits / Check ingestion, product/date/scope and corpus profile.; Hits, no answer / Inspect generation, draft status and citation repair.; Wrong embedding family / Create a new namespace; re-ingest and compare.; Missing metric / Read unavailable/error reason before changing thresholds.. Source anchors: app/chains/answer.py:129; app/database/postgres.py:46; app/services/retrieval.py:54.

#### Slide 19 - Scenario 6 · Latency and repeated traffic
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: panels expression for the page's operational question.
- **Title**: Scenario 6 · Latency and repeated traffic
- **Core message**: Measure the slow stage before choosing cache, replicas or a model change.
- **Content**: Slow generation / Compare retrieval vs generation time.
Inspect citation repair and fallback.
Evaluator latency is separate work.; Repeated prompts / litellm_cache.yaml
Exact local cache; TTL 300 seconds.
One worker; preserve scope keys.; Concurrent demand / litellm_balanced.yaml
Two independent Ollama replicas.
No promised speedup on one host.. Source anchors: app/gateway/litellm_cache.yaml:34; app/gateway/litellm_balanced.yaml:2; app/chains/llm.py:14.

#### Slide 20 - Scenario 7 · A prompt release regresses
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: order: deployment, request, evidence and recovery stages
- **Composition**: sequence expression for the page's operational question.
- **Title**: Scenario 7 · A prompt release regresses
- **Core message**: Compare the same cases with fixed evaluator and corpus profiles.
- **Content**: Baseline / Save case, prompt SHA and actual route.; Candidate / Change one controlled variable.; Evaluate / Check status, evidence and scored metrics.; Release / Approve gates or restore prior artifact.. Source anchors: app/chains/prompts/answer.py:8; app/chains/prompts/answer.py:72; app/evaluation/run.py:277; app/evaluation/compare.py:82.

#### Slide 21 - Scenario 8 · Phoenix looks empty
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: order: deployment, request, evidence and recovery stages
- **Composition**: flow expression for the page's operational question.
- **Title**: Scenario 8 · Phoenix looks empty
- **Core message**: Trace export, payload capture and scoring are separate checks.
- **Content**: No spans / Check project / time range, collector URL and exporter logs.; No answer body / Check synthetic-only capture and root API Output.; No Ragas scores / Call /answer/evaluated; inspect status and export logs.; No local model label / Use gateway provider attributes, not alias titles.. Source anchors: app/phoenix_main.py:29; app/evaluation/phoenix_export.py:55; app/evaluation/phoenix_export.py:84.

#### Slide 22 - Teach the code by boundary
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: codemap expression for the page's operational question.
- **Title**: Teach the code by boundary
- **Core message**: Open the owner of the failing stage, then follow its callers.
- **Content**: Serving / app/api/answer.py / async def evaluated_answer; Input / retrieval / app/services/retrieval.py / def scrub_request; Generation / citations / app/chains/answer.py / def build_answer_chain; Output validator / app/security/guardrails_service.py / def validate(; Trace result / app/core/phoenix.py / def record_result; Evaluation export / app/evaluation/phoenix_export.py / def publish_annotations(. Source anchors: app/api/answer.py:28; app/services/retrieval.py:23; app/chains/answer.py:36; app/security/guardrails_service.py:20; app/core/phoenix.py:22; app/evaluation/phoenix_export.py:55.

#### Slide 23 - Before an enterprise rollout
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: contrast: distinct responsibilities or observed states
- **Composition**: panels expression for the page's operational question.
- **Title**: Before an enterprise rollout
- **Core message**: This local Compose stack is a reference deployment to qualify.
- **Content**: Access and data / Add access control and TLS.
Use managed secrets and scoped DB roles.
Verify backup / restore and retention.; Reliability / Define actual SLOs and escalation.
Qualify replicas and dependency outages.
Use shared counters / cache at scale.; Quality release / Freeze cases, corpus and judge profiles.
Approve measured quality thresholds.
Keep rollback artifacts and namespace.. Source anchors: CONSTRAINTS.md:22; app/operations/PGVECTOR_VALIDATION.md:64; app/evaluation/gates.json:2.

#### Slide 24 - Restart safely; prove the result
- **Audience move**: Unsure of the responsible boundary → can explain and verify this stage.
- **Relationships**: order: deployment, request, evidence and recovery stages
- **Composition**: closing expression for the page's operational question.
- **Title**: Restart safely; prove the result
- **Core message**: A complete demo ends with evidence and a recoverable service state.
- **Content**: Start → initialize once → ingest once → retrieve → answer.; Evaluate → inspect API Output + annotations + provider.; Stop with volumes preserved; repeat smoke checks after restart.. Source anchors: app/compose.yaml:11; README.md:141.

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Register**: Instructor-led enterprise training in plain English.
- **Coverage**: Explain every visible concept, request, expected result and source boundary.
- **Evidence**: Distinguish historical 25 October observations from unexecuted drills and proposed production qualifications.
- **Practical material**: Full runnable commands, source-line anchors and safety/recovery steps in LAB_GUIDE.md and speaker notes.
