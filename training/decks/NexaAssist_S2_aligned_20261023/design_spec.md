<!-- ppt-master-schema: design-spec/v1 -->
# NexaAssist_S2_aligned_20261023 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | NexaAssist_S2_aligned_20261023 |
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
| Accent | #2463A6 | accent |

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

#### Slide 01 - Distill I
- **Audience move**: Uncertain about distill i → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: cover page, with the dominant teaching task as focal point.
- **Title**: Distill I
- **Core message**: Data foundations, embeddings and retrieval
- **Content**: Data foundations, embeddings and retrieval · Session 2 of 5 · 16-slide teaching edition

#### Slide 02 - Documents carry meaning through structure
- **Audience move**: Uncertain about documents carry meaning through structure → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Documents carry meaning through structure
- **Core message**: Tables, headers and code blocks define useful boundaries.
- **Content**: Tables, headers and code blocks define useful boundaries. · Extraction can mix unrelated columns and page furniture. · Inspect representative parsed output before embedding.

#### Slide 03 - Ingestion / prepare evidence before embedding
- **Audience move**: Uncertain about ingestion / prepare evidence before embedding → can explain the mechanism or required decision.
- **Relationships**: link: labelled directed dependencies; boundary and element types distinguish C4 levels where named
- **Composition**: architecture page, with the dominant teaching task as focal point.
- **Title**: Ingestion / prepare evidence before embedding
- **Core message**: Verify → parse → chunk → redact and fingerprint.
- **Content**: Verify → parse → chunk → redact and fingerprint. · Embed changed children; publish children and parents.

#### Slide 04 - Storage / search children, read parent sections
- **Audience move**: Uncertain about storage / search children, read parent sections → can explain the mechanism or required decision.
- **Relationships**: link: labelled directed dependencies; boundary and element types distinguish C4 levels where named
- **Composition**: architecture page, with the dominant teaching task as focal point.
- **Title**: Storage / search children, read parent sections
- **Core message**: A child identifies the precise matched clause.
- **Content**: A child identifies the precise matched clause. · Its parent supplies neighboring conditions and tables.

#### Slide 05 - Chunk around clauses, then size
- **Audience move**: Uncertain about chunk around clauses, then size → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Chunk around clauses, then size
- **Core message**: Inspect how the clause-aware splitter handles oversized sections.
- **Content**: Inspect how the clause-aware splitter handles oversized sections. Source excerpt: def chunk_by_clause(elements: list[Element], max_characters: int, overlap: int) -> list[Chunk]: /     """Hybrid chunking: structure rules first, size rules second. /  /     Structure: one chunk per numbered clause ("6.2 Processing fee. ..."). A table or /     continuation line stays with the clause that introduces it, and a table is never split. /     Size: only a clause longer than `max_characters` is split. Its tables become their own /     chunks and its narrative is split at sentence boundaries with `overlap` characters /     repeated. Text before section 1 is section 0, "Front matter". /     """ /     section_number, section = 0, "Front matter" /     clauses: list[_Clause] = [_Clause(section_number, section, None, None)] /     for element in elements:

#### Slide 06 - Code / the ingestion fingerprint
- **Audience move**: Uncertain about code / the ingestion fingerprint → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Code / the ingestion fingerprint
- **Core message**: Text, metadata, embedding model and dimensions determine whether to re-embed.
- **Content**: Text, metadata, embedding model and dimensions determine whether to re-embed. Source excerpt: def chunk_checksum(text: str, metadata: dict[str, Any]) -> str: /     """Fingerprint text, metadata, embedding model and embedding dimensions. /  /     Enrichment includes both embedding settings, so either change invalidates chunks. /     """ /     payload = json.dumps({"text": text, "metadata": metadata}, sort_keys=True, ensure_ascii=False) /     return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()

#### Slide 07 - Practical / observe repeatable ingestion
- **Audience move**: Uncertain about practical / observe repeatable ingestion → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical / observe repeatable ingestion
- **Core message**: python -m training.session2.ingest_twin
- **Content**: python -m training.session2.ingest_twin · Expected embedding counts: 32 → 0 → 32 → 0. · Inspect one child ID, checksum and parent section.

#### Slide 08 - Embeddings and the Atlas index must agree
- **Audience move**: Uncertain about embeddings and the atlas index must agree → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Embeddings and the Atlas index must agree
- **Core message**: Use the same model and dimensions for write and query.
- **Content**: Use the same model and dimensions for write and query. · Create the vector/filter index from the documented JSON. · Parent sections need no vector index.

