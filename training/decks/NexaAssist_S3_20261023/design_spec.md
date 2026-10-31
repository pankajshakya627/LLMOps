<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_S3_20261023 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_S3_20261023 |
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
| Accent | #7954A3 | accent |

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

#### Slide 01 - Distill II
- **Audience move**: Uncertain about distill ii → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: cover page, with the dominant teaching task as focal point.
- **Title**: Distill II
- **Core message**: Prompts, generation and evaluation gates
- **Content**: Prompts, generation and evaluation gates · Session 3 of 5 · 3 hours · offline draft replay

#### Slide 02 - What you will produce
- **Audience move**: Uncertain about what you will produce → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: What you will produce
- **Core message**: A grounded answer replay and a failure diagnosis.
- **Content**: A grounded answer replay and a failure diagnosis. · Three proposed golden cases with a review memo. · A documented quality gate decision.

#### Slide 03 - The three-hour plan
- **Audience move**: Uncertain about the three-hour plan → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The three-hour plan
- **Core message**: 25 min prompts/evaluation + 20 min code walkthrough
- **Content**: 25 min prompts/evaluation + 20 min code walkthrough · 90 min pair labs, including a 10 min break · 25 min gate decisions + 20 min review

#### Slide 04 - A prompt has three responsibilities
- **Audience move**: Uncertain about a prompt has three responsibilities → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: A prompt has three responsibilities
- **Core message**: Role: what the assistant is authorized to do.
- **Content**: Role: what the assistant is authorized to do. · Evidence boundary: which supplied text supports claims. · Output contract: schema, status and citations.

