# NexaAssist_S2_syllabus_20261024_20261024_073224

- Source: `NexaAssist_S2_syllabus_20261024_20261024_073224.pptx`
- Total slides: 16

## Slide 1

NEXAASSIST / SESSION 02 / DISTILL I

Distill I

RAGOps / version, verify and diagnose evidence

Session 2 / ingestion, retrieval and operational checks

16 slides / offline labs + incident worksheet

LLMOps_Syllabus.md / 03, 04, 05, 09, 12, 14 / Platform agnostic controls; NexaAssist worked example

01/16

### Speaker Notes

Operate the evidence path through versioned ingestion, permission-aware retrieval, evaluation and incident diagnosis. The primary source is LLMOps_Syllabus.md section 12, with EvalOps, tracing, quality and security controls introduced where they affect retrieval. Use 25 minutes for concepts, 20 for code and diagrams, 90 for practicals including a 10-minute break, 25 for the exit review and 20 for recap. The core practicals need no credentials and produce a chunk comparison, re-ingestion transcript, date/product matrix and retrieval-incident worksheet. Primary syllabus: LLMOps_Syllabus.md sections 03, 04, 05, 09, 12, 14.

## Slide 2

NEXAASSIST / SESSION 02 / DISTILL I

RAGOps starts with a versioned source manifest

Track source hash, effective dates, scope and ingestion result.

Compare source and stored chunks for missing or stale evidence.

Inspect tables and exceptions before publishing a candidate.

LLMOps_Syllabus.md / 04, 09, 10, 12 / Concept + inspected local implementation; sources in notes

02/16

### Speaker Notes

Inspect the document register and distinguish source publication from successful ingestion and a queryable index. Record document/version/hash, relevant policy dates, scope, chunking and embedding identities and the ingestion outcome; propose a freshness timestamp and expected freshness window without claiming those controls are all implemented. Compare source and stored chunk manifests for missing, changed and unexpected entries, then inspect representative extraction output for lost table or exception meaning. A metadata match cannot establish statistical embedding drift or live search readiness. Primary syllabus: LLMOps_Syllabus.md sections 04, 09, 10, 12. Supporting lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

## Slide 3

NEXAASSIST / SESSION 02 / INGESTION ARCHITECTURE

Ingestion / prepare evidence before embedding

1 / Verify register

2 / Parse layout

3 / Chunk clauses

load

split

Authority + source SHA-256

Headings, text and tables

Stable IDs + parent links

protect

write

check

6 / Upsert stores

5 / Compare + embed

4 / Redact + hash

Child vectors + parent text

Changed children only

Before embedding disclosure

Capture per-document outcome and changed counts; redaction precedes provider disclosure.

LLMOps_Syllabus.md / 04, 09, 12 / Concept + inspected local implementation; sources in notes

03/16

### Speaker Notes

Follow verify, parse, chunk, redact, compare/embed and upsert as observable ingestion stages. The service records document_ingested with counts and embedding metadata or document_ingest_failed with the document ID and error type; learners identify the responsible stage and the retry/reconciliation evidence. Parent sections are stored without embeddings and stale children are removed only after successful document ingestion. The existing publisher spans collections and is not an atomic blue/green deployment; an ingestion success log alone does not prove index freshness or query readiness. Primary syllabus: LLMOps_Syllabus.md sections 04, 09, 12. Supporting lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

## Slide 4

NEXAASSIST / SESSION 02 / KNOWLEDGE STORAGE

Storage / search children, read parent sections

Embedded child chunks

parent_id lookup

6.2 / Processing fee

Whole fee section

POL-HL-V3_6.2_c01

Key: parent_id

Includes 6.1, 6.2 and other fee clauses

6.1 / General fee terms

Plain text store / not embedded

Neighboring conditions

same parent link

Search the child; expand a scope-compatible parent. Missing or mismatched parent → child fallback.

The matched child does not own every claim in the parent. Keep citation identity precise.

LLMOps_Syllabus.md / 09, 12 / Concept + inspected local implementation; sources in notes

04/16

### Speaker Notes

Use this storage diagram to state the retrieval contract: stable child IDs identify searchable clauses and a parent link supplies complete neighboring conditions. Check parent existence, matching document/version/date/product/access scope and body containment before trusting expanded evidence. A missing or scope-mismatched parent falls back to the child in this implementation and needs an operational diagnostic. Keep citation identity precise because a matched child is not the author of every claim contained in its parent. Primary syllabus: LLMOps_Syllabus.md sections 09, 12. Supporting lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

