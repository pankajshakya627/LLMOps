<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_S4_aligned_20261023 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_S4_aligned_20261023 |
| Canvas Format | PPT 16:9, 1280 × 720 |
| Page Count | 41 |
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
| Accent | #B86416 | accent |

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

#### Slide 01 - Deploy
- **Audience move**: Uncertain about deploy → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: cover page, with the dominant teaching task as focal point.
- **Title**: Deploy
- **Core message**: Secure serving, reliability and cost
- **Content**: Secure serving, reliability and cost · Session 4 of 5 · 3 hours · source-aligned workshop

#### Slide 02 - Outcomes you can demonstrate
- **Audience move**: Uncertain about outcomes you can demonstrate → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Outcomes you can demonstrate
- **Core message**: Predict 422, 429 and 503 responses.
- **Content**: Predict 422, 429 and 503 responses. · Trace input, output and resource controls. · Explain why an empty metrics window cannot pass an SLO.

#### Slide 03 - Three hours to harden the boundary
- **Audience move**: Uncertain about three hours to harden the boundary → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Three hours to harden the boundary
- **Core message**: 25 min serving/security + 20 min walkthrough
- **Content**: 25 min serving/security + 20 min walkthrough · 90 min labs, including a 10 min break · 25 min SLO review + 20 min recap

#### Slide 04 - Showcase / the service fails safely
- **Audience move**: Uncertain about showcase / the service fails safely → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Showcase / the service fails safely
- **Core message**: Provider failure → private details stay private.
- **Content**: Provider failure → private details stay private. · Repeated calls → the configured quota applies. · Database failure → readiness reports unavailable.

#### Slide 05 - Run the serving-failure demonstration
- **Audience move**: Uncertain about run the serving-failure demonstration → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Run the serving-failure demonstration
- **Core message**: python -m training.showcase --session 4
- **Content**: python -m training.showcase --session 4 · Provider failures then quota: [503, 503, 429]. · Invalid input: 422; failed readiness: 503.

#### Slide 06 - Security, Compliance, and Responsible Operation in LLMOps
- **Audience move**: Uncertain about security, compliance, and responsible operation in llmops → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: Security, Compliance, and Responsible Operation in LLMOps
- **Core message**: Educative lesson 11
- **Content**: Educative lesson 11 · Concept → worked example → NexaAssist application

#### Slide 07 - Grounded output can still be unsafe
- **Audience move**: Uncertain about grounded output can still be unsafe → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Grounded output can still be unsafe
- **Core message**: A source may contain private information.
- **Content**: A source may contain private information. · A user may request an unauthorized disclosure. · A safe-looking request can consume excessive resources.

#### Slide 08 - Recognize direct and indirect injection
- **Audience move**: Uncertain about recognize direct and indirect injection → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Recognize direct and indirect injection
- **Core message**: Direct: the user tries to override the assistant’s rules.
- **Content**: Direct: the user tries to override the assistant’s rules. · Indirect: retrieved material contains hostile instructions. · Defend at data, prompt, authorization and output boundaries.

#### Slide 09 - Risk names are stable; numbering is versioned
- **Audience move**: Uncertain about risk names are stable; numbering is versioned → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Risk names are stable; numbering is versioned
- **Core message**: The lesson uses older OWASP LLM01 / LLM04 / LLM06 labels.
- **Content**: The lesson uses older OWASP LLM01 / LLM04 / LLM06 labels. · OWASP 2025 maps disclosure to LLM02 and consumption to LLM10. · Record the list version when naming a risk.

#### Slide 10 - Layer the controls around generation
- **Audience move**: Uncertain about layer the controls around generation → can explain the mechanism or required decision.
- **Relationships**: order: stages follow the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: Layer the controls around generation
- **Core message**: Before: validate, quota and redact the query.
- **Content**: Before: validate, quota and redact the query. · During: bound context and output tokens. · After: detect PII and verify cited quotes.

