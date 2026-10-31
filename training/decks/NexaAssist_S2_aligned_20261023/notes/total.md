# 01_Distill I

Data foundations, embeddings and retrieval Session 2 of 5 · 16-slide teaching edition Start from the Session 1 contract. Today each pair explains chunk boundaries, demonstrates incremental ingestion and separates retrieval misses from generation problems. This revised deck follows the course lesson sequence; exact lesson URLs appear in section notes and the coverage map.

---

# 02_Documents carry meaning through structure

Tables, headers and code blocks define useful boundaries. Extraction can mix unrelated columns and page furniture. Inspect representative parsed output before embedding. The course starts with Markdown and recursive splitting. NexaAssist adds layout-aware PDF parsing and clause boundaries. A parser that runs successfully can still produce semantically damaged text; the chunking lab makes that visible. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

---

# 03_Ingestion / prepare evidence before embedding

Verify → parse → chunk → redact and fingerprint. Embed changed children; publish children and parents. The source register is verified before building requests. LCEL performs parse, clause chunking, configured redaction, enrichment/checksum, stored-checksum comparison and changed-child upsert. Entire parent sections are stored separately without embeddings. The service removes stale children after successful ingestion; one document failure is isolated and reported. Writes span collections and are not a concurrent transactional publisher. Provider disclosure occurs at embedding, so configured redaction must precede it. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops. The implementation or concept reference is app/services/ingestion.py; app/chains/ingestion.py.

---

# 04_Storage / search children, read parent sections

A child identifies the precise matched clause. Its parent supplies neighboring conditions and tables. For POL-HL-V3, clause 6.2 is a child in the fee section. parent_id links it to the complete section, which also contains other fee conditions. Atlas embeds child text; the parent store is not embedded. Retrieval verifies parent metadata scope and falls back to the child if the parent is missing or mismatched. A matched child is not the author of every parent clause. Required linked amendments are handled separately and the context packer never cuts a table. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops. The implementation or concept reference is app/chains/ingestion.py; app/chains/retrieval.py; app/database/mongo.py.

---

# 05_Chunk around clauses, then size

Inspect how the clause-aware splitter handles oversized sections. Open app/chains/chunking.py and locate def chunk_by_clause. Read the displayed excerpt in context; it is taken directly from the application. Inspect how the clause-aware splitter handles oversized sections. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops. The implementation or concept reference is app/chains/chunking.py.

---

# 06_Code / the ingestion fingerprint

Text, metadata, embedding model and dimensions determine whether to re-embed. Open app/chains/ingestion.py and locate def chunk_checksum. Read the displayed excerpt in context; it is taken directly from the application. Text, metadata, embedding model and dimensions determine whether to re-embed. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops. The implementation or concept reference is app/chains/ingestion.py.

---

# 07_Practical / observe repeatable ingestion

python -m training.session2.ingest_twin Expected embedding counts: 32 → 0 → 32 → 0. Inspect one child ID, checksum and parent section. The lab uses the real PDF and ingestion chain with deterministic fake embeddings and in-memory stores. Run 3 changes the model identifier; it demonstrates invalidation, not actual provider model compatibility. Run chunks and redact from the handout as extensions. Retain a table, an exception and a date caveat in the chunk experiment. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

---

# 08_Embeddings and the Atlas index must agree

Use the same model and dimensions for write and query. Create the vector/filter index from the documented JSON. Parent sections need no vector index. Open app/database/indexes.md and app/chains/embeddings.py. The documented example uses 1536 dimensions; runtime configuration and the selected model must agree. Equal dimension count does not make two models compatible. The index must include every metadata filter field. The full-text Atlas Search index is separate and used only for configured hybrid retrieval. No live index is created or verified by this deck. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 09_Retrieval / scope first, then expand evidence

