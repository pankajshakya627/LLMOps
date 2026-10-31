<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_S5_20261023 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_S5_20261023 |
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
| Accent | #AF476A | accent |

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

#### Slide 01 - Deliver
- **Audience move**: Uncertain about deliver → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: cover page, with the dominant teaching task as focal point.
- **Title**: Deliver
- **Core message**: Observability, human review and rollback
- **Content**: Observability, human review and rollback · Session 5 of 5 · 3 hours · complete the release file

#### Slide 02 - What the final release file must explain
- **Audience move**: Uncertain about what the final release file must explain → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: What the final release file must explain
- **Core message**: What changed and which artifacts produced the answer.
- **Content**: What changed and which artifacts produced the answer. · Which measured gates passed, failed or remain unknown. · Who can approve release and who can restore service.

#### Slide 03 - The last three-hour workshop
- **Audience move**: Uncertain about the last three-hour workshop → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The last three-hour workshop
- **Core message**: 25 min operating loop + 20 min trace walkthrough
- **Content**: 25 min operating loop + 20 min trace walkthrough · 90 min labs, including a 10 min break · 25 min incident review + 20 min final debrief

#### Slide 04 - Use two kinds of observation
- **Audience move**: Uncertain about use two kinds of observation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: Use two kinds of observation
- **Core message**: System health: latency, failures, tokens and priced cost.
- **Content**: System health: latency, failures, tokens and priced cost. · Answer quality: grounding, relevance and correct scope. · A healthy system can still produce a harmful answer.

#### Slide 05 - Trace one answer to its artifacts
- **Audience move**: Uncertain about trace one answer to its artifacts → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Trace one answer to its artifacts
- **Core message**: Prompt ID, version and content fingerprint.
- **Content**: Prompt ID, version and content fingerprint. · Chat/embedding model and retrieval configuration. · Evidence references and optional Datadog span ID.

