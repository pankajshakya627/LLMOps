<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_S2_20261023 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_S2_20261023 |
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
| Accent | #2463A6 | accent |

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

#### Slide 01 - Distill I
- **Audience move**: Uncertain about distill i → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: cover page, with the dominant teaching task as focal point.
- **Title**: Distill I
- **Core message**: Data foundations, embeddings and retrieval
- **Content**: Data foundations, embeddings and retrieval · Session 2 of 5 · 3 hours · hands-on NexaAssist

#### Slide 02 - The evidence path is the product
- **Audience move**: Uncertain about the evidence path is the product → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The evidence path is the product
- **Core message**: Preserve policy structure and tables.
- **Content**: Preserve policy structure and tables. · Retrieve the right version for the requested date. · Measure expected clauses before generating answers.

#### Slide 03 - Today’s workshop route
- **Audience move**: Uncertain about today’s workshop route → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Today’s workshop route
- **Core message**: 25 min data/retrieval concepts + 20 min walkthrough
- **Content**: 25 min data/retrieval concepts + 20 min walkthrough · 90 min pair experiments, including a 10 min break · 25 min retrieval gate review + 20 min recap

#### Slide 04 - One ingestion pipeline, separate duties
- **Audience move**: Uncertain about one ingestion pipeline, separate duties → can explain the mechanism or required decision.
- **Relationships**: order: the stages progress in the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: One ingestion pipeline, separate duties
- **Core message**: Parse structure → chunk clauses → mask identifiers
- **Content**: Parse structure → chunk clauses → mask identifiers · Enrich metadata → compare checksums · Embed changed children → upsert parents and chunks

#### Slide 05 - Three forms of document noise
- **Audience move**: Uncertain about three forms of document noise → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Three forms of document noise
- **Core message**: Artifact noise: control characters and extraction debris.
- **Content**: Artifact noise: control characters and extraction debris. · Layout noise: repeated page headers and split tables. · Semantic noise: obsolete or contradictory policy text.

#### Slide 06 - Chunk around clauses, then size
- **Audience move**: Uncertain about chunk around clauses, then size → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Chunk around clauses, then size
- **Core message**: Inspect how the clause-aware splitter handles oversized sections.
- **Content**: Inspect how the clause-aware splitter handles oversized sections. Source excerpt: def chunk_by_clause(elements: list[Element], max_characters: int, overlap: int) -> list[Chunk]: /     """Hybrid chunking: structure rules first, size rules second. /  /     Structure: one chunk per numbered clause ("6.2 Processing fee. ..."). A table or /     continuation line stays with the clause that introduces it, and a table is never split. /     Size: only a clause longer than `max_characters` is split. Its tables become their own /     chunks and its narrative is split at sentence boundaries with `overlap` characters /     repeated. Text before section 1 is section 0, "Front matter". /     """ /     section_number, section = 0, "Front matter" /     clauses: list[_Clause] = [_Clause(section_number, section, None, None)] /     for element in elements:

#### Slide 07 - Practical 1 / observe real PDF chunks
- **Audience move**: Uncertain about practical 1 / observe real pdf chunks → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 1 / observe real PDF chunks
- **Core message**: Run: python -m training.session2.chunks
- **Content**: Run: python -m training.session2.chunks · Compare maximum sizes 300, 1200 and 5000. · Expected counts: 40, 32 and 32; tables remain visible.

#### Slide 08 - Small search units; readable context
- **Audience move**: Uncertain about small search units; readable context → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: Small search units; readable context
- **Core message**: Child: precise clause text with metadata.
- **Content**: Child: precise clause text with metadata. · Parent: the surrounding section used for generation. · Budgeting must preserve required amendment evidence.

#### Slide 09 - Idempotency is an observable property
- **Audience move**: Uncertain about idempotency is an observable property → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Idempotency is an observable property
- **Core message**: Unchanged text and embedding schema → no re-embedding.
- **Content**: Unchanged text and embedding schema → no re-embedding. · Model or dimensions change → regenerate vectors. · Stable clause identity avoids renumbering unrelated data.

#### Slide 10 - Practical 2 / repeat ingestion offline
- **Audience move**: Uncertain about practical 2 / repeat ingestion offline → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 2 / repeat ingestion offline
- **Core message**: Run: python -m training.session2.ingest_twin
- **Content**: Run: python -m training.session2.ingest_twin · Predict embedded counts before each run. · Expected: 32 → 0 → 32 → 0.

#### Slide 11 - PII controls belong before embedding
- **Audience move**: Uncertain about pii controls belong before embedding → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: PII controls belong before embedding
- **Core message**: Run: python -m training.session2.redact
- **Content**: Run: python -m training.session2.redact · Inspect EMAIL, PHONE, PAN and AADHAAR placeholders. · Verify loan amounts remain readable.

