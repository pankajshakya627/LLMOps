<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_S1_aligned_20261023 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_S1_aligned_20261023 |
| Canvas Format | PPT 16:9, 1280 × 720 |
| Page Count | 43 |
| Primary Language | en |
| Target Audience | Python developers with REST familiarity |
| Communication Intent | Teach concepts through actual NexaAssist code and practical failure experiments |
| Desired Audience Outcome | Run the session labs and defend an evidence-based gate decision |
| Core Message / Ask / Action | Version, measure and review the artifacts that change RAG behavior |
| Delivery Context | Instructor-led three-hour workshop |
| Artifact Afterlife | Editable slides, notes and repo handouts |
| Reading Mode | balanced |
| Content Strategy | Original code walkthroughs, concise concepts and concrete exercises |
| Design Style | Engineering field guide |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — delegated author decision |
| Custom Animations | disabled — delegated author decision |
| Narration Audio | disabled — delegated author decision |
| Created Date | 2026-10-23 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 64 px |
| Content Area | 64 160 1152 470 |

## III. Visual Theme

### Theme Style
- **Mode**: custom
- **Mode Behavior**: Start with a measurable outcome, explain the mechanism, exercise real code, inspect failure and close with a gate.
- **Visual style**: custom
- **Visual Style Behavior**: Engineering field guide with warm paper, dark code fields, numbered sequences and broad whitespace; use sharp edges and a restrained per-session accent.
- **Theme**: NexaAssist engineering workshop
- **Tone**: Precise, practical and candid

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #F5F3EC | background |
| Primary | #132C42 | primary |
| Body Text | #132C42 | body_text |
| Secondary Text | #526375 | secondary_text |
| Divider | #CCD3D8 | divider |
| Surface | #FFFFFF | surface |
| Secondary Background | #E8EDF0 | secondary_background |
| Positive | #176849 | positive |
| Warning | #98521A | warning |
| Negative | #A13442 | negative |
| Accent | #087E8B | accent |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | Strong technical sans | Trebuchet MS | | |
| Body | Neutral readable sans | Arial | | |
| Code | Literal monospace | Courier New | | |
- **Title stack**: Trebuchet MS
- **Body stack**: Arial
- **Code stack**: Courier New
- **Display stack**: Trebuchet MS
- **Role rationale**: Code preserves source indentation; display establishes the session title.

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 26 |
| Title | 40 |
| Subtitle | 30 |
| Annotation | 20 |
| Footnote | 16 |
| Display | 76 |
| Code | 20 |

## V. Layout Principles

### Deck-wide Direction
- **Hierarchy direction**: Title, mechanism or exercise, interpretation.
- **Composition tendency**: Mix open text, code fields, vertically numbered flows and lab/gate pages.
- **Cross-page continuity**: Session accent, stable footer and source caption.
- **Spacing posture**: Variable by teaching duty.
- **Spacing anchors**: page margin 64 px; block gap 24 px; column gutter 40 px; corner radius 0 px; body leading 38 px.

## VI. Icon Usage Specification
- **Primary bundled library**: none

| Icon Path | Suitable Scenarios |
| --- | --- |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

No raster images: diagrams and actual code communicate the mechanisms directly.

## IX. Content Outline

#### Slide 01 - Discover
- **Audience move**: Uncertain about discover → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: cover page, with the dominant teaching task as focal point.
- **Title**: Discover
- **Core message**: NexaAssist / LLMOps engineering workshop
- **Content**: NexaAssist / LLMOps engineering workshop · Session 1 of 5 · 3 hours · source-aligned workshop

#### Slide 02 - Today’s measurable outcomes
- **Audience move**: Uncertain about today’s measurable outcomes → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Today’s measurable outcomes
- **Core message**: Trace one question across the application layers.
- **Content**: Trace one question across the application layers. · Verify that trusted documents match the register. · Propose a gate and explain who approves it.

#### Slide 03 - Three hours with time to build
- **Audience move**: Uncertain about three hours with time to build → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Three hours with time to build
- **Core message**: 25 min concepts + 20 min code walkthrough
- **Content**: 25 min concepts + 20 min code walkthrough · 90 min pair labs, including a 10 min break · 25 min gate review + 20 min recap

