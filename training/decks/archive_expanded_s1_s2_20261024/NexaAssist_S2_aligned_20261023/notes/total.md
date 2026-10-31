# 01_Distill I

Data foundations, embeddings and retrieval Session 2 of 5 · 3 hours · source-aligned workshop Start from the Session 1 contract. Today each pair explains chunk boundaries, demonstrates incremental ingestion and separates retrieval misses from generation problems. This revised deck follows the course lesson sequence; exact lesson URLs appear in section notes and the coverage map.

---

# 02_The evidence path is the product

Preserve policy structure and tables. Retrieve the right version for the requested date. Measure expected clauses before generating answers. Similarity is a ranking signal, not policy authority. The model cannot recover a policy clause that never enters the context.

---

# 03_Today’s workshop route

25 min data/retrieval concepts + 20 min walkthrough 90 min pair experiments, including a 10 min break 25 min retrieval gate review + 20 min recap Collect the chunk-count experiment, an idempotency explanation and a retrieval score sheet. Those become part of the release file.

---

# 04_Showcase / a fee changes on 1 July

30 June sanction and lookup: base policy fee. 1 July sanction and lookup: linked circular fee. A different product must not reuse those sources. Use actual registered POL-HL-V3 and CIR-2026-07 PDFs. State both lookup and sanction dates. A later lookup does not change an earlier sanction's fee. All policies are synthetic.

---

# 05_Run the dated-policy demonstration

python -m training.showcase --session 2 June: 0.35% / POL-HL-V3. July: 0.30% / CIR-2026-07; quotes verified. Allow 20 minutes. Parsing, ingestion, date/product filters, parent expansion, linked amendments and answer checks are real code. Mongo transport, embedding, ranking and model outputs are fixtures. Inspect the full circular, including applicability and revised caps.