#### Slide 05 - The prompt is a tracked artifact
- **Audience move**: Uncertain about the prompt is a tracked artifact → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: The prompt is a tracked artifact
- **Core message**: Prompt ID, version and fingerprint travel with the answer provenance.
- **Content**: Prompt ID, version and fingerprint travel with the answer provenance. Source excerpt: ANSWER_PROMPT_ID = "nexaassist-policy-answer" / ANSWER_PROMPT_VERSION = "1.0.0" / ANSWER_PROMPT = ChatPromptTemplate.from_messages( /     [ /         ( /             "system", /             """ / You are NexaAssist, an assistant that explains synthetic NexaBank policies to staff. /  / Resolve product/date/rate ambiguity before judging whether evidence is sufficient. / If the user's requested policy-lookup date differs from as_of, ask for scope

#### Slide 06 - Make a prompt change reviewable
- **Audience move**: Uncertain about make a prompt change reviewable → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Make a prompt change reviewable
- **Core message**: Run tests/test_prompts.py before changing wording.
- **Content**: Run tests/test_prompts.py before changing wording. · A wording change requires a version and pin update. · Then replay cases; a new hash proves identity, not quality.

#### Slide 07 - LCEL composes prompt and strict model output
- **Audience move**: Uncertain about lcel composes prompt and strict model output → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: LCEL composes prompt and strict model output
- **Core message**: The chain requests AnswerDraft with strict JSON-schema output.
- **Content**: The chain requests AnswerDraft with strict JSON-schema output. Source excerpt:     generation = ANSWER_PROMPT | llm.with_structured_output( /         AnswerDraft, method="json_schema", strict=True /     ) / 

#### Slide 08 - Status is part of the API contract
- **Audience move**: Uncertain about status is part of the api contract → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Status is part of the API contract
- **Core message**: Distinguish answered, insufficient_evidence and needs_clarification.
- **Content**: Distinguish answered, insufficient_evidence and needs_clarification. Source excerpt: class AnswerDraft(BaseModel): /     """Model output; source identities are resolved by application code.""" /  /     model_config = ConfigDict(extra="forbid") /  /     status: Literal["answered", "insufficient_evidence", "needs_clarification"] /     answer: str = Field(min_length=1) /     evidence: list[EvidenceQuote] / 

#### Slide 09 - The answer path fails closed
- **Audience move**: Uncertain about the answer path fails closed → can explain the mechanism or required decision.
- **Relationships**: order: the stages progress in the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: The answer path fails closed
- **Core message**: Retrieve and budget evidence → generate draft
- **Content**: Retrieve and budget evidence → generate draft · Check output PII → check IDs, markers and exact quotes · Return supported response, repair once or abstain

#### Slide 10 - What exact quotes do and do not establish
- **Audience move**: Uncertain about what exact quotes do and do not establish → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: What exact quotes do and do not establish
- **Core message**: An exact quote proves those bytes were supplied.
- **Content**: An exact quote proves those bytes were supplied. · It does not prove the claim follows from the quote. · Semantic evaluation must still check grounding and scope.

#### Slide 11 - Practical 1 / replay three model drafts
- **Audience move**: Uncertain about practical 1 / replay three model drafts → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 1 / replay three model drafts
- **Core message**: Run: python -m training.session3.answers
- **Content**: Run: python -m training.session3.answers · Valid → answered; invented quote → abstention. · Output PII → abstention with no leaked citation.

#### Slide 12 - Exercise / break evidence identity
- **Audience move**: Uncertain about exercise / break evidence identity → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Exercise / break evidence identity
- **Core message**: In a lab copy, change the evidence ID to 99.
- **Content**: In a lab copy, change the evidence ID to 99. · Predict the marker/ID mismatch and repair count. · Then explain a wrong answer with a valid quote.

#### Slide 13 - Use metrics that match the failure
- **Audience move**: Uncertain about use metrics that match the failure → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Use metrics that match the failure
- **Core message**: Context precision: relevance of retrieved material.
- **Content**: Context precision: relevance of retrieved material. · Context recall: coverage of reference information. · Faithfulness and answer relevance: grounding and fit.

#### Slide 14 - Golden cases need human verification
- **Audience move**: Uncertain about golden cases need human verification → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Golden cases need human verification
- **Core message**: Input includes question, date and product scope.
- **Content**: Input includes question, date and product scope. · Expected output/status and source references are explicit. · Put verifier and review rationale in a companion memo.

#### Slide 15 - Practical 2 / classify the fault
- **Audience move**: Uncertain about practical 2 / classify the fault → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 2 / classify the fault
- **Core message**: Run: python -m training.session3.gates
- **Content**: Run: python -m training.session3.gates · Missing required context → retrieval_error. · Complete context, unsupported response → generation_error.

#### Slide 16 - A gate names the metric that failed
- **Audience move**: Uncertain about a gate names the metric that failed → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: A gate names the metric that failed
- **Core message**: Per-metric means and failed cases make the decision actionable.
- **Content**: Per-metric means and failed cases make the decision actionable. Source excerpt: def gate_failures(report: dict[str, Any], gates: Gates) -> list[dict[str, Any]]: /     """Offline quality gate: aggregate means plus the cases that fell short.""" /     records = report["records"] /     failures: list[dict[str, Any]] = [] /  /     def check(metric: str, value: float, minimum: float) -> None: /         if value < minimum: /             failures.append({"metric": metric, "value": round(value, 4), "minimum": minimum}) /  /     for name, value in report["ragas"]["means"].items(): /         check(name, value, getattr(gates, f"{name}_min")) /     for key in ("correctness", "groundedness"):

#### Slide 17 - Practical 3 / propose three golden cases
- **Audience move**: Uncertain about practical 3 / propose three golden cases → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 3 / propose three golden cases
- **Core message**: Copy the JSONL dataset into /tmp.
- **Content**: Copy the JSONL dataset into /tmp. · Add answer, abstention and clarification examples. · Validate with load_golden; review the actual source clauses.

#### Slide 18 - Offline does not always mean no provider
- **Audience move**: Uncertain about offline does not always mean no provider → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: Offline does not always mean no provider
- **Core message**: Class labs use fakes and need no credentials.
- **Content**: Class labs use fakes and need no credentials. · A pre-release golden evaluation can call real models. · Live evaluation needs approved access, cost and data.

#### Slide 19 - Compare like with like
- **Audience move**: Uncertain about compare like with like → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Compare like with like
- **Core message**: Keep case set, retrieval configuration and judge aligned.
- **Content**: Keep case set, retrieval configuration and judge aligned. · Save the baseline before writing the next report. · Inspect per-metric deltas and newly failing cases.

#### Slide 20 - Optional live / run and compare
- **Audience move**: Uncertain about optional live / run and compare → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Optional live / run and compare
- **Core message**: Run app.evaluation.run --limit 3 with approved .env.
- **Content**: Run app.evaluation.run --limit 3 with approved .env. · Preserve old and new reports under distinct paths. · Run app.evaluation.compare OLD.json NEW.json.

#### Slide 21 - Exit gate / quality with an explanation
- **Audience move**: Uncertain about exit gate / quality with an explanation → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: gate page, with the dominant teaching task as focal point.
- **Title**: Exit gate / quality with an explanation
- **Core message**: Three valid cases and human review memo.
- **Content**: Three valid cases and human review memo. · A named failure type for every failing example. · Thresholds met or a documented release hold.

#### Slide 22 - Next / make failure safe to serve
- **Audience move**: Uncertain about next / make failure safe to serve → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: ending page, with the dominant teaching task as focal point.
- **Title**: Next / make failure safe to serve
- **Core message**: Keep generation behind the service layer.
- **Content**: Keep generation behind the service layer. · Bring one invalid input and one dependency outage. · Session 4 will measure the API failure contract.

## X. Speaker Notes Requirements
- **Generation**: enabled
Explain visible claims, practical commands, expected outcomes, sources and limitations.