#### Slide 12 - Embeddings are part of the schema
- **Audience move**: Uncertain about embeddings are part of the schema → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Embeddings are part of the schema
- **Core message**: Configured model and dimensions must match indexed vectors.
- **Content**: Configured model and dimensions must match indexed vectors. · The Atlas index points to the embedding field. · A dimension mismatch is a compatibility failure.

#### Slide 13 - Use the official MongoDB integration
- **Audience move**: Uncertain about use the official mongodb integration → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Use the official MongoDB integration
- **Core message**: Collection, embedding and index_name are passed explicitly; index creation is manual.
- **Content**: Collection, embedding and index_name are passed explicitly; index creation is manual. Source excerpt:     return MongoDBAtlasVectorSearch( /         collection=_database(settings)[settings.mongodb_collection], /         embedding=embedding, /         index_name=settings.vector_index_name, /         text_key="text", /         embedding_key="embedding", /         relevance_score_fn="cosine", /         auto_create_index=False, /     ) /  / 

#### Slide 14 - The index definition is already documented
- **Audience move**: Uncertain about the index definition is already documented → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: The index definition is already documented
- **Core message**: Open app/database/indexes.md.
- **Content**: Open app/database/indexes.md. · Use the exact JSON matching configured dimensions. · Check every metadata filter field in the live index.

#### Slide 15 - Dates and permissions constrain evidence
- **Audience move**: Uncertain about dates and permissions constrain evidence → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Dates and permissions constrain evidence
- **Core message**: Run: python -m training.session2.asof
- **Content**: Run: python -m training.session2.asof · Compare 2026-06-30 with 2026-07-01. · Expected: the July circular enters scope on its effective date.

#### Slide 16 - Dense, hybrid and reranked retrieval
- **Audience move**: Uncertain about dense, hybrid and reranked retrieval → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: split page, with the dominant teaching task as focal point.
- **Title**: Dense, hybrid and reranked retrieval
- **Core message**: Dense search matches embedding similarity.
- **Content**: Dense search matches embedding similarity. · Hybrid adds lexical evidence; reranking changes order. · Evaluate each configuration on the same cases.

#### Slide 17 - Recall and rank answer different questions
- **Audience move**: Uncertain about recall and rank answer different questions → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Recall and rank answer different questions
- **Core message**: Recall@k: fraction of required references found.
- **Content**: Recall@k: fraction of required references found. · MRR: reciprocal rank of the first expected reference. · A fee question can require more than one clause.

#### Slide 18 - Practical 3 / score a retrieval miss
- **Audience move**: Uncertain about practical 3 / score a retrieval miss → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical 3 / score a retrieval miss
- **Core message**: Run: python -m training.session2.recall
- **Content**: Run: python -m training.session2.recall · Compare k=1, k=3 and k=5. · Explain the two-clause fee case and linked amendment.

#### Slide 19 - Optional live / ingest then evaluate
- **Audience move**: Uncertain about optional live / ingest then evaluate → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Optional live / ingest then evaluate
- **Core message**: Needs approved Atlas access and model credentials.
- **Content**: Needs approved Atlas access and model credentials. · Run ingestion twice; then retrieval_eval --k 5. · Record configuration, missing clauses and the gate result.

#### Slide 20 - Treat re-indexing as a release
- **Audience move**: Uncertain about treat re-indexing as a release → can explain the mechanism or required decision.
- **Relationships**: order: the stages progress in the written sequence
- **Composition**: flow page, with the dominant teaching task as focal point.
- **Title**: Treat re-indexing as a release
- **Core message**: Build a separate compatible candidate data store.
- **Content**: Build a separate compatible candidate data store. · Evaluate candidate retrieval and answer quality. · Switch the full configuration only after review.

#### Slide 21 - Exit gate / evidence before eloquence
- **Audience move**: Uncertain about exit gate / evidence before eloquence → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: gate page, with the dominant teaching task as focal point.
- **Title**: Exit gate / evidence before eloquence
- **Core message**: Submit chunk experiment and checksum explanation.
- **Content**: Submit chunk experiment and checksum explanation. · Report recall/MRR and categorize every missing reference. · Live scores remain unmeasured until the live lab runs.

#### Slide 22 - Next / control what generation may claim
- **Audience move**: Uncertain about next / control what generation may claim → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: ending page, with the dominant teaching task as focal point.
- **Title**: Next / control what generation may claim
- **Core message**: Read app/chains/prompts/answer.py.
- **Content**: Read app/chains/prompts/answer.py. · Bring one unsupported question and one scope ambiguity. · Keep the same retrieval cases for Session 3.

## X. Speaker Notes Requirements
- **Generation**: enabled
Explain visible claims, practical commands, expected outcomes, sources and limitations.
