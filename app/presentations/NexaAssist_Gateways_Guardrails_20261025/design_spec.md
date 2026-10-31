<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_Gateways_Guardrails_20261025 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_Gateways_Guardrails_20261025 |
| Canvas Format | PPT 16:9, 1280 × 720 |
| Page Count | 22 |
| Primary Language | en |
| Target Audience | Enterprise LLMOps engineers and Python developers with REST familiarity |
| Communication Intent | Teach gateway and guardrail mechanisms through actual code and controlled requests |
| Desired Audience Outcome | Follow the request path, select the right control and identify its evidence |
| Core Message / Ask / Action | Route for reliability; validate policy boundaries; distinguish execution from quality |
| Delivery Context | Instructor-led 45–60 minute workshop with optional live drills |
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
| Created Date | 2026-10-25 |

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

#### Slide 01 - Route reliably. Validate every answer.
- **Audience move**: Uncertain about the mechanism → can explain llm gateways, routing, security and guardrails
- **Relationships**: order: concept precedes code, request and evidence
- **Composition**: cover expression serving its specific code or boundary question.
- **Title**: Route reliably. Validate every answer.
- **Core message**: LLM gateways, routing, security and guardrails
- **Content**: Concept → code → request → evidence; LiteLLM · Ollama / OpenAI · Guardrails AI. Source anchors: app/gateway/litellm.yaml:2, app/security/guardrails_service.py:20

#### Slide 02 - Choose the mechanism for the failure
- **Audience move**: Uncertain about the mechanism → can explain availability, capacity, repetition and safety require different controls.
- **Relationships**: contrast: four distinct operating conditions map to different mechanisms
- **Composition**: decision expression serving its specific code or boundary question.
- **Title**: Choose the mechanism for the failure
- **Core message**: Availability, capacity, repetition and safety require different controls.
- **Content**: Provider failure / Retry + fallback; Concurrent demand / Independent replicas; Repeated generation / Exact scoped cache; Unsafe input / output / Application checks + Guardrails. Source anchors: app/gateway/litellm.yaml:23, app/gateway/litellm_balanced.yaml:2, app/gateway/litellm_cache.yaml:31, app/chains/guardrails.py:9

#### Slide 03 - The gateway is inside the policy boundary
- **Audience move**: Uncertain about the mechanism → can explain policy users enter through fastapi; direct gateway calls bypass application rails.
- **Relationships**: link: API calls gateway, pgvector and validator; gateway calls selected providers
- **Composition**: architecture expression serving its specific code or boundary question.
- **Title**: The gateway is inside the policy boundary
- **Core message**: Policy users enter through FastAPI; direct gateway calls bypass application rails.
- **Content**: FastAPI → input checks → scoped retrieval; Gateway selects chat and embedding routes; Application checks every generated or cached draft. Source anchors: app/compose.yaml:70, app/chains/llm.py:14, app/chains/guardrails.py:9

#### Slide 04 - Follow the request in execution order
- **Audience move**: Uncertain about the mechanism → can explain retrieval must supply usable evidence before generation starts.
- **Relationships**: order: six request stages execute from HTTP validation to response
- **Composition**: requestflow expression serving its specific code or boundary question.
- **Title**: Follow the request in execution order
- **Core message**: Retrieval must supply usable evidence before generation starts.
- **Content**: 1 / Validate HTTP request; 2 / Reject injection; redact PII; 3 / Embed query; search pgvector; 4 / Assemble and escape evidence; 5 / Route chat; generate draft; 6 / Validate output; return response. Source anchors: app/api/answer.py:45, app/services/answer.py:36, app/chains/retrieval.py:35, app/chains/answer.py:169

#### Slide 05 - Open these functions as the request runs
- **Audience move**: Uncertain about the mechanism → can explain show one entry point and its purpose at each boundary.
- **Relationships**: order: handler delegates to service, input rail, retrieval and answer chain
- **Composition**: codemap expression serving its specific code or boundary question.
- **Title**: Open these functions as the request runs
- **Core message**: Show one entry point and its purpose at each boundary.
- **Content**: HTTP handler / api / Calls the answer service; Input + accounting / service / Scrubs query; tracks latency/tokens; Shared input rail / scrub / Rejects overrides; replaces PII; Retrieval / retrieval / Searches scoped policy evidence; Generation + checks / draft / Validates the returned draft. Source anchors: app/api/answer.py:45, app/services/answer.py:36, app/services/retrieval.py:23, app/chains/retrieval.py:35, app/chains/answer.py:169