#### Slide 11 - Reuse the query PII rail
- **Audience move**: Uncertain about reuse the query pii rail → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Reuse the query PII rail
- **Core message**: scrub_request runs before embeddings and generation.
- **Content**: scrub_request runs before embeddings and generation. · The same pattern engine masks corpus identifiers. · Regex misses names and addresses and can misclassify digits.

#### Slide 12 - New / block detected PII before returning
- **Audience move**: Uncertain about new / block detected pii before returning → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: New / block detected PII before returning
- **Core message**: Check answer text and evidence quotes; return the existing safe abstention.
- **Content**: Check answer text and evidence quotes; return the existing safe abstention. Source excerpt:             if any(redact(text)[1] for text in (draft.answer, *(e.quote for e in draft.evidence))): /                 logger.warning("answer_output_pii_blocked") /                 return response / 

#### Slide 13 - Preserve citation integrity when blocking
- **Audience move**: Uncertain about preserve citation integrity when blocking → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Preserve citation integrity when blocking
- **Core message**: Never rewrite a quote and still call it exact.
- **Content**: Never rewrite a quote and still call it exact. · On a detected identifier, discard the draft and citations. · Log only the event; never log the sensitive text.

#### Slide 14 - Practical 2 / inspect security tests
- **Audience move**: Uncertain about practical 2 / inspect security tests → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 2 / inspect security tests
- **Core message**: Run input_rail, output_cap and rate_limit tests.
- **Content**: Run input_rail, output_cap and rate_limit tests. · Run test_readiness_timeout.py and the answer replay. · Explain both protected cases and known detector limits.

#### Slide 15 - Resource governance has explicit bounds
- **Audience move**: Uncertain about resource governance has explicit bounds → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Resource governance has explicit bounds
- **Core message**: Request query length is capped.
- **Content**: Request query length is capped. · CHAT_MAX_OUTPUT_TOKENS bounds answer generation. · RATE_LIMIT_PER_MINUTE is a per-process quota.

#### Slide 16 - Treat residual risk as part of the result
- **Audience move**: Uncertain about treat residual risk as part of the result → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Treat residual risk as part of the result
- **Core message**: Patterns cover selected identifiers, not all personal data.
- **Content**: Patterns cover selected identifiers, not all personal data. · Quotas are per process; proxy behavior affects client identity. · Authorization and retention still need deployment decisions.

#### Slide 17 - Inference Infrastructure: Hardware, Economics, and Latency
- **Audience move**: Uncertain about inference infrastructure: hardware, economics, and latency → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: Inference Infrastructure: Hardware, Economics, and Latency
- **Core message**: Educative lesson 12
- **Content**: Educative lesson 12 · Concept → worked example → NexaAssist application

#### Slide 18 - Split response time into useful measurements
- **Audience move**: Uncertain about split response time into useful measurements → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Split response time into useful measurements
- **Core message**: TTFT: request start until the first output token.
- **Content**: TTFT: request start until the first output token. · TPS: generation rate after output begins. · End-to-end latency also includes queues and retrieval.

#### Slide 19 - Weight memory is only the starting estimate
- **Audience move**: Uncertain about weight memory is only the starting estimate → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Weight memory is only the starting estimate
- **Core message**: Approximate decimal GB = parameter billions × bytes/parameter.
- **Content**: Approximate decimal GB = parameter billions × bytes/parameter. · Scenario: 8B × 2 bytes = 16 GB for FP16 weights. · Reserve additional memory for cache, runtime and concurrency.

#### Slide 20 - Quantization changes the weight budget
- **Audience move**: Uncertain about quantization changes the weight budget → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Quantization changes the weight budget
- **Core message**: FP16 uses roughly 2 bytes per parameter.
- **Content**: FP16 uses roughly 2 bytes per parameter. · INT8 uses roughly 1; packed INT4 roughly 0.5. · Quality, kernel support and metadata overhead still matter.

#### Slide 21 - The KV cache grows with workload shape
- **Audience move**: Uncertain about the kv cache grows with workload shape → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The KV cache grows with workload shape
- **Core message**: Longer context requires more cached attention state.
- **Content**: Longer context requires more cached attention state. · Concurrent sequences increase the live memory footprint. · A model loading successfully does not prove capacity.