Apply policy filters before ranking candidates. Expand parents and complete linked amendments. The scrubbed query and request scope feed a shared pre-filter. Dense search is the baseline; hybrid BM25/vector RRF and reranking are conditional settings. The parent store expands each matched child only after scope validation. Linked circulars are loaded by scoped database queries and can exceed top_k as separate amendments. The final context packs complete evidence within its budget. This diagram shows the baseline and names optional ranking in its search node; it does not imply every request uses all modes. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation. The implementation or concept reference is app/services/retrieval.py; app/chains/retrieval.py; app/database/retrieval.py.

---

# 10_Code / date and permission filters

Product scope is added when supplied; model similarity never overrides this filter. Open app/chains/retrieval.py and locate filters: list[dict[str, object]]. Read the displayed excerpt in context; it is taken directly from the application. Product scope is added when supplied; model similarity never overrides this filter. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation. The implementation or concept reference is app/chains/retrieval.py.

---

# 11_Amendments / lookup date and sanction date

The circular enters policy scope on 1 July 2026. Its revised fee applies to sanctions from that date. The base processing fee is 0.35%, minimum ₹5,000 and maximum ₹15,000, plus GST. CIR-2026-07 clause 3.1 changes it to 0.30%, minimum ₹5,000 and maximum ₹10,000; clause 5.1 restricts it to sanctions on or after 1 July 2026. A July policy lookup for a June sanction retains the earlier fee. These are synthetic policy terms. Do not infer precedence from rank or a higher version number. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation. The implementation or concept reference is nexa_synthetic_data/document_register.json; nexa_synthetic_data/policies/CIR-2026-07_Circular_NexaHome_Fee_and_PartPrepayment.pdf.

---

# 12_Load the amendment's complete condition

A fee quote without applicability can mislead. Resolve the linked instrument as a complete unit. POL-HL-V3 clause 6.2 links through supersedes metadata to CIR-2026-07. The full circular supplies precedence (2.1), revised fee (3.1) and sanction applicability (5.1). Other terms remain unchanged and part-prepayment opt-in has a separate rule. Circular links are followed transitively. Inconsistent instrument metadata fails closed; an entirely missing indexed chunk cannot be detected without a source ingestion manifest. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation. The implementation or concept reference is app/database/retrieval.py; app/models/retrieval.py.

---

# 13_Hit rate and multi-reference recall are different

Single expected source: hit or miss among top-k. Multiple expected clauses: fraction of required references found. MRR adds where the first expected item appears. The source labels its single-reference hit-rate exercise Recall@K. NexaAssist can require multiple clauses, so it reports reference recall separately. For two required clauses and one found, recall is one-half; an any-hit metric would hide the missing condition. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 14_Practical / replay the July policy boundary

python -m training.showcase --session 2 June: 0.35% / POL-HL-V3; July: 0.30% / CIR-2026-07. Wrong product: insufficient_evidence; no citations. The actual registered PDFs pass through real parsing, ingestion, scope filters, parent expansion, linked amendments and citation checks. Embeddings, vector ranking, Mongo transport and model drafts are fixtures. Both sanction and lookup dates are explicit in the two examples. Inspect full quoted text and record why the wrong product must abstain. This does not measure live model reasoning or Atlas recall. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 15_Practical / diagnose a retrieval miss

python -m training.session2.recall Compare k=1, 3 and 5; distinguish recall from rank. One of two required clauses found → recall 0.5. Expected evidence is explicit document/clause identity. A first expected item at rank 4 has reciprocal rank 0.25, even when recall is 1 for a single-reference case. A full linked circular can satisfy both required clauses. The lab scores constructed results through the actual scorer; these are not measured retrieval results. Course single-reference hit rate and multi-reference recall are different definitions. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 16_Session 2 / evidence exit gate

Show a stable child ID and a compatible parent scope. Find fee plus applicability; report missing references. Submit recall/MRR evidence and unresolved live checks. Require the chunk experiment, re-ingestion transcript and two-clause retrieval diagnosis. Quality gates remain placeholder targets. Live Atlas retrieval requires a compatible queryable index and approved credentials; a local Mongo fake is not Atlas Vector Search. Keep candidate chunk/parent collections and embedding versions compatible for any future blue/green plan. Next, control what generation may claim.
