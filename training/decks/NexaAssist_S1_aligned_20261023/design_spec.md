<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_S1_aligned_20261023 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_S1_aligned_20261023 |
| Canvas Format | PPT 16:9, 1280 × 720 |
| Page Count | 16 |
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
- **Content**: NexaAssist / LLMOps engineering workshop · Session 1 of 5 · 16-slide teaching edition

#### Slide 02 - LLMOps manages behavior under real constraints
- **Audience move**: Uncertain about llmops manages behavior under real constraints → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: LLMOps manages behavior under real constraints
- **Core message**: Correctness and safety are part of the product.
- **Content**: Correctness and safety are part of the product. · Latency shapes whether people can use the service. · Token consumption determines variable cost.

#### Slide 03 - From models to operated applications
- **Audience move**: Uncertain about from models to operated applications → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: From models to operated applications
- **Core message**: AI → ML → GenAI → LLMs: a scope relationship.
- **Content**: AI → ML → GenAI → LLMs: a scope relationship. · The application owns data, prompts and integration. · Hosted-model behavior still needs measured evidence.

#### Slide 04 - What changes from MLOps to LLMOps
- **Audience move**: Uncertain about what changes from mlops to llmops → can explain the mechanism or required decision.
- **Relationships**: compare: four independent MLOps-to-LLMOps changes; each cell maps before to after
- **Composition**: diagram page, with the dominant teaching task as focal point.
- **Title**: What changes from MLOps to LLMOps
- **Core message**: Data: Features → documents + vectors
- **Content**: Data: Features → documents + vectors · Tuning: Parameters → prompts + retrieval · Artifacts: Weights → coupled runtime assets · Evaluation: Labels → semantic criteria

#### Slide 05 - Four phases, four decisions
- **Audience move**: Uncertain about four phases, four decisions → can explain the mechanism or required decision.
- **Relationships**: link: labelled dependencies between the stated units
- **Composition**: diagram page, with the dominant teaching task as focal point.
- **Title**: Four phases, four decisions
- **Core message**: Discover: Problem + permitted data
- **Content**: Discover: Problem + permitted data · Distill: Prove retrieval and generation · Deploy: Validate the serving envelope · Deliver: Observe and improve

#### Slide 06 - C4 / system context
- **Audience move**: Uncertain about c4 / system context → can explain the mechanism or required decision.
- **Relationships**: link: labelled directed dependencies; boundary and element types distinguish C4 levels where named
- **Composition**: architecture page, with the dominant teaching task as focal point.
- **Title**: C4 / system context
- **Core message**: People ask, review and maintain policy knowledge.
- **Content**: People ask, review and maintain policy knowledge. · NexaAssist depends on models, Atlas and optional telemetry.

#### Slide 07 - C4 / containers and ownership
- **Audience move**: Uncertain about c4 / containers and ownership → can explain the mechanism or required decision.
- **Relationships**: link: labelled directed dependencies; boundary and element types distinguish C4 levels where named
- **Composition**: architecture page, with the dominant teaching task as focal point.
- **Title**: C4 / containers and ownership
- **Core message**: Streamlit renders; FastAPI coordinates the answer path.
- **Content**: Streamlit renders; FastAPI coordinates the answer path. · The ingestion CLI maintains Atlas knowledge collections.

#### Slide 08 - Two paths share one knowledge contract
- **Audience move**: Uncertain about two paths share one knowledge contract → can explain the mechanism or required decision.
- **Relationships**: link: labelled directed dependencies; boundary and element types distinguish C4 levels where named
- **Composition**: architecture page, with the dominant teaching task as focal point.
- **Title**: Two paths share one knowledge contract
- **Core message**: Offline: prepare and publish trusted searchable evidence.
- **Content**: Offline: prepare and publish trusted searchable evidence. · Online: retrieve, generate and validate a scoped answer.

#### Slide 09 - One answer / request and failure flow
- **Audience move**: Uncertain about one answer / request and failure flow → can explain the mechanism or required decision.
- **Relationships**: link: labelled directed dependencies; boundary and element types distinguish C4 levels where named
- **Composition**: architecture page, with the dominant teaching task as focal point.
- **Title**: One answer / request and failure flow
- **Core message**: Validate → retrieve scoped evidence → build the prompt.
- **Content**: Validate → retrieve scoped evidence → build the prompt. · Generate → check output → return answer or abstention.

#### Slide 10 - Freshness, permission and traceability are separate
- **Audience move**: Uncertain about freshness, permission and traceability are separate → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Freshness, permission and traceability are separate
- **Core message**: A fresh document can still be unauthorized.
- **Content**: A fresh document can still be unauthorized. · A permitted document can still be obsolete. · An answer needs a recoverable source identity.

#### Slide 11 - Code / pure chain, strict draft
- **Audience move**: Uncertain about code / pure chain, strict draft → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Code / pure chain, strict draft
- **Core message**: The same LCEL chain is callable from the service and evaluation.
- **Content**: The same LCEL chain is callable from the service and evaluation. Source excerpt:     generation = ANSWER_PROMPT | llm.with_structured_output( /         AnswerDraft, method="json_schema", strict=True /     )

#### Slide 12 - Scope the policy assistant before release
- **Audience move**: Uncertain about scope the policy assistant before release → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Scope the policy assistant before release
- **Core message**: Staff receive cited explanations or safe non-answers.
- **Content**: Staff receive cited explanations or safe non-answers. · Credit decisions and account actions are outside scope. · The manifest names permitted sources and unresolved owners.

#### Slide 13 - Code / reject changed source bytes
- **Audience move**: Uncertain about code / reject changed source bytes → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Code / reject changed source bytes
- **Core message**: A source must match the register before parsing or embedding.
- **Content**: A source must match the register before parsing or embedding. Source excerpt: def _verify_source(path: Path, entry: dict[str, Any]) -> str: /     """Refuse a file whose bytes differ from the register's recorded sha256.""" /     digest = hashlib.sha256(path.read_bytes()).hexdigest() /     if digest != entry["sha256"]: /         raise ValueError(f"{entry['doc_id']}: file sha256 does not match the document register") /     return str(path)

#### Slide 14 - Practical / prove the source boundary
- **Audience move**: Uncertain about practical / prove the source boundary → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical / prove the source boundary
- **Core message**: python -m training.showcase --session 1
- **Content**: python -m training.showcase --session 1 · Observe: 8 original documents verify. · Tampered copy: hash mismatch; ingestion is refused.

#### Slide 15 - The release file is more than application code
- **Audience move**: Uncertain about the release file is more than application code → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The release file is more than application code
- **Core message**: Record prompt, model, corpus and embedding identities.
- **Content**: Record prompt, model, corpus and embedding identities. · Attach golden results and measured operating evidence. · Keep placeholder targets and missing approvals visible.

#### Slide 16 - Session 1 / architecture exit gate
- **Audience move**: Uncertain about session 1 / architecture exit gate → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: gate page, with the dominant teaching task as focal point.
- **Title**: Session 1 / architecture exit gate
- **Core message**: Trace one staff question across the real layers.
- **Content**: Trace one staff question across the real layers. · Explain which source or output failure stops an answer. · Submit the scope manifest and source-verification evidence.

## X. Speaker Notes Requirements
- **Generation**: enabled
Explain visible claims, practical commands, expected outcomes, sources and limitations.