#### Slide 22 - API versus self-hosting is a utilization decision
- **Audience move**: Uncertain about api versus self-hosting is a utilization decision → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: API versus self-hosting is a utilization decision
- **Core message**: API: variable token cost plus provider limits and governance.
- **Content**: API: variable token cost plus provider limits and governance. · Self-hosting: fixed capacity cost plus operating effort. · Compare representative traffic, privacy and reliability needs.

#### Slide 23 - Separate input and output prices in the estimate
- **Audience move**: Uncertain about separate input and output prices in the estimate → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Separate input and output prices in the estimate
- **Core message**: Scenario: 1,000 queries/day, 500 input + 200 output tokens.
- **Content**: Scenario: 1,000 queries/day, 500 input + 200 output tokens. · At $0.10/$0.50 per 1M: $0.15/day, $4.50/30 days. · These are scenario prices, not a current provider quote.

#### Slide 24 - Parallelism and batching solve different constraints
- **Audience move**: Uncertain about parallelism and batching solve different constraints → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Parallelism and batching solve different constraints
- **Core message**: Replicas distribute requests when a model fits per worker.
- **Content**: Replicas distribute requests when a model fits per worker. · Sharding distributes a model that needs multiple devices. · Batching trades queue delay for better resource utilization.

#### Slide 25 - Practical / calculate capacity and spend
- **Audience move**: Uncertain about practical / calculate capacity and spend → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical / calculate capacity and spend
- **Core message**: Run: python -m training.session4.capacity
- **Content**: Run: python -m training.session4.capacity · Verify weight-only estimates and scenario token costs. · Write down the missing cache, runtime and concurrency inputs.

#### Slide 26 - Measure latency, errors and priced tokens
- **Audience move**: Uncertain about measure latency, errors and priced tokens → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Measure latency, errors and priced tokens
- **Core message**: Use /metrics/answers and app.evaluation.slo_check.
- **Content**: Use /metrics/answers and app.evaluation.slo_check. · Missing traffic or prices → not_measured. · Process metrics do not establish a fleet-wide SLO.

#### Slide 27 - Streaming needs a separate contract
- **Audience move**: Uncertain about streaming needs a separate contract → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Streaming needs a separate contract
- **Core message**: Current answers are buffered and validated as a whole.
- **Content**: Current answers are buffered and validated as a whole. · Total generation time does not measure TTFT or TPS. · Streaming requires deciding when validated content may leave.

#### Slide 28 - Hosting, Serving, and Scaling LLMs in Production
- **Audience move**: Uncertain about hosting, serving, and scaling llms in production → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: section page, with the dominant teaching task as focal point.
- **Title**: Hosting, Serving, and Scaling LLMs in Production
- **Core message**: Educative lesson 13
- **Content**: Educative lesson 13 · Concept → worked example → NexaAssist application

#### Slide 29 - Async endpoints still need non-blocking internals
- **Audience move**: Uncertain about async endpoints still need non-blocking internals → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Async endpoints still need non-blocking internals
- **Core message**: Await asynchronous provider and HTTP clients.
- **Content**: Await asynchronous provider and HTTP clients. · Offload synchronous database/file work explicitly. · FastAPI does not offload every utility called inside async def.

#### Slide 30 - The API owns a strict contract
- **Audience move**: Uncertain about the api owns a strict contract → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The API owns a strict contract
- **Core message**: Pydantic rejects invalid or extra request fields.
- **Content**: Pydantic rejects invalid or extra request fields. · Depends injects settings and request controls. · Routers delegate; provider failures become safe 503s.

#### Slide 31 - Practical 1 / exercise the real API
- **Audience move**: Uncertain about practical 1 / exercise the real api → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 1 / exercise the real API
- **Core message**: Run: python -m training.session4.serving
- **Content**: Run: python -m training.session4.serving · Observe health 200, readiness 503 and invalid input 422. · Two provider failures then quota: [503, 503, 429].