#### Slide 06 - Use stable aliases for four model routes
- **Audience move**: Uncertain about the mechanism → can explain the app selects aliases; litellm resolves provider deployments.
- **Relationships**: membership: chat aliases belong to generation; embedding aliases belong to retrieval
- **Composition**: routes expression serving its specific code or boundary question.
- **Title**: Use stable aliases for four model routes
- **Core message**: The app selects aliases; LiteLLM resolves provider deployments.
- **Content**: nexa-chat / Ollama qwen3.5:9b-mlx / Primary generation; nexa-chat-openai / OPENAI_LITELLM_CHAT_MODEL / Approved cloud chat; nexa-embed-local / qwen3-embedding:0.6b / Local query / document vectors; nexa-embed-openai / text-embedding-3-small / Separate cloud vector corpus. Source anchors: app/gateway/litellm.yaml:2, app/chains/llm.py:14, app/chains/embeddings.py:44, app/compose.yaml:70

#### Slide 07 - Fail over chat; keep retrieval available
- **Audience move**: Uncertain about the mechanism → can explain a provider failure can trigger backup chat; missing evidence cannot.
- **Relationships**: order: primary chat failure leads to configured backup attempt; evidence retrieval remains separate
- **Composition**: fallback expression serving its specific code or boundary question.
- **Title**: Fail over chat; keep retrieval available
- **Core message**: A provider failure can trigger backup chat; missing evidence cannot.
- **Content**: One configured retry; one fallback depth.; Router timeout setting: 30 seconds.; SDK retries and citation repair add more time.. Source anchors: app/gateway/litellm.yaml:23, app/chains/llm.py:14

#### Slide 08 - Fault drill: break only the chat address
- **Audience move**: Uncertain about the mechanism → can explain keep embeddings healthy so the class observes chat failover.
- **Relationships**: none
- **Composition**: code expression serving its specific code or boundary question.
- **Title**: Fault drill: break only the chat address
- **Core message**: Keep embeddings healthy so the class observes chat failover.
- **Content**: Verify the chosen fault port is unused.; Ask the known home-loan question.; Inspect gateway/provider evidence, then restore.. Source anchors: app/gateway/litellm.yaml:23, app/compose.yaml:70

#### Slide 09 - Balance across independent deployments
- **Audience move**: Uncertain about the mechanism → can explain two aliases to one daemon do not create independent capacity.
- **Relationships**: link: one chat alias distributes calls to two independent deployments
- **Composition**: balance expression serving its specific code or boundary question.
- **Title**: Balance across independent deployments
- **Core message**: Two aliases to one daemon do not create independent capacity.
- **Content**: Shared alias: nexa-chat-balanced; Separate deployment IDs and replica URLs; Simple shuffle is not strict alternation. Source anchors: app/gateway/litellm_balanced.yaml:2

#### Slide 10 - Cache matching generation, not the request
- **Audience move**: Uncertain about the mechanism → can explain a cache hit still passes current application output checks.
- **Relationships**: order: scoped request checks cache; hit reuses draft; both paths rejoin output validation
- **Composition**: cache expression serving its specific code or boundary question.
- **Title**: Cache matching generation, not the request
- **Core message**: A cache hit still passes current application output checks.
- **Content**: Exact chat cache; five-minute TTL.; Scope includes corpus, model and prompt identity.; Retrieval and Ragas evaluation still execute.. Source anchors: app/gateway/litellm_cache.yaml:31, app/chains/llm.py:14, app/chains/answer.py:169

#### Slide 11 - Keep embedding families in separate corpora
- **Audience move**: Uncertain about the mechanism → can explain document vectors and query vectors must share a compatible profile.
- **Relationships**: contrast: local and cloud vector spaces require distinct compatible corpora
- **Composition**: embeddings expression serving its specific code or boundary question.
- **Title**: Keep embedding families in separate corpora
- **Core message**: Document vectors and query vectors must share a compatible profile.
- **Content**: LOCAL QWEN / qwen3-embedding:0.6b / 1024 dimensions / Qwen namespaces; OPENAI / text-embedding-3-small / 1536 dimensions / Separate OpenAI namespaces. Source anchors: app/chains/embeddings.py:44, app/gateway/openai-embeddings.env.example:2

