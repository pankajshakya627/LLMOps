<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_S1_20261023 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_S1_20261023 |
| Canvas Format | PPT 16:9, 1280 × 720 |
| Page Count | 22 |
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
| Code | Literal monospace | Consolas | | |
- **Title stack**: Trebuchet MS
- **Body stack**: Arial
- **Code stack**: Consolas
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
- **Content**: NexaAssist / LLMOps engineering workshop · Session 1 of 5 · 3 hours · Python + REST prerequisite

#### Slide 02 - Five sessions. One release file.
- **Audience move**: Uncertain about five sessions. one release file. → can explain the mechanism or required decision.
- **Relationships**: order: the stages progress in the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: Five sessions. One release file.
- **Core message**: Discover → scope and data contract
- **Content**: Discover → scope and data contract · Distill → retrieval, prompts and evaluation · Deploy + Deliver → secure service and operations

#### Slide 03 - Today’s measurable outcomes
- **Audience move**: Uncertain about today’s measurable outcomes → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Today’s measurable outcomes
- **Core message**: Trace one question across the application layers.
- **Content**: Trace one question across the application layers. · Verify that trusted documents match the register. · Propose a gate and explain who approves it.

#### Slide 04 - Three hours with time to build
- **Audience move**: Uncertain about three hours with time to build → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Three hours with time to build
- **Core message**: 25 min concepts + 20 min code walkthrough
- **Content**: 25 min concepts + 20 min code walkthrough · 90 min pair labs, including a 10 min break · 25 min gate review + 20 min recap

#### Slide 05 - A successful request can still be wrong
- **Audience move**: Uncertain about a successful request can still be wrong → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: A successful request can still be wrong
- **Core message**: HTTP 200 tells us the service returned a response.
- **Content**: HTTP 200 tells us the service returned a response. · A valid quote can accompany an unsupported claim. · Measure retrieval and meaning alongside availability.

#### Slide 06 - The deployable unit has several artifacts
- **Audience move**: Uncertain about the deployable unit has several artifacts → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The deployable unit has several artifacts
- **Core message**: Code + dependency lock + container
- **Content**: Code + dependency lock + container · Prompt ID/version/hash + model configuration · Corpus register + embedding schema + golden dataset

#### Slide 07 - The 4D loop has explicit gates
- **Audience move**: Uncertain about the 4d loop has explicit gates → can explain the mechanism or required decision.
- **Relationships**: order: the stages progress in the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: The 4D loop has explicit gates
- **Core message**: Discover → permitted data and defined problem
- **Content**: Discover → permitted data and defined problem · Distill → measured evidence and answer quality · Deploy → measured SLOs; Deliver → rollback decisions

#### Slide 08 - Keep ingestion outside the request path
- **Audience move**: Uncertain about keep ingestion outside the request path → can explain the mechanism or required decision.
- **Relationships**: order: the stages progress in the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: Keep ingestion outside the request path
- **Core message**: Register → parse → chunk → redact → Atlas
- **Content**: Register → parse → chunk → redact → Atlas · Question → scoped retrieval → context → generation · Answer → validation → API → staff interface

#### Slide 09 - Use the existing layer boundaries
- **Audience move**: Uncertain about use the existing layer boundaries → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Use the existing layer boundaries
- **Core message**: chains/ owns pure LangChain runnables.
- **Content**: chains/ owns pure LangChain runnables. · database/ owns MongoDB client and retrieval setup. · services/ coordinates; api/ validates; ui/ renders.

