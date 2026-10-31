<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_S5_aligned_20261023 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_S5_aligned_20261023 |
| Canvas Format | PPT 16:9, 1280 × 720 |
| Page Count | 40 |
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

#### Slide 01 - Deliver
- **Audience move**: Uncertain about deliver → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: cover page, with the dominant teaching task as focal point.
- **Title**: Deliver
- **Core message**: Observability, human review and rollback
- **Content**: Observability, human review and rollback · Session 5 of 5 · 3 hours · source-aligned workshop

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

#### Slide 04 - Showcase / a complaint becomes a test
- **Audience move**: Uncertain about showcase / a complaint becomes a test → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Showcase / a complaint becomes a test
- **Core message**: A staff member flags an unhelpful answer.
- **Content**: A staff member flags an unhelpful answer. · A reviewer checks sources and accepts the signal. · A separate curated answer becomes a golden case.

#### Slide 05 - Run the reviewed-feedback demonstration
- **Audience move**: Uncertain about run the reviewed-feedback demonstration → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Run the reviewed-feedback demonstration
- **Core message**: python -m training.showcase --session 5
- **Content**: python -m training.showcase --session 5 · No token: 401; pending: 409; curated export: 200. · Validate JSONL, keep the review, rehearse recovery.

#### Slide 06 - Orchestration and Application Logic
- **Audience move**: Uncertain about orchestration and application logic → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: Orchestration and Application Logic
- **Core message**: Educative lesson 14
- **Content**: Educative lesson 14 · Concept → worked example → NexaAssist application

#### Slide 07 - Follow-up questions change retrieval requirements
- **Audience move**: Uncertain about follow-up questions change retrieval requirements → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Follow-up questions change retrieval requirements
- **Core message**: A query such as “Does that fee apply earlier?” lacks scope alone.
- **Content**: A query such as “Does that fee apply earlier?” lacks scope alone. · Conversation history can resolve the subject and date. · Memory adds privacy, latency and correctness obligations.

#### Slide 08 - Keep API workers stateless; store conversation state
- **Audience move**: Uncertain about keep api workers stateless; store conversation state → can explain the mechanism or required decision.
- **Relationships**: link: labelled dependencies between the stated units
- **Composition**: diagram page, with the dominant teaching task as focal point.
- **Title**: Keep API workers stateless; store conversation state
- **Core message**: Request: Session + user scope
- **Content**: Request: Session + user scope · Load history: Authorized durable turns · Rewrite: Standalone search query · Retrieve / answer: Generate, validate, persist

#### Slide 09 - A sliding window is a budget approximation
- **Audience move**: Uncertain about a sliding window is a budget approximation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: A sliding window is a budget approximation
- **Core message**: Load a bounded recent history instead of all turns.
- **Content**: Load a bounded recent history instead of all turns. · Message count is simple but ignores varying token length. · Reserve tokens for instructions, evidence and output.

#### Slide 10 - Rewriting must preserve the user’s meaning
- **Audience move**: Uncertain about rewriting must preserve the user’s meaning → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Rewriting must preserve the user’s meaning
- **Core message**: Resolve references using only authorized recent history.
- **Content**: Resolve references using only authorized recent history. · Keep original question and rewritten search query separate. · Validate output; time out or fall back when rewriting fails.

#### Slide 11 - New state needs multi-turn evaluation
- **Audience move**: Uncertain about new state needs multi-turn evaluation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: New state needs multi-turn evaluation
- **Core message**: Capture history, current input and expected source.
- **Content**: Capture history, current input and expected source. · Test incorrect rewrites, missing history and cross-user access. · Recheck retrieval and answer quality before rollout.

#### Slide 12 - Practical / model the memory contract offline
- **Audience move**: Uncertain about practical / model the memory contract offline → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical / model the memory contract offline
- **Core message**: Run: python -m training.session5.memory_design
- **Content**: Run: python -m training.session5.memory_design · Inspect a bounded fixture and a failed-rewrite fallback. · Explain why the simulation is not a durable session service.

#### Slide 13 - Quality, Human-in-the-Loop, and Governance Systems
- **Audience move**: Uncertain about quality, human-in-the-loop, and governance systems → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: Quality, Human-in-the-Loop, and Governance Systems
- **Core message**: Educative lesson 15
- **Content**: Educative lesson 15 · Concept → worked example → NexaAssist application

#### Slide 14 - Use two kinds of observation
- **Audience move**: Uncertain about use two kinds of observation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: Use two kinds of observation
- **Core message**: System health: latency, failures, tokens and priced cost.
- **Content**: System health: latency, failures, tokens and priced cost. · Answer quality: grounding, relevance and correct scope. · A healthy system can still produce a harmful answer.

#### Slide 15 - Trace one answer to its artifacts
- **Audience move**: Uncertain about trace one answer to its artifacts → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Trace one answer to its artifacts
- **Core message**: Prompt ID, version and content fingerprint.
- **Content**: Prompt ID, version and content fingerprint. · Chat/embedding model and retrieval configuration. · Evidence references and optional Datadog span ID.