#### Slide 12 - Guard the input, draft and source claims
- **Audience move**: Uncertain about the mechanism → can explain the gateway controls access to models; the app controls policy behavior.
- **Relationships**: order: input checks precede draft validation and source attribution checks
- **Composition**: securitycover expression serving its specific code or boundary question.
- **Title**: Guard the input, draft and source claims
- **Core message**: The gateway controls access to models; the app controls policy behavior.
- **Content**: INPUT  →  reject overrides; redact supported PII; DRAFT  →  enforce schema; reject detected PII; SOURCE  →  verify markers and exact quotes. Source anchors: app/security/input_policy.py:26, app/models/answer.py:18, app/chains/answer.py:184

#### Slide 13 - Redact PII before the provider sees it
- **Audience move**: Uncertain about the mechanism → can explain supported identifiers become typed placeholders before retrieval/generation.
- **Relationships**: contrast: supported identifiers in input are replaced; detected output PII causes abstention
- **Composition**: pii expression serving its specific code or boundary question.
- **Title**: Redact PII before the provider sees it
- **Core message**: Supported identifiers become typed placeholders before retrieval/generation.
- **Content**: Email · PAN · supported phone / Aadhaar patterns; Input: redact before embedding and generation.; Output: detected PII discards the draft.. Source anchors: app/services/retrieval.py:23, app/chains/redaction.py:15, app/chains/ingestion.py:64

#### Slide 14 - Reject explicit instruction overrides early
- **Audience move**: Uncertain about the mechanism → can explain known explicit overrides return http 400 before retrieval or generation.
- **Relationships**: order: question enters normalization, pattern match and rejection or sanitized continuation
- **Composition**: injection expression serving its specific code or boundary question.
- **Title**: Reject explicit instruction overrides early
- **Core message**: Known explicit overrides return HTTP 400 before retrieval or generation.
- **Content**: NFKC normalization + case-folding for detection; Explicit English override/extraction patterns; Escaped data and system instructions add boundaries. Source anchors: app/security/input_policy.py:26, app/main.py:31, app/chains/answer.py:147

#### Slide 15 - Treat schema validity as a contract
- **Audience move**: Uncertain about the mechanism → can explain a structurally valid draft can still be wrong or unsupported.
- **Relationships**: none
- **Composition**: code expression serving its specific code or boundary question.
- **Title**: Treat schema validity as a contract
- **Core message**: A structurally valid draft can still be wrong or unsupported.
- **Content**: Strict AnswerDraft forbids unknown fields.; Evidence IDs must be positive.; Source membership is checked after the schema.. Source anchors: app/models/answer.py:18, app/chains/answer.py:169, app/security/guardrails_service.py:20

#### Slide 16 - The validator returns a decision, not an answer
- **Audience move**: Uncertain about the mechanism → can explain http 200 can carry validation_passed:false.
- **Relationships**: order: strict original JSON check precedes fresh Guard parse and returned decision
- **Composition**: validator expression serving its specific code or boundary question.
- **Title**: The validator returns a decision, not an answer
- **Core message**: HTTP 200 can carry validation_passed:false.
- **Content**: Original JSON / Pydantic rejects invalid input; Fresh local Guard / Schema parsed; no LLM reasks; Decision / true or false returned to application. Source anchors: app/security/guardrails_service.py:20, app/chains/guardrails.py:9

#### Slide 17 - Verify quotes before returning an answer
- **Audience move**: Uncertain about the mechanism → can explain one citation repair is allowed; exhaustion returns safe abstention.
- **Relationships**: order: validate markers and quotes; failed candidate repairs once then passes or abstains
- **Composition**: citation expression serving its specific code or boundary question.
- **Title**: Verify quotes before returning an answer
- **Core message**: One citation repair is allowed; exhaustion returns safe abstention.
- **Content**: Inline markers must match evidence IDs.; Every quote must occur in the selected source.; Same retrieval is reused for the repair.. Source anchors: app/chains/answer.py:184, app/chains/context.py:30