Code walkthrough: app/chains/retrieval.py
        if amendment_search is not None and rows:
            documents = await amendment_search.ainvoke(
                {
                    "doc_ids": list(
                        dict.fromkeys(document.metadata["doc_id"] for document, _ in rows)
                    ),
                    "pre_filter": {"$and": filters},
                }
            )
            amendments = [

NEXA-HL → NEXA-PL with the fee question. Expect insufficient_evidence and no citation. Explain the separate role of the sanction date. The script asserts the wrong-product outcome. Change one input at a time and inspect source IDs. The fake generator does not measure live reasoning or ranking quality.

---

# 06_Data Foundations for LLMOps

Educative lesson 07 Concept → worked example → NexaAssist application This section follows the lesson Data Foundations for LLMOps. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

---

# 07_Documents carry meaning through structure

Tables, headers and code blocks define useful boundaries. Extraction can mix unrelated columns and page furniture. Inspect representative parsed output before embedding. The course starts with Markdown and recursive splitting. NexaAssist adds layout-aware PDF parsing and clause boundaries. A parser that runs successfully can still produce semantically damaged text; the chunking lab makes that visible. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

---

# 08_Three forms of document noise

Artifact noise: control characters and extraction debris. Layout noise: repeated page headers and split tables. Semantic noise: obsolete or contradictory policy text. Different noise needs different remedies. Do not use a larger model as a substitute for correcting source structure or effective-date metadata. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

---

# 09_Embed-ETL has a safety order

Parse and normalize → inspect structure. Redact sensitive fields → define stable chunk metadata. Only then compute embeddings and publish searchable data. Embedding can disclose text to a provider as well as create a stored representation. The practical lesson is to remove sensitive material before that boundary and retain deletion/version metadata. Avoid the absolute claim that all embeddings are impossible to delete: known records can be retired, but hidden sensitive content is hard to locate. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

---

# 10_Chunk around clauses, then size

Inspect how the clause-aware splitter handles oversized sections. Open app/chains/chunking.py and locate def chunk_by_clause. Read the displayed excerpt in context; it is taken directly from the application. Inspect how the clause-aware splitter handles oversized sections. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops. The implementation or concept reference is app/chains/chunking.py.

---

# 11_Practical 1 / observe real PDF chunks

Run: python -m training.session2.chunks Compare maximum sizes 300, 1200 and 5000. Expected counts: 40, 32 and 32; tables remain visible. The corpus is local. The size setting only splits oversized clauses, so 1200 and 5000 produce the same count here. Inspect an actual table chunk before choosing a size. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

---

# 12_Small search units; readable context

Child: precise clause text with metadata. Parent: the surrounding section used for generation. Budgeting must preserve required amendment evidence. Parent context can contain other clauses. A citation must not pretend the search child owns every clause in its parent. Unfittable amendments lead to safe abstention. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops. The implementation or concept reference is app/chains/context.py; app/database/mongo.py.

---

# 13_Idempotency is an observable property

Unchanged text and embedding schema → no re-embedding. Model or dimensions change → regenerate vectors. Stable clause identity avoids renumbering unrelated data. Ask the class to distinguish a source hash from a chunk-plus-embedding checksum. Both matter, but they protect different boundaries. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops. The implementation or concept reference is training/session2/ingest_twin.py.

---

# 14_Practical 2 / repeat ingestion offline

Run: python -m training.session2.ingest_twin Predict embedded counts before each run. Expected: 32 → 0 → 32 → 0. The embedding and stores are test doubles. This proves the incremental control flow, not Atlas writes or model-vector compatibility in a live index. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

---

# 15_PII controls belong before embedding

Run: python -m training.session2.redact Inspect EMAIL, PHONE, PAN and AADHAAR placeholders. Verify loan amounts remain readable. Regex has false positives and misses free-form personal data. The lab distinguishes identifiers from grouped currency values, but cannot establish complete privacy protection. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops. The implementation or concept reference is app/chains/redaction.py.

---

# 16_Exercise / preserve the complete policy condition

Find one table, one exception and one date caveat. Show the child text and its parent context. Explain which change could create an incomplete answer. Use the actual synthetic PDF and existing chunks lab. Record the clause identity rather than only a character count. Expected learning: a smaller search unit needs enough surrounding context to preserve an exception, and larger chunks can weaken ranking. Source lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

---

# 17_Embeddings, Vector Storage, and Evaluation

Educative lesson 08 Concept → worked example → NexaAssist application This section follows the lesson Embeddings, Vector Storage, and Evaluation. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 18_An embedding is a representation, not an answer

A model maps text into numeric coordinates. Similarity helps rank candidates; it does not prove authority. Use the same compatible model and dimension schema. The source uses LiteLLM with provider embeddings and PostgreSQL vector columns. NexaAssist obtains integration-specific embeddings and explicitly configures Atlas dimensions. A nominally equal dimension count does not make two embedding models interchangeable. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 19_Approximate search trades exhaustive work for speed

Nearest-neighbor structures avoid scanning every vector. Index settings affect latency and candidate recall. Measure expected sources under the actual filters. HNSW is an example of approximate nearest-neighbor indexing, not an application-level correctness guarantee. The live Atlas configuration is documented locally. Do not manufacture cluster parameters or claim a throughput benchmark from an offline fake. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 20_Embeddings are part of the schema

Configured model and dimensions must match indexed vectors. The Atlas index points to the embedding field. A dimension mismatch is a compatibility failure. Do not assume that changing a configuration variable transforms stored vectors. Re-embedding and compatible index configuration are required. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 21_Use the official MongoDB integration

Collection, embedding and index_name are passed explicitly; index creation is manual. Open app/database/mongo.py and locate return MongoDBAtlasVectorSearch(. Read the displayed excerpt in context; it is taken directly from the application. Collection, embedding and index_name are passed explicitly; index creation is manual. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation. The implementation or concept reference is app/database/mongo.py.

---

# 22_The index definition is already documented

Open app/database/indexes.md. Use the exact JSON matching configured dimensions. Check every metadata filter field in the live index. No new vector-store configuration is introduced by this training kit. The existing index JSON remains the authority; never infer a new cluster layout from a slide. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation. The implementation or concept reference is app/database/indexes.md.

---

# 23_Dates and permissions constrain evidence

Run: python -m training.session2.asof Compare 2026-06-30 with 2026-07-01. Expected: the July circular enters scope on its effective date. Loan sanction date and policy lookup date are distinct. The answer chain asks for clarification when the requested lookup scope conflicts with the supplied filter. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 24_Dense, hybrid and reranked retrieval

Dense search matches embedding similarity. Hybrid adds lexical evidence; reranking changes order. Evaluate each configuration on the same cases. Optional retrieval modes already exist. Avoid assuming that a hybrid configuration is better until a comparable retrieval evaluation supports that claim. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation. The implementation or concept reference is app/chains/retrieval.py.

---

# 25_Hit rate and multi-reference recall are different

Single expected source: hit or miss among top-k. Multiple expected clauses: fraction of required references found. MRR adds where the first expected item appears. The source labels its single-reference hit-rate exercise Recall@K. NexaAssist can require multiple clauses, so it reports reference recall separately. For two required clauses and one found, recall is one-half; an any-hit metric would hide the missing condition. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 26_Recall and rank answer different questions

Recall@k: fraction of required references found. MRR: reciprocal rank of the first expected reference. A fee question can require more than one clause. With one required reference at rank four and k at least four, recall is one and reciprocal rank is 0.25. With two required clauses and only one found, recall is 0.5. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 27_Practical 3 / score a retrieval miss

Run: python -m training.session2.recall Compare k=1, k=3 and k=5. Explain the two-clause fee case and linked amendment. These hand-authored hits exercise the real scoring function. They are scenario data, not reference scores from a live Atlas run. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 28_Version the retrieval artifact as a compatible set

Record parser/chunker settings and embedding identity. Build a candidate knowledge snapshot. Evaluate before changing the serving configuration. Changing embeddings or splitting changes retrieval behavior. The source proposes rebuilding a separate index version. Our code supports incremental upserts; immutable snapshots and traffic promotion are future operational capabilities. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 29_The course retrieval CI gate is an example

Source example: fail when single-reference hit rate < 0.90. NexaAssist has local recall gates with placeholder targets. A live Atlas test needs a real compatible candidate index. Do not claim that a local MongoDB container supplies Atlas Vector Search. CI should distinguish offline control-flow tests from a credentialed integration gate, and dataset owners must approve actual thresholds. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 30_Optional live / ingest then evaluate

Needs approved Atlas access and model credentials. Run ingestion twice; then retrieval_eval --k 5. Record configuration, missing clauses and the gate result. Use the complete commands in the handout. Query embeddings spend provider tokens. Create the existing documented index manually and confirm it is queryable before the class. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation. The implementation or concept reference is training/session2/handout.md.

---

# 31_Treat re-indexing as a release

Build a separate compatible candidate data store. Evaluate candidate retrieval and answer quality. Switch the full configuration only after review. Blue/green is discussed, not automated here. A new index name over the same mutated collection does not preserve old data; parent sections must remain compatible as well. Source lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

---

# 32_Exit gate / evidence before eloquence

Submit chunk experiment and checksum explanation. Report recall/MRR and categorize every missing reference. Live scores remain unmeasured until the live lab runs. Use the owner-approved threshold for a real release. For the offline class, pass by explaining the measurements and their limitations rather than claiming live recall.

---

# 33_Next / control what generation may claim

Read app/chains/prompts/answer.py. Bring one unsupported question and one scope ambiguity. Keep the same retrieval cases for Session 3. The next session adds structured generation, deterministic citation checks and semantic evaluation while preserving this evidence contract.