#### Slide 32 - A failure should reveal enough to act
- **Audience move**: Uncertain about a failure should reveal enough to act → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: A failure should reveal enough to act
- **Core message**: 422 → repair the request.
- **Content**: 422 → repair the request. · 429 + Retry-After → respect the quota. · 503 → dependency unavailable; preserve private details.

#### Slide 33 - Dependency injection defines resource ownership
- **Audience move**: Uncertain about dependency injection defines resource ownership → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Dependency injection defines resource ownership
- **Core message**: Create or cache shared clients with clear lifecycle.
- **Content**: Create or cache shared clients with clear lifecycle. · Inject application settings and replace services in tests. · Keep domain logic callable outside HTTP routes.

#### Slide 34 - Health and readiness answer different questions
- **Audience move**: Uncertain about health and readiness answer different questions → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: Health and readiness answer different questions
- **Core message**: /health: this process can respond.
- **Content**: /health: this process can respond. · /ready: the configured database ping succeeds. · Neither endpoint proves retrieval or answer quality.

#### Slide 35 - New / put a deadline on the driver ping
- **Audience move**: Uncertain about new / put a deadline on the driver ping → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: New / put a deadline on the driver ping
- **Core message**: The two-second driver deadline applies to readiness, not ordinary retrieval.
- **Content**: The two-second driver deadline applies to readiness, not ordinary retrieval. Source excerpt: def ping_database(settings: Settings) -> None: /     """Bound the readiness probe without shortening normal query deadlines.""" /     with timeout(2): /         _database(settings).command("ping") / 

#### Slide 36 - Package the existing application
- **Audience move**: Uncertain about package the existing application → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Package the existing application
- **Core message**: Read app/Dockerfile and Dockerfile.dockerignore.
- **Content**: Read app/Dockerfile and Dockerfile.dockerignore. · Inspect locked dependencies, non-root user and probe. · Keep API secrets outside the image build context.

#### Slide 37 - Practical 3 / inspect operational tests
- **Audience move**: Uncertain about practical 3 / inspect operational tests → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 3 / inspect operational tests
- **Core message**: Run tests/test_slo.py and tests/test_telemetry.py.
- **Content**: Run tests/test_slo.py and tests/test_telemetry.py. · Map a request through FastAPI and workflow spans. · Explain why transport-only API tests omit lifespan.

#### Slide 38 - A reproducible image still needs safe deployment
- **Audience move**: Uncertain about a reproducible image still needs safe deployment → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: A reproducible image still needs safe deployment
- **Core message**: Freeze dependencies and build with an excluded-secret context.
- **Content**: Freeze dependencies and build with an excluded-secret context. · Inject secrets at runtime; do not COPY .env into images. · Review networking, readiness and rollout in the target platform.

#### Slide 39 - Cost follows measured tokens
- **Audience move**: Uncertain about cost follows measured tokens → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Cost follows measured tokens
- **Core message**: Cost = (input tokens × input price + output tokens × output price) / 1M.
- **Content**: Cost = (input tokens × input price + output tokens × output price) / 1M. · Monthly estimate = priced query cost × expected query volume. · Verify current provider prices before the live exercise.

#### Slide 40 - Exit gate / can we serve it responsibly?
- **Audience move**: Uncertain about exit gate / can we serve it responsibly? → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: gate page, with the dominant teaching task as focal point.
- **Title**: Exit gate / can we serve it responsibly?
- **Core message**: Submit API failure matrix and limitation note.
- **Content**: Submit API failure matrix and limitation note. · Define representative staging traffic and approved budgets. · Hold a live release when required SLOs are unmeasured.

#### Slide 41 - Next / detect, investigate and recover
- **Audience move**: Uncertain about next / detect, investigate and recover → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: ending page, with the dominant teaching task as focal point.
- **Title**: Next / detect, investigate and recover
- **Core message**: Carry the quality and operational evidence forward.
- **Content**: Carry the quality and operational evidence forward. · Bring one regression and one misleading feedback item. · Session 5 rehearses the operating loop.

## X. Speaker Notes Requirements
- **Generation**: enabled
Explain visible claims, practical commands, expected outcomes, sources and limitations.