#### Slide 04 - Showcase / can we trust this policy?
- **Audience move**: Uncertain about showcase / can we trust this policy? → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Showcase / can we trust this policy?
- **Core message**: Staff need the approved policy explanation.
- **Content**: Staff need the approved policy explanation. · A file changes while its register hash stays fixed. · The ingestion boundary must reject that file.

#### Slide 05 - Run the evidence-integrity demonstration
- **Audience move**: Uncertain about run the evidence-integrity demonstration → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Run the evidence-integrity demonstration
- **Core message**: python -m training.showcase --session 1
- **Content**: python -m training.showcase --session 1 · Original: 8 documents verified. · Tampered copy: hash mismatch; ingestion refused.

#### Slide 06 - What Is LLMOps, and Why Does It Exist?
- **Audience move**: Uncertain about what is llmops, and why does it exist? → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: What Is LLMOps, and Why Does It Exist?
- **Core message**: Educative lesson 01
- **Content**: Educative lesson 01 · Concept → worked example → NexaAssist application

#### Slide 07 - LLMOps manages behavior under real constraints
- **Audience move**: Uncertain about llmops manages behavior under real constraints → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: LLMOps manages behavior under real constraints
- **Core message**: Correctness and safety are part of the product.
- **Content**: Correctness and safety are part of the product. · Latency shapes whether people can use the service. · Token consumption determines variable cost.

#### Slide 08 - From a convincing demo to an operated service
- **Audience move**: Uncertain about from a convincing demo to an operated service → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: From a convincing demo to an operated service
- **Core message**: A demo tests a few questions in a controlled setting.
- **Content**: A demo tests a few questions in a controlled setting. · Production introduces changing data, users and traffic. · The remedy is a repeatable evaluation and release loop.

#### Slide 09 - A successful request can still be wrong
- **Audience move**: Uncertain about a successful request can still be wrong → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: A successful request can still be wrong
- **Core message**: HTTP 200 tells us the service returned a response.
- **Content**: HTTP 200 tells us the service returned a response. · A valid quote can accompany an unsupported claim. · Measure retrieval and meaning alongside availability.

#### Slide 10 - How We Reached LLMOps
- **Audience move**: Uncertain about how we reached llmops → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: How We Reached LLMOps
- **Core message**: Educative lesson 02
- **Content**: Educative lesson 02 · Concept → worked example → NexaAssist application

#### Slide 11 - AI, ML, GenAI and LLMs describe different scopes
- **Audience move**: Uncertain about ai, ml, genai and llms describe different scopes → can explain the mechanism or required decision.
- **Relationships**: link: labelled dependencies between the stated units
- **Composition**: diagram page, with the dominant teaching task as focal point.
- **Title**: AI, ML, GenAI and LLMs describe different scopes
- **Core message**: AI: Goal-directed systems
- **Content**: AI: Goal-directed systems · ML: Learns patterns from data · GenAI: Creates new artifacts · LLMs: Language-generating models

#### Slide 12 - The operational burden moved toward integration
- **Audience move**: Uncertain about the operational burden moved toward integration → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The operational burden moved toward integration
- **Core message**: Research focused on building and training models.
- **Content**: Research focused on building and training models. · Interactive interfaces broadened access to generation. · Applications now coordinate data, APIs and model behavior.

#### Slide 13 - The artifact gap and the closed-box problem
- **Audience move**: Uncertain about the artifact gap and the closed-box problem → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The artifact gap and the closed-box problem
- **Core message**: Prompts, embeddings and knowledge can change separately.
- **Content**: Prompts, embeddings and knowledge can change separately. · Remote model internals are usually outside our control. · Debug using observed inputs, evidence, outputs and versions.

#### Slide 14 - MLOps to LLMOps: What Changes and What Stays
- **Audience move**: Uncertain about mlops to llmops: what changes and what stays → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: MLOps to LLMOps: What Changes and What Stays
- **Core message**: Educative lesson 03
- **Content**: Educative lesson 03 · Concept → worked example → NexaAssist application