#### Slide 09 - Retrieval / scope first, then expand evidence
- **Audience move**: Uncertain about retrieval / scope first, then expand evidence → can explain the mechanism or required decision.
- **Relationships**: link: labelled directed dependencies; boundary and element types distinguish C4 levels where named
- **Composition**: architecture page, with the dominant teaching task as focal point.
- **Title**: Retrieval / scope first, then expand evidence
- **Core message**: Apply policy filters before ranking candidates.
- **Content**: Apply policy filters before ranking candidates. · Expand parents and complete linked amendments.

#### Slide 10 - Code / date and permission filters
- **Audience move**: Uncertain about code / date and permission filters → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: code page, with the dominant teaching task as focal point.
- **Title**: Code / date and permission filters
- **Core message**: Product scope is added when supplied; model similarity never overrides this filter.
- **Content**: Product scope is added when supplied; model similarity never overrides this filter. Source excerpt:         filters: list[dict[str, object]] = [ /             {"institution": settings.institution}, /             {"effective_date": {"$lte": as_of}}, /             {"effective_to_search": {"$gte": as_of}}, /             {"jurisdiction": request.jurisdiction or settings.jurisdiction}, /             {"confidentiality_level": settings.confidentiality_level}, /         ] /         if request.product_id is not None: /             filters.append({"product_id": request.product_id})

#### Slide 11 - Amendments / lookup date and sanction date
- **Audience move**: Uncertain about amendments / lookup date and sanction date → can explain the mechanism or required decision.
- **Relationships**: link: labelled directed dependencies; boundary and element types distinguish C4 levels where named
- **Composition**: architecture page, with the dominant teaching task as focal point.
- **Title**: Amendments / lookup date and sanction date
- **Core message**: The circular enters policy scope on 1 July 2026.
- **Content**: The circular enters policy scope on 1 July 2026. · Its revised fee applies to sanctions from that date.

#### Slide 12 - Load the amendment's complete condition
- **Audience move**: Uncertain about load the amendment's complete condition → can explain the mechanism or required decision.
- **Relationships**: link: labelled directed dependencies; boundary and element types distinguish C4 levels where named
- **Composition**: architecture page, with the dominant teaching task as focal point.
- **Title**: Load the amendment's complete condition
- **Core message**: A fee quote without applicability can mislead.
- **Content**: A fee quote without applicability can mislead. · Resolve the linked instrument as a complete unit.

#### Slide 13 - Hit rate and multi-reference recall are different
- **Audience move**: Uncertain about hit rate and multi-reference recall are different → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: text page, with the dominant teaching task as focal point.
- **Title**: Hit rate and multi-reference recall are different
- **Core message**: Single expected source: hit or miss among top-k.
- **Content**: Single expected source: hit or miss among top-k. · Multiple expected clauses: fraction of required references found. · MRR adds where the first expected item appears.

#### Slide 14 - Practical / replay the July policy boundary
- **Audience move**: Uncertain about practical / replay the july policy boundary → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical / replay the July policy boundary
- **Core message**: python -m training.showcase --session 2
- **Content**: python -m training.showcase --session 2 · June: 0.35% / POL-HL-V3; July: 0.30% / CIR-2026-07. · Wrong product: insufficient_evidence; no citations.

#### Slide 15 - Practical / diagnose a retrieval miss
- **Audience move**: Uncertain about practical / diagnose a retrieval miss → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: lab page, with the dominant teaching task as focal point.
- **Title**: Practical / diagnose a retrieval miss
- **Core message**: python -m training.session2.recall
- **Content**: python -m training.session2.recall · Compare k=1, 3 and 5; distinguish recall from rank. · One of two required clauses found → recall 0.5.

#### Slide 16 - Session 2 / evidence exit gate
- **Audience move**: Uncertain about session 2 / evidence exit gate → can explain the mechanism or required decision.
- **Relationships**: none
- **Composition**: gate page, with the dominant teaching task as focal point.
- **Title**: Session 2 / evidence exit gate
- **Core message**: Show a stable child ID and a compatible parent scope.
- **Content**: Show a stable child ID and a compatible parent scope. · Find fee plus applicability; report missing references. · Submit recall/MRR evidence and unresolved live checks.

## X. Speaker Notes Requirements
- **Generation**: enabled
Explain visible claims, practical commands, expected outcomes, sources and limitations.