## Slide 5

NEXAASSIST / SESSION 02 / DISTILL I

Practical / compare chunking candidates

uv run --no-sync python -m training.session2.chunks

max_characters chunks tables preserved

300 40 yes

1200 32 yes

5000 32 yes

Submit: chunk counts, preserved table and a justified candidate setting.

LLMOps_Syllabus.md / 03, 12 / Offline exercise; observed fixture results

05/16

### Speaker Notes

Allow 15 minutes for python -m training.session2.chunks and compare max_characters values 300, 1200 and 5000 on the shipped policy. The expected counts are 40, 32 and 32 chunks, with tables preserved and a longest 372-character table chunk at the 300-character setting. Save the comparison and inspect a table plus an exception before selecting a candidate. Count and shape are diagnostic evidence, not a retrieval-quality benchmark; the next evaluation must use fixed questions and evidence references. Primary syllabus: LLMOps_Syllabus.md sections 03, 12. Supporting lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

## Slide 6

NEXAASSIST / SESSION 02 / INGESTION IDENTITY

Code / the ingestion fingerprint

def chunk_checksum(text: str, metadata: dict[str, Any]) -> str:

"""Fingerprint text, metadata, embedding model and embedding dimensions.

Enrichment includes both embedding settings, so either change invalidates chunks.

"""

payload = json.dumps({"text": text, "metadata": metadata}, sort_keys=True, ensure_ascii=False)

return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()

Text, metadata, embedding model and dimensions determine

whether to re-embed.

LLMOps_Syllabus.md / 01, 08, 12 / Concept + inspected local implementation; sources in notes

06/16

### Speaker Notes

Use the actual checksum code to explain invalidation and embedding cost. The fingerprint includes text and metadata, including the embedding model and dimensions, so a relevant change makes the child eligible for embedding again. An unchanged rerun avoids repeated embeddings and preserves stable IDs. A matching dimension count alone does not make different embedding models compatible, and changing a model identifier in a fixture is not a real embedding migration. Primary syllabus: LLMOps_Syllabus.md sections 01, 08, 12. Supporting lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

## Slide 7

NEXAASSIST / SESSION 02 / OFFLINE PRACTICAL

Practical / observe repeatable ingestion

uv run --no-sync python -m training.session2.ingest_twin

Predict → run: embedded counts 32 → 0 → 32 → 0.

Submit: ID, checksum, parent scope and re-embedding reason.

LLMOps_Syllabus.md / 01, 08, 12 / Offline exercise; observed fixture results

07/16

### Speaker Notes

Allow 20 minutes for the four-run ingestion lab using a real PDF, the actual ingestion chain, counting fake embeddings and in-memory stores. Expect 32 embedded chunks on the initial run, zero on an unchanged rerun, 32 after the model identifier changes and zero on its unchanged rerun. Record one child ID, checksum, parent ID and the reason each run does or does not embed. Treat the counts as fixture observations and explain the avoided embedding work without inventing a provider price or claiming live Atlas idempotency. Primary syllabus: LLMOps_Syllabus.md sections 01, 08, 12. Supporting lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

## Slide 8

NEXAASSIST / SESSION 02 / VECTOR SCHEMA

Embedding migration / rebuild and validate

Keep model, dimensions and query/index settings compatible.

Plan candidate chunk + parent stores; rerun fixed evaluations.

Promote after validation; retain the complete rollback bundle.

LLMOps_Syllabus.md / 01, 11, 12, 14 / Design exercise; no live migration

08/16

### Speaker Notes

Use app/database/indexes.md as the exact Atlas JSON reference for the configured dimensions and filter fields; the 1536-dimensional example is not a universal model requirement. A migration design uses a compatible query embedding and candidate child/parent stores, verifies index readiness, permissions and fixed retrieval cases, and evaluates quality, latency and embedding cost before promotion. Retain the old model/settings and stores for rollback rather than merely renaming an index, and retire them only after validated recovery and retention review. This is a design exercise: the current ingestion path updates stores in place and no live index build, blue/green switch or rollback is executed. Primary syllabus: LLMOps_Syllabus.md sections 01, 11, 12, 14. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 9

NEXAASSIST / SESSION 02 / RETRIEVAL ARCHITECTURE

Retrieval / scope first, then expand evidence

1 / Request + filters

2 / Candidate search

3 / Rank + top_k

search

rank

Scrub query; constrain corpus

Query embedding + Atlas

Reranker when enabled

Dates, product, access scope