#### Slide 15 - Keep the software-engineering foundation
- **Audience move**: Uncertain about keep the software-engineering foundation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Keep the software-engineering foundation
- **Core message**: Version control and CI still coordinate changes.
- **Content**: Version control and CI still coordinate changes. · Containers and reproducible dependencies still matter. · Infrastructure configuration still needs review and rollback.

#### Slide 16 - What changes from MLOps to LLMOps
- **Audience move**: Uncertain about what changes from mlops to llmops → can explain the mechanism or required decision.
- **Relationships**: link: labelled dependencies between the stated units
- **Composition**: diagram page, with the dominant teaching task as focal point.
- **Title**: What changes from MLOps to LLMOps
- **Core message**: Data: Features → documents + vectors
- **Content**: Data: Features → documents + vectors · Tuning: Parameters → prompts + retrieval · Artifacts: Weights → coupled runtime assets · Evaluation: Labels → semantic criteria

#### Slide 17 - Semantic drift needs meaning-aware evidence
- **Audience move**: Uncertain about semantic drift needs meaning-aware evidence → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Semantic drift needs meaning-aware evidence
- **Core message**: Different words can express the same request.
- **Content**: Different words can express the same request. · Similar words can refer to different domains. · Replay representative cases and review emerging topics.

#### Slide 18 - The 4D Framework (Discover, Distill, Deploy, Deliver)
- **Audience move**: Uncertain about the 4d framework (discover, distill, deploy, deliver) → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: The 4D Framework (Discover, Distill, Deploy, Deliver)
- **Core message**: Educative lesson 04
- **Content**: Educative lesson 04 · Concept → worked example → NexaAssist application

#### Slide 19 - Four phases, four decisions
- **Audience move**: Uncertain about four phases, four decisions → can explain the mechanism or required decision.
- **Relationships**: link: labelled dependencies between the stated units
- **Composition**: diagram page, with the dominant teaching task as focal point.
- **Title**: Four phases, four decisions
- **Core message**: Discover: Problem + permitted data
- **Content**: Discover: Problem + permitted data · Distill: Prove retrieval and generation · Deploy: Validate the serving envelope · Deliver: Observe and improve

#### Slide 20 - Discover produces an operating contract
- **Audience move**: Uncertain about discover produces an operating contract → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Discover produces an operating contract
- **Core message**: Define who asks what and which outcomes are excluded.
- **Content**: Define who asks what and which outcomes are excluded. · Identify sources, freshness, permissions and disclosure. · Name proposed quality, latency and cost criteria.

#### Slide 21 - Distill produces evidence, not a favorite prompt
- **Audience move**: Uncertain about distill produces evidence, not a favorite prompt → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Distill produces evidence, not a favorite prompt
- **Core message**: Tune chunking, retrieval, prompt and model together.
- **Content**: Tune chunking, retrieval, prompt and model together. · Use reviewed cases and capture per-case failures. · Separate a missing source from unsupported generation.

#### Slide 22 - Deploy and Deliver require different evidence
- **Audience move**: Uncertain about deploy and deliver require different evidence → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Deploy and Deliver require different evidence
- **Core message**: Deploy: representative traffic within approved budgets.
- **Content**: Deploy: representative traffic within approved budgets. · Deliver: quality signals, reviewed failures and recovery. · Missing measurements remain unknown, not successful.

#### Slide 23 - Proposed targets need a rationale
- **Audience move**: Uncertain about proposed targets need a rationale → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: Proposed targets need a rationale
- **Core message**: Quality: source-grounded answers and correct status.
- **Content**: Quality: source-grounded answers and correct status. · Operations: latency, error rate and priced cost. · Safety: a measured rollback signal and named owner.

#### Slide 24 - Architecture of a Retrieval-Augmented Generation Application
- **Audience move**: Uncertain about architecture of a retrieval-augmented generation application → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: Architecture of a Retrieval-Augmented Generation Application
- **Core message**: Educative lesson 05
- **Content**: Educative lesson 05 · Concept → worked example → NexaAssist application