#### Slide 06 - Sampled judging is an explicit choice
- **Audience move**: Uncertain about sampled judging is an explicit choice → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Sampled judging is an explicit choice
- **Core message**: The sample rate is configurable; zero disables sampled judging.
- **Content**: The sample rate is configurable; zero disables sampled judging. Source excerpt: def should_sample(answer: AnswerResponse, settings: Settings) -> bool: /     """Only answered responses carry claims to check; abstentions are skipped.""" /     return answer.status == "answered" and random.random() < settings.live_eval_sample_rate /  /  / async def score_sampled_answer( /     request: RetrieveRequest, answer: AnswerResponse, settings: Settings / ) -> None: /     """Background reference-free judging of live traffic; failures are logged, never raised. / 

#### Slide 07 - Know what sampled faithfulness measures
- **Audience move**: Uncertain about know what sampled faithfulness measures → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Know what sampled faithfulness measures
- **Core message**: Sampling answered requests adds model cost.
- **Content**: Sampling answered requests adds model cost. · The current judge uses cited quotes as its context. · This is a grounding proxy with limited observation.

#### Slide 08 - Practical 1 / run an incident safely
- **Audience move**: Uncertain about practical 1 / run an incident safely → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 1 / run an incident safely
- **Core message**: Run: python -m training.session5.incident
- **Content**: Run: python -m training.session5.incident · No traffic → every required SLO is not_measured. · Scenario failures: p95 latency and hallucination proxy.

#### Slide 09 - A regression needs a comparable baseline
- **Audience move**: Uncertain about a regression needs a comparable baseline → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: A regression needs a comparable baseline
- **Core message**: Scenario faithfulness changes from 0.95 to 0.70.
- **Content**: Scenario faithfulness changes from 0.95 to 0.70. · Delta −0.25 exceeds the placeholder tolerance. · Investigate cases and configuration before interpreting it.

#### Slide 10 - Exercise / remove an observation
- **Audience move**: Uncertain about exercise / remove an observation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Exercise / remove an observation
- **Core message**: Set sampled_count=0 and the proxy to None.
- **Content**: Set sampled_count=0 and the proxy to None. · Predict not_measured rather than pass. · Explain what evidence is needed before clearing an incident.

#### Slide 11 - Human feedback is a signal
- **Audience move**: Uncertain about human feedback is a signal → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Human feedback is a signal
- **Core message**: A thumbs-down may mean wrong scope or poor wording.
- **Content**: A thumbs-down may mean wrong scope or poor wording. · Review source, context and answer before accepting it. · Never turn raw feedback directly into a golden answer.

#### Slide 12 - The human review loop has owners
- **Audience move**: Uncertain about the human review loop has owners → can explain the mechanism or required decision.
- **Relationships**: order: the stages progress in the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: The human review loop has owners
- **Core message**: Signal → triage → source-supported correction
- **Content**: Signal → triage → source-supported correction · Review → proposed golden case → regression replay · Approved fix → measured release → observation

#### Slide 13 - Practical 2 / inspect feedback behavior
- **Audience move**: Uncertain about practical 2 / inspect feedback behavior → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 2 / inspect feedback behavior
- **Core message**: Run feedback, sampling and comparison tests.
- **Content**: Run feedback, sampling and comparison tests. · Follow reviewer authentication and review transitions. · Explain why accepted feedback still needs a verified reference.

#### Slide 14 - Promote a correction manually
- **Audience move**: Uncertain about promote a correction manually → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Promote a correction manually
- **Core message**: Copy a golden case and verify the policy clause.
- **Content**: Copy a golden case and verify the policy clause. · Write expected status and answer; validate load_golden. · Keep reviewer, feedback reference and rationale in a memo.

#### Slide 15 - Governance follows the change’s meaning
- **Audience move**: Uncertain about governance follows the change’s meaning → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Governance follows the change’s meaning
- **Core message**: Engineering reviews code and operational behavior.
- **Content**: Engineering reviews code and operational behavior. · A domain expert reviews policy meaning and golden answers. · The designated owner approves real data use and risk.

#### Slide 16 - Practical 3 / rehearse rollback
- **Audience move**: Uncertain about practical 3 / rehearse rollback → can explain the mechanism or required decision.
- **Relationships**: order: the stages progress in the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: Practical 3 / rehearse rollback
- **Core message**: Hold candidate → preserve evidence → restore known-good set
- **Content**: Hold candidate → preserve evidence → restore known-good set · Replay failing and golden cases → measure representative traffic · Document owner decision and follow-up regression case

#### Slide 17 - A new index name is not a data snapshot
- **Audience move**: Uncertain about a new index name is not a data snapshot → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: A new index name is not a data snapshot
- **Core message**: Ingestion mutates the configured chunk collection.
- **Content**: Ingestion mutates the configured chunk collection. · Parent sections must also match the candidate corpus. · Blue/green requires isolated compatible stores and a tested switch.

#### Slide 18 - What belongs in the release file
- **Audience move**: Uncertain about what belongs in the release file → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: What belongs in the release file
- **Core message**: Prompt/model/retrieval identities and dataset hash.
- **Content**: Prompt/model/retrieval identities and dataset hash. · Offline quality report and representative SLO evidence. · Approver, rollback owner, known limits and incident links.

#### Slide 19 - Agents add actions and new failure modes
- **Audience move**: Uncertain about agents add actions and new failure modes → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Agents add actions and new failure modes
- **Core message**: Tool access needs permissions and an allowlist.
- **Content**: Tool access needs permissions and an allowlist. · Loops need iteration, time and cost bounds. · Side effects need isolation, audit and recovery.

#### Slide 20 - Multimodality and smaller models need evidence
- **Audience move**: Uncertain about multimodality and smaller models need evidence → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Multimodality and smaller models need evidence
- **Core message**: New input types expand ingestion and privacy work.
- **Content**: New input types expand ingestion and privacy work. · Distillation adds a versioned training-data lifecycle. · Add capability only with a concrete use case and evaluation.

#### Slide 21 - Final gate / defend the decision
- **Audience move**: Uncertain about final gate / defend the decision → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: gate page, with the dominant teaching task as focal point.
- **Title**: Final gate / defend the decision
- **Core message**: Submit manifest, retrieval experiment and golden review.
- **Content**: Submit manifest, retrieval experiment and golden review. · Attach quality/SLO reports and an incident write-up. · State release, hold or unmeasured with supporting evidence.

#### Slide 22 - Operate the loop, not just the endpoint
- **Audience move**: Uncertain about operate the loop, not just the endpoint → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: ending page, with the dominant teaching task as focal point.
- **Title**: Operate the loop, not just the endpoint
- **Core message**: Version the artifacts that change answers.
- **Content**: Version the artifacts that change answers. · Measure evidence, meaning and operations separately. · Turn reviewed failures into durable regression cases.

## X. Speaker Notes Requirements
- **Generation**: enabled
Explain visible claims, practical commands, expected outcomes, sources and limitations.