Dense or configured hybrid

Keep the requested hit count

expand

pack

link

6 / Pack context

5 / Load amendments

4 / Expand parents

Preserve complete evidence

Scoped linked instruments

Validate matching scope

Then hand off to generation

Separate from top_k results

Otherwise retain child text

Numbered path: baseline retrieval. Hybrid search and reranking are explicit configuration branches.

LLMOps_Syllabus.md / 03, 04, 09, 12 / Concept + inspected local implementation; sources in notes

09/16

### Speaker Notes

Use the retrieval diagram to assign evidence and timing checks to filtering, search, optional reranking, parent expansion, amendment resolution and context packing. Read the existing retrieval_stages event and RetrieveTimings fields rather than assuming every operation has an exported span. Compare dense search, hybrid retrieval or a reranker on the same questions, corpus, embedding settings and k; include quality, timing and cost in a proposed experiment record. Ranking cannot override access/date filters, and fixture rankings do not establish live Atlas recall or reranker improvement. Primary syllabus: LLMOps_Syllabus.md sections 03, 04, 09, 12. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 10

NEXAASSIST / SESSION 02 / SCOPED RETRIEVAL

Code / date and permission filters

filters: list[dict[str, object]] = [

{"institution": settings.institution},

{"effective_date": {"$lte": as_of}},

{"effective_to_search": {"$gte": as_of}},

{"jurisdiction": request.jurisdiction or settings.jurisdiction},

{"confidentiality_level": settings.confidentiality_level},

]

if request.product_id is not None:

filters.append({"product_id": request.product_id})

Product scope is added when supplied; model similarity

never overrides this filter.

LLMOps_Syllabus.md / 09, 10, 12 / Concept + inspected local implementation; sources in notes

10/16

### Speaker Notes

Read the actual pre-filter and predict the eligible institution, dates, jurisdiction, confidentiality and optional product scope. A wrong-product query must not use unrelated product evidence, and table/date correctness remains necessary after access filtering. Add boundary and unauthorized-scope cases to the proposed permission test matrix. The displayed confidentiality scope comes from settings, so this is not evidence that per-user identity, tenant authentication or authorization policies have been implemented. Primary syllabus: LLMOps_Syllabus.md sections 09, 10, 12. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 11

NEXAASSIST / SESSION 02 / POLICY APPLICABILITY

Amendments / lookup date and sanction date

Lookup from 1 July 2026

Lookup on 30 June:

POL-HL-V3 is in force.

CIR-2026-07 enters policy scope

Earlier sanction

On/after cutoff

Sanction before 1 July

Sanction from 1 July

Keep 0.35% processing fee

Apply revised 0.30% fee

Min ₹5,000 / max ₹15,000 / plus GST

Min ₹5,000 / max ₹10,000 / plus GST

Lookup date chooses instruments; sanction date controls the circular's fee applicability.

LLMOps_Syllabus.md / 03, 05, 12 / Concept + inspected local implementation; sources in notes

11/16

### Speaker Notes

Use this date boundary as a regression case, distinguishing when a circular enters policy scope from the sanction date that determines fee applicability. The synthetic base fee is 0.35 percent with minimum ₹5,000 and maximum ₹15,000 plus GST, while the circular revises it to 0.30 percent with minimum ₹5,000 and maximum ₹10,000 plus GST for sanctions from 1 July 2026. A July lookup for an earlier sanction retains the earlier applicable fee. Do not choose policy precedence from similarity rank or a higher version label. Primary syllabus: LLMOps_Syllabus.md sections 03, 05, 12. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 12

NEXAASSIST / SESSION 02 / LINKED EVIDENCE

Load the amendment's complete condition

2.1 / Precedence

priority

Which clauses are replaced?

POL-HL-V3

CIR-2026-07

load

fee

Matched clause 6.2 / fee

supersedes: POL-HL-V3

Base policy hit

Load complete scoped instrument

3.1 / Revised fee

Rate + minimum + maximum

scope

5.1 / Loans covered

A fee quote without applicability can mislead.

Sanction-date applicability

Selected clauses are shown; production loads the whole instrument.

The link query follows metadata, not the similarity rank.

LLMOps_Syllabus.md / 03, 05, 12 / Concept + inspected local implementation; sources in notes

12/16

### Speaker Notes