#### Slide 25 - RAG separates knowledge preparation from answering
- **Audience move**: Uncertain about rag separates knowledge preparation from answering → can explain the mechanism or required decision.
- **Relationships**: link: labelled dependencies between the stated units
- **Composition**: diagram page, with the dominant teaching task as focal point.
- **Title**: RAG separates knowledge preparation from answering
- **Core message**: Sources: Registered policy documents
- **Content**: Sources: Registered policy documents · Ingestion: Parse, redact, embed, upsert · Knowledge: Vectors + parent sections · Inference: Retrieve, prompt, generate

#### Slide 26 - Freshness, permission and traceability are separate
- **Audience move**: Uncertain about freshness, permission and traceability are separate → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Freshness, permission and traceability are separate
- **Core message**: A fresh document can still be unauthorized.
- **Content**: A fresh document can still be unauthorized. · A permitted document can still be obsolete. · An answer needs a recoverable source identity.

#### Slide 27 - Repeated ingestion needs three guarantees
- **Audience move**: Uncertain about repeated ingestion needs three guarantees → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Repeated ingestion needs three guarantees
- **Core message**: Stable identities prevent duplicate accumulation.
- **Content**: Stable identities prevent duplicate accumulation. · Compatible versions prevent mixed embedding spaces. · Failure isolation preserves progress and exposes bad files.

#### Slide 28 - Budget the online path before adding hops
- **Audience move**: Uncertain about budget the online path before adding hops → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Budget the online path before adding hops
- **Core message**: Scenario: 2,000 ms total minus 1,500 ms generation.
- **Content**: Scenario: 2,000 ms total minus 1,500 ms generation. · That leaves 500 ms for queueing, retrieval and overhead. · Parallelism, caching and model choice require measurement.

#### Slide 29 - Use the existing layer boundaries
- **Audience move**: Uncertain about use the existing layer boundaries → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Use the existing layer boundaries
- **Core message**: chains/ owns pure LangChain runnables.
- **Content**: chains/ owns pure LangChain runnables. · database/ owns MongoDB client and retrieval setup. · services/ coordinates; api/ validates; ui/ renders.