#### Slide 16 - Sampled judging is an explicit choice
- **Audience move**: Uncertain about sampled judging is an explicit choice → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Sampled judging is an explicit choice
- **Core message**: The sample rate is configurable; zero disables sampled judging.
- **Content**: The sample rate is configurable; zero disables sampled judging. Source excerpt: def should_sample(answer: AnswerResponse, settings: Settings) -> bool: /     """Only answered responses carry claims to check; abstentions are skipped.""" /     return answer.status == "answered" and random.random() < settings.live_eval_sample_rate /  /  / async def score_sampled_answer( /     request: RetrieveRequest, answer: AnswerResponse, settings: Settings / ) -> None: /     """Background reference-free judging of live traffic; failures are logged, never raised. / 

#### Slide 17 - Know what sampled faithfulness measures
- **Audience move**: Uncertain about know what sampled faithfulness measures → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Know what sampled faithfulness measures
- **Core message**: Sampling answered requests adds model cost.
- **Content**: Sampling answered requests adds model cost. · The current judge uses cited quotes as its context. · This is a grounding proxy with limited observation.

#### Slide 18 - Quality is maintained in three layers
- **Audience move**: Uncertain about quality is maintained in three layers → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Quality is maintained in three layers
- **Core message**: Automated gates catch known regressions.
- **Content**: Automated gates catch known regressions. · Human review assesses context and newly observed failures. · Governance controls changes to meaning and risk.

#### Slide 19 - The review queue needs the exact interaction
- **Audience move**: Uncertain about the review queue needs the exact interaction → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The review queue needs the exact interaction
- **Core message**: Link the input, evidence references, output and versions.
- **Content**: Link the input, evidence references, output and versions. · Prioritize explicit complaints and representative samples. · Review the source before accepting the correction.

#### Slide 20 - Human feedback is a signal
- **Audience move**: Uncertain about human feedback is a signal → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Human feedback is a signal
- **Core message**: A thumbs-down may mean wrong scope or poor wording.
- **Content**: A thumbs-down may mean wrong scope or poor wording. · Review source, context and answer before accepting it. · Never turn raw feedback directly into a golden answer.

#### Slide 21 - The human review loop has owners
- **Audience move**: Uncertain about the human review loop has owners → can explain the mechanism or required decision.
- **Relationships**: order: stages follow the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: The human review loop has owners
- **Core message**: Signal → triage → source-supported correction
- **Content**: Signal → triage → source-supported correction · Review → proposed golden case → regression replay · Approved fix → measured release → observation

#### Slide 22 - Practical 2 / inspect feedback behavior
- **Audience move**: Uncertain about practical 2 / inspect feedback behavior → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 2 / inspect feedback behavior
- **Core message**: Run feedback, sampling and comparison tests.
- **Content**: Run feedback, sampling and comparison tests. · Follow reviewer authentication and review transitions. · Explain why accepted feedback still needs a verified reference.

#### Slide 23 - Export a reviewed regression case
- **Audience move**: Uncertain about export a reviewed regression case → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Export a reviewed regression case
- **Core message**: Run: python -m training.session5.feedback_loop
- **Content**: Run: python -m training.session5.feedback_loop · Accepted review + curated answer → golden case. · Keep the review bundle beside the validated JSONL.

#### Slide 24 - Governance follows the change’s meaning
- **Audience move**: Uncertain about governance follows the change’s meaning → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Governance follows the change’s meaning
- **Core message**: Engineering reviews code and operational behavior.
- **Content**: Engineering reviews code and operational behavior. · A domain expert reviews policy meaning and golden answers. · The designated owner approves real data use and risk.

#### Slide 25 - Watch both semantic and operational drift
- **Audience move**: Uncertain about watch both semantic and operational drift → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Watch both semantic and operational drift
- **Core message**: Topic shifts can expose gaps in the golden set.
- **Content**: Topic shifts can expose gaps in the golden set. · Policy updates can invalidate otherwise stable answers. · Judge changes can move scores without application changes.

#### Slide 26 - Practical 1 / run an incident safely
- **Audience move**: Uncertain about practical 1 / run an incident safely → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 1 / run an incident safely
- **Core message**: Run: python -m training.session5.incident
- **Content**: Run: python -m training.session5.incident · No traffic → every required SLO is not_measured. · Scenario failures: p95 latency and hallucination proxy.

#### Slide 27 - A regression needs a comparable baseline
- **Audience move**: Uncertain about a regression needs a comparable baseline → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: A regression needs a comparable baseline
- **Core message**: Scenario faithfulness changes from 0.95 to 0.70.
- **Content**: Scenario faithfulness changes from 0.95 to 0.70. · Delta −0.25 exceeds the placeholder tolerance. · Investigate cases and configuration before interpreting it.

#### Slide 28 - Exercise / remove an observation
- **Audience move**: Uncertain about exercise / remove an observation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Exercise / remove an observation
- **Core message**: Set sampled_count=0 and the proxy to None.
- **Content**: Set sampled_count=0 and the proxy to None. · Predict not_measured rather than pass. · Explain what evidence is needed before clearing an incident.

#### Slide 29 - Practical 3 / rehearse rollback
- **Audience move**: Uncertain about practical 3 / rehearse rollback → can explain the mechanism or required decision.
- **Relationships**: order: stages follow the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: Practical 3 / rehearse rollback
- **Core message**: Hold candidate → preserve evidence → restore known-good set
- **Content**: Hold candidate → preserve evidence → restore known-good set · Replay failing and golden cases → measure representative traffic · Document owner decision and follow-up regression case

#### Slide 30 - A new index name is not a data snapshot
- **Audience move**: Uncertain about a new index name is not a data snapshot → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: A new index name is not a data snapshot
- **Core message**: Ingestion mutates the configured chunk collection.
- **Content**: Ingestion mutates the configured chunk collection. · Parent sections must also match the candidate corpus. · Blue/green requires isolated compatible stores and a tested switch.

#### Slide 31 - What belongs in the release file
- **Audience move**: Uncertain about what belongs in the release file → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: What belongs in the release file
- **Core message**: Prompt/model/retrieval identities and dataset hash.
- **Content**: Prompt/model/retrieval identities and dataset hash. · Offline quality report and representative SLO evidence. · Approver, rollback owner, known limits and incident links.

#### Slide 32 - Future Directions in LLMOps
- **Audience move**: Uncertain about future directions in llmops → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: Future Directions in LLMOps
- **Core message**: Educative lesson 16
- **Content**: Educative lesson 16 · Concept → worked example → NexaAssist application

#### Slide 33 - Agents add actions and new failure modes
- **Audience move**: Uncertain about agents add actions and new failure modes → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Agents add actions and new failure modes
- **Core message**: Tool access needs permissions and an allowlist.
- **Content**: Tool access needs permissions and an allowlist. · Loops need iteration, time and cost bounds. · Side effects need isolation, audit and recovery.

#### Slide 34 - Bound an agent before granting actions
- **Audience move**: Uncertain about bound an agent before granting actions → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Bound an agent before granting actions
- **Core message**: Limit steps, time, token spend and tool permissions.
- **Content**: Limit steps, time, token spend and tool permissions. · Isolate side effects and preserve an audit trail. · Evaluate tool choice, arguments and recovery behavior.

#### Slide 35 - Multimodal inputs expand the ingestion boundary
- **Audience move**: Uncertain about multimodal inputs expand the ingestion boundary → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Multimodal inputs expand the ingestion boundary
- **Core message**: OCR or vision extraction introduces interpretation errors.
- **Content**: OCR or vision extraction introduces interpretation errors. · Images and audio can carry identifiers or instructions. · Queue expensive processing and evaluate the extracted evidence.

#### Slide 36 - Model distillation introduces a training lifecycle
- **Audience move**: Uncertain about model distillation introduces a training lifecycle → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Model distillation introduces a training lifecycle
- **Core message**: Curate teacher traces into reviewed training data.
- **Content**: Curate teacher traces into reviewed training data. · Evaluate a smaller student on quality and safety cases. · Version the dataset, model and rollback decision.

#### Slide 37 - Edge execution shifts the operational trade-off
- **Audience move**: Uncertain about edge execution shifts the operational trade-off → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Edge execution shifts the operational trade-off
- **Core message**: Local inference can reduce network disclosure and round trips.
- **Content**: Local inference can reduce network disclosure and round trips. · Device differences affect performance and version consistency. · Telemetry, updates and recovery need a new design.

#### Slide 38 - The lifecycle survives a change in capabilities
- **Audience move**: Uncertain about the lifecycle survives a change in capabilities → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The lifecycle survives a change in capabilities
- **Core message**: Define the new permission and data boundaries.
- **Content**: Define the new permission and data boundaries. · Evaluate before deployment and version the artifacts. · Observe failures and close the reviewed feedback loop.

#### Slide 39 - Final gate / defend the decision
- **Audience move**: Uncertain about final gate / defend the decision → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: gate page, with the dominant teaching task as focal point.
- **Title**: Final gate / defend the decision
- **Core message**: Submit manifest, retrieval experiment and golden review.
- **Content**: Submit manifest, retrieval experiment and golden review. · Attach quality/SLO reports and an incident write-up. · State release, hold or unmeasured with supporting evidence.

#### Slide 40 - Operate the loop, not just the endpoint
- **Audience move**: Uncertain about operate the loop, not just the endpoint → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: ending page, with the dominant teaching task as focal point.
- **Title**: Operate the loop, not just the endpoint
- **Core message**: Version the artifacts that change answers.
- **Content**: Version the artifacts that change answers. · Measure evidence, meaning and operations separately. · Turn reviewed failures into durable regression cases.

## X. Speaker Notes Requirements
- **Generation**: enabled
Explain visible claims, practical commands, expected outcomes, sources and limitations.