A grounded answer needs the fee and the applicability condition, so follow the linked circular as a complete scoped instrument. The example separates precedence, revised fee and sanction applicability, while production resolution loads the full instrument and follows supported links transitively. A plausible answer or exact quotation can still be incomplete if the condition is missing. Inconsistent instrument metadata fails closed, but detecting an entirely absent indexed chunk also needs a complete ingestion manifest. Primary syllabus: LLMOps_Syllabus.md sections 03, 05, 12. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 13

NEXAASSIST / SESSION 02 / DISTILL I

Retrieval quality / coverage and ranking

Recall@k: required references found / references required.

MRR: mean reciprocal rank of the first required hit.

NDCG@k: graded ranking / ideal ranking; worksheet only.

LLMOps_Syllabus.md / 03, 12 / Concept + inspected local implementation; sources in notes

13/16

### Speaker Notes

The existing scorer reports reference recall and reciprocal-rank behavior over constructed retrieval results, with the complete-amendment convention documented separately from ranked child hits. Finding one of two required clauses gives recall 0.5, and finding the first relevant item at rank four gives reciprocal rank 0.25; a dataset mean produces MRR. For the manual extension use nonnegative linear relevance gains and log2(rank+1) discount, then normalize DCG by the ideal ranking at the same k, explicitly recording this gain convention. NDCG needs graded relevance labels and is not implemented in this repository scorer; consult https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html for the definition. Primary syllabus: LLMOps_Syllabus.md sections 03, 12. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 14

NEXAASSIST / SESSION 02 / OFFLINE POLICY DEMONSTRATION

Practical / replay the July policy boundary

uv run --no-sync python -m training.showcase --session 2

June: 0.35% / POL-HL-V3; July: 0.30% / CIR-2026-07.

Record lookup + sanction dates, product, status and citations.

Wrong product: insufficient_evidence; no citations.

LLMOps_Syllabus.md / 03, 05, 09, 12 / Offline exercise; observed fixture results

14/16

### Speaker Notes

Allow 20 minutes for the date/product regression lab and predict the fee and evidence before running it. The June example yields the synthetic 0.35 percent fee from POL-HL-V3, the July example yields 0.30 percent from CIR-2026-07 with explicit lookup and sanction dates, and the wrong product returns insufficient_evidence with no citations. Submit a three-row matrix with dates, scope, status, evidence IDs and applicable conditions rather than only answer strings. Real registered PDFs and application controls are exercised, while external embeddings, ranking, Mongo transport and model drafts are fixtures. Primary syllabus: LLMOps_Syllabus.md sections 03, 05, 09, 12. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 15

NEXAASSIST / SESSION 02 / RETRIEVAL EVALUATION

Practical / score, then triage the incident

uv run --no-sync python -m training.session2.recall

Partial evidence: recall 0.5; first hit at rank 4: RR 0.25.

Classify: nonempty miss / stale chunks / embedding mismatch.

LLMOps_Syllabus.md / 03, 04, 05, 12, 14 / Offline exercise; observed fixture results

15/16

### Speaker Notes

Allow 25 minutes for the recall script, the failure-mode report and the incident worksheet, with the 10-minute break completing the 90-minute practical block. Run python -m training.session2.recall and python -m app.evaluation.rag_failure_modes, then record constructed scores and classify each fixture failure before proposing a model or prompt change. The report marks Atlas readiness not_checked and embedding distribution drift not_measured; preserve those states and identify the missing measurement. Draft a redacted correlation record with case/request identity, artifact versions, evidence IDs, stage/timing, error class, owner and response; this is worksheet evidence and not a captured production trace. Primary syllabus: LLMOps_Syllabus.md sections 03, 04, 05, 12, 14. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 16

NEXAASSIST / SESSION 02 / EXIT GATE

Session 2 / RAGOps exit gate

Hand in: chunk table, repeat-ingest log and date/product matrix.

Add: recall/MRR worksheet, incident owner and recovery check.

Separate scored fixtures from open live quality/latency checks.

LLMOps_Syllabus.md / 03, 04, 05, 11, 12, 14 / Learning gate; production evidence remains open

16/16

### Speaker Notes

Use the gate review to inspect the chunk comparison, four-run ingestion transcript, date/product matrix and retrieval-incident worksheet. Require the learner to identify missing evidence, choose the responsible ingestion/retrieval stage and propose a recovery validation using the same fixed cases. Include the manual NDCG extension only when graded labels and the gain convention are supplied, and retain live readiness, recall, quality, latency and cost as open measurements. Session 3 deepens PromptOps, judge calibration and answer-quality evaluation before a production release can be approved. Primary syllabus: LLMOps_Syllabus.md sections 03, 04, 05, 11, 12, 14.