#### Slide 18 - Fail closed at a configured validator
- **Audience move**: Uncertain about the mechanism → can explain an unavailable validator is not permission to bypass validation.
- **Relationships**: contrast: failures at distinct boundaries produce different safe outcomes
- **Composition**: outage expression serving its specific code or boundary question.
- **Title**: Fail closed at a configured validator
- **Core message**: An unavailable validator is not permission to bypass validation.
- **Content**: No usable evidence / Abstain before generation; Detected output PII / Discard draft; abstain; Validator false / unavailable / Sanitized service error if reached. Source anchors: app/chains/guardrails.py:9, app/chains/answer.py:169

#### Slide 19 - Trace the security calls in this order
- **Audience move**: Uncertain about the mechanism → can explain each check has a narrow purpose; none replaces the next boundary.
- **Relationships**: order: input policy precedes generation, sidecar validation and source checks
- **Composition**: codemap expression serving its specific code or boundary question.
- **Title**: Trace the security calls in this order
- **Core message**: Each check has a narrow purpose; none replaces the next boundary.
- **Content**: Input orchestration / scrub / Injection check, then supported PII; Override detection / inject / Normalize and reject explicit patterns; Output schema / schema / Allowed status, fields and evidence shape; External validation / guard / Bounded call; false/outage fails closed; Source validation / citation / Markers, IDs and exact quotes. Source anchors: app/services/retrieval.py:23, app/security/input_policy.py:26, app/models/answer.py:18, app/chains/guardrails.py:9, app/chains/answer.py:184

#### Slide 20 - Run one question through four demonstrations
- **Audience move**: Uncertain about the mechanism → can explain establish the baseline, change one condition, then restore.
- **Relationships**: order: baseline retrieval precedes answer, injection and validator demonstrations
- **Composition**: lab expression serving its specific code or boundary question.
- **Title**: Run one question through four demonstrations
- **Core message**: Establish the baseline, change one condition, then restore.
- **Content**: 8001 /retrieve / Prove evidence exists; 8001 /answer / Inspect status and citation; 8001 /answer + override / Observe verified HTTP 400; 8101 /validate / Compare true and false decisions. Source anchors: app/api/answer.py:45, app/security/guardrails_service.py:20

#### Slide 21 - Separate observed results from configured behavior
- **Audience move**: Uncertain about the mechanism → can explain a successful retrieval does not guarantee every generation succeeds.
- **Relationships**: contrast: successful baseline answer and separate evaluated abstention are distinct measured requests
- **Composition**: results expression serving its specific code or boundary question.
- **Title**: Separate observed results from configured behavior
- **Core message**: A successful retrieval does not guarantee every generation succeeds.
- **Content**: Baseline: five hits; answered ₹7,50,00,000 with a citation.; Separate evaluated request: abstained after generation.; Recall 1.0; precision ≈0.20; answer metrics unavailable.. Source anchors: app/core/phoenix.py:14, app/evaluation/phoenix_export.py:36

#### Slide 22 - Choose the control; show the evidence
- **Audience move**: Uncertain about the mechanism → can explain route for reliability. validate for policy boundaries. measure both.
- **Relationships**: contrast: operating condition determines control and required evidence
- **Composition**: ending expression serving its specific code or boundary question.
- **Title**: Choose the control; show the evidence
- **Core message**: Route for reliability. Validate for policy boundaries. Measure both.
- **Content**: Unavailable provider? / Retry / fallback; More concurrent work? / Independent capacity; Same scoped generation? / Exact cache; Personal identifiers? / Redact supported PII; Override or invalid draft? / Reject / validate; Unsupported claims? / Inspect sources and quality. Source anchors: app/gateway/litellm.yaml:23, app/gateway/litellm_cache.yaml:31, app/security/input_policy.py:26, app/chains/answer.py:184

## X. Speaker Notes Requirements
- **Generation**: enabled
- **Filename**: match each SVG filename under notes/
- **Content**: Ground narration in final visible content; add exact source paths, full drill/restoration commands and measured-versus-expected qualifiers. No invented results.
- **Total duration**: 45–60 minutes including demonstrations
- **Notes style**: Conversational, technical and interactive
- **Presentation purpose**: Teach mechanism selection and request/code literacy for gateways and guardrails.