#### Slide 30 - A thin route delegates to the service
- **Audience move**: Uncertain about a thin route delegates to the service → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: A thin route delegates to the service
- **Core message**: Dependency injection supplies settings; the service owns the workflow.
- **Content**: Dependency injection supplies settings; the service owns the workflow. Source excerpt: @router.post("/answer") / async def answer( /     request: RetrieveRequest, /     background: BackgroundTasks, /     settings: Annotated[Settings, Depends(get_settings)], / ) -> AnswerResponse: /     try: /         response = await answer_policy(request, settings) /         if should_sample(response, settings): /             background.add_task(score_sampled_answer, request, response, settings) /         return response /     except (

#### Slide 31 - Scoping and Planning a Production RAG Application
- **Audience move**: Uncertain about scoping and planning a production rag application → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: Scoping and Planning a Production RAG Application
- **Core message**: Educative lesson 06
- **Content**: Educative lesson 06 · Concept → worked example → NexaAssist application

#### Slide 32 - The source course builds an internal support assistant
- **Audience move**: Uncertain about the source course builds an internal support assistant → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The source course builds an internal support assistant
- **Core message**: Staff search internal policies and tool instructions.
- **Content**: Staff search internal policies and tool instructions. · The response must be grounded and cite its documentation. · A use-case manifest keeps later scope changes reviewable.

#### Slide 33 - Translate the stack without losing the lesson
- **Audience move**: Uncertain about translate the stack without losing the lesson → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Translate the stack without losing the lesson
- **Core message**: Course: FastAPI, PostgreSQL/pgvector, LiteLLM, Docker.
- **Content**: Course: FastAPI, PostgreSQL/pgvector, LiteLLM, Docker. · NexaAssist: FastAPI, MongoDB Atlas, LangChain, Docker. · Preserve responsibilities, validation and evaluation gates.

#### Slide 34 - The use-case contract is intentionally narrow
- **Audience move**: Uncertain about the use-case contract is intentionally narrow → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The use-case contract is intentionally narrow
- **Core message**: Explain synthetic policy clauses for staff.
- **Content**: Explain synthetic policy clauses for staff. · Ask for missing scope or abstain when unsupported. · Never approve credit or execute account actions.

#### Slide 35 - A trusted source needs an identity
- **Audience move**: Uncertain about a trusted source needs an identity → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: A trusted source needs an identity
- **Core message**: Register: doc_id, version, effective dates and hash.
- **Content**: Register: doc_id, version, effective dates and hash. · Authority and amendment relationships affect retrieval. · A changed file must fail source verification.

#### Slide 36 - Data permission is a release dependency
- **Audience move**: Uncertain about data permission is a release dependency → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Data permission is a release dependency
- **Core message**: Identify who owns and may access the source.
- **Content**: Identify who owns and may access the source. · Decide whether content may leave for embeddings or generation. · Set freshness and retention before using real documents.

#### Slide 37 - Map the interface boundary honestly
- **Audience move**: Uncertain about map the interface boundary honestly → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Map the interface boundary honestly
- **Core message**: Course examples describe /ingest and /chat.
- **Content**: Course examples describe /ingest and /chat. · NexaAssist uses an ingestion CLI and /answer routes. · Operational traces and feedback retain answer context.

#### Slide 38 - Practical 2 / tamper with a safe copy
- **Audience move**: Uncertain about practical 2 / tamper with a safe copy → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 2 / tamper with a safe copy
- **Core message**: Run: python -m training.session1.tamper
- **Content**: Run: python -m training.session1.tamper · Predict which document hash will fail. · Expected: 8 originals verify; changed PDF is refused.

#### Slide 39 - Practical 3 / inspect the gate contract
- **Audience move**: Uncertain about practical 3 / inspect the gate contract → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 3 / inspect the gate contract
- **Core message**: Run: python -m training.session1.check_gates app/evaluation/gates.json
- **Content**: Run: python -m training.session1.check_gates app/evaluation/gates.json · Change a copied faithfulness minimum to 1.5. · Expected: validation rejects a value outside [0, 1].

#### Slide 40 - Thresholds are typed data
- **Audience move**: Uncertain about thresholds are typed data → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Thresholds are typed data
- **Core message**: Status distinguishes placeholder numbers from owner-confirmed targets.
- **Content**: Status distinguishes placeholder numbers from owner-confirmed targets. Source excerpt: class Gates(BaseModel): /     model_config = ConfigDict(extra="forbid") /  /     # "placeholder" values are course examples that the owner has not yet confirmed. /     status: Literal["placeholder", "confirmed"] /     faithfulness_min: float = Fraction /     answer_relevancy_min: float = Fraction /     context_precision_min: float = Fraction /     context_recall_min: float = Fraction /     judge_correctness_min: float = Fraction /     judge_groundedness_min: float = Fraction /     status_match_rate_min: float = Fraction

#### Slide 41 - Exit gate / are we ready to experiment?
- **Audience move**: Uncertain about exit gate / are we ready to experiment? → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: gate page, with the dominant teaching task as focal point.
- **Title**: Exit gate / are we ready to experiment?
- **Core message**: Hand in the manifest and data-access decision.
- **Content**: Hand in the manifest and data-access decision. · Name source owner, restrictions and must-abstain cases. · Keep unresolved approvals visible in the release file.

#### Slide 42 - Check your understanding
- **Audience move**: Uncertain about check your understanding → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Check your understanding
- **Core message**: Does a SHA-256 match prove that a policy is correct?
- **Content**: Does a SHA-256 match prove that a policy is correct? · Can a healthy API answer from the wrong clause? · Which artifacts must be restored together?

#### Slide 43 - Next / prove retrieval before generation
- **Audience move**: Uncertain about next / prove retrieval before generation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: ending page, with the dominant teaching task as focal point.
- **Title**: Next / prove retrieval before generation
- **Core message**: Read app/chains/chunking.py.
- **Content**: Read app/chains/chunking.py. · Bring a table question and an effective-date trap. · Carry the manifest into Session 2.

## X. Speaker Notes Requirements
- **Generation**: enabled
Explain visible claims, practical commands, expected outcomes, sources and limitations.