#### Slide 10 - A thin route delegates to the service
- **Audience move**: Uncertain about a thin route delegates to the service → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: A thin route delegates to the service
- **Core message**: Dependency injection supplies settings; the service owns the workflow.
- **Content**: Dependency injection supplies settings; the service owns the workflow. Source excerpt: @router.post("/answer") / async def answer( /     request: RetrieveRequest, /     background: BackgroundTasks, /     settings: Annotated[Settings, Depends(get_settings)], / ) -> AnswerResponse: /     try: /         response = await answer_policy(request, settings) /         if should_sample(response, settings): /             background.add_task(score_sampled_answer, request, response, settings) /         return response /     except (

#### Slide 11 - The use-case contract is intentionally narrow
- **Audience move**: Uncertain about the use-case contract is intentionally narrow → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The use-case contract is intentionally narrow
- **Core message**: Explain synthetic policy clauses for staff.
- **Content**: Explain synthetic policy clauses for staff. · Ask for missing scope or abstain when unsupported. · Never approve credit or execute account actions.

#### Slide 12 - A trusted source needs an identity
- **Audience move**: Uncertain about a trusted source needs an identity → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: A trusted source needs an identity
- **Core message**: Register: doc_id, version, effective dates and hash.
- **Content**: Register: doc_id, version, effective dates and hash. · Authority and amendment relationships affect retrieval. · A changed file must fail source verification.

#### Slide 13 - Practical 1 / inspect the baseline
- **Audience move**: Uncertain about practical 1 / inspect the baseline → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 1 / inspect the baseline
- **Core message**: Run: uv run --no-sync pytest -q tests
- **Content**: Run: uv run --no-sync pytest -q tests · Locate the missing architecture-document failure. · Record it separately; do not delete or skip the test.

#### Slide 14 - Practical 2 / tamper with a safe copy
- **Audience move**: Uncertain about practical 2 / tamper with a safe copy → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 2 / tamper with a safe copy
- **Core message**: Run: python -m training.session1.tamper
- **Content**: Run: python -m training.session1.tamper · Predict which document hash will fail. · Expected: 8 originals verify; changed PDF is refused.

#### Slide 15 - Practical 3 / inspect the gate contract
- **Audience move**: Uncertain about practical 3 / inspect the gate contract → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 3 / inspect the gate contract
- **Core message**: Run: python -m training.session1.check_gates app/evaluation/gates.json
- **Content**: Run: python -m training.session1.check_gates app/evaluation/gates.json · Change a copied faithfulness minimum to 1.5. · Expected: validation rejects a value outside [0, 1].

#### Slide 16 - Thresholds are typed data
- **Audience move**: Uncertain about thresholds are typed data → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Thresholds are typed data
- **Core message**: Status distinguishes placeholder numbers from owner-confirmed targets.
- **Content**: Status distinguishes placeholder numbers from owner-confirmed targets. Source excerpt: class Gates(BaseModel): /     model_config = ConfigDict(extra="forbid") /  /     # "placeholder" values are course examples that the owner has not yet confirmed. /     status: Literal["placeholder", "confirmed"] /     faithfulness_min: float = Fraction /     answer_relevancy_min: float = Fraction /     context_precision_min: float = Fraction /     context_recall_min: float = Fraction /     judge_correctness_min: float = Fraction /     judge_groundedness_min: float = Fraction /     status_match_rate_min: float = Fraction

#### Slide 17 - Data permission is a release dependency
- **Audience move**: Uncertain about data permission is a release dependency → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Data permission is a release dependency
- **Core message**: Identify who owns and may access the source.
- **Content**: Identify who owns and may access the source. · Decide whether content may leave for embeddings or generation. · Set freshness and retention before using real documents.

#### Slide 18 - Security begins before embeddings
- **Audience move**: Uncertain about security begins before embeddings → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Security begins before embeddings
- **Core message**: Remove detected identifiers before sending text out.
- **Content**: Remove detected identifiers before sending text out. · Apply metadata scope to retrieval, including dates. · Keep secrets in approved environment configuration.

#### Slide 19 - Proposed targets need a rationale
- **Audience move**: Uncertain about proposed targets need a rationale → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: Proposed targets need a rationale
- **Core message**: Quality: source-grounded answers and correct status.
- **Content**: Quality: source-grounded answers and correct status. · Operations: latency, error rate and priced cost. · Safety: a measured rollback signal and named owner.

#### Slide 20 - Exit gate / are we ready to experiment?
- **Audience move**: Uncertain about exit gate / are we ready to experiment? → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: gate page, with the dominant teaching task as focal point.
- **Title**: Exit gate / are we ready to experiment?
- **Core message**: Hand in the manifest and data-access decision.
- **Content**: Hand in the manifest and data-access decision. · Name source owner, restrictions and must-abstain cases. · Keep unresolved approvals visible in the release file.

#### Slide 21 - Check your understanding
- **Audience move**: Uncertain about check your understanding → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Check your understanding
- **Core message**: Does a SHA-256 match prove that a policy is correct?
- **Content**: Does a SHA-256 match prove that a policy is correct? · Can a healthy API answer from the wrong clause? · Which artifacts must be restored together?

#### Slide 22 - Next / prove retrieval before generation
- **Audience move**: Uncertain about next / prove retrieval before generation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: ending page, with the dominant teaching task as focal point.
- **Title**: Next / prove retrieval before generation
- **Core message**: Read app/chains/chunking.py.
- **Content**: Read app/chains/chunking.py. · Bring a table question and an effective-date trap. · Carry the manifest into Session 2.

## X. Speaker Notes Requirements
- **Generation**: enabled
Explain visible claims, practical commands, expected outcomes, sources and limitations.
