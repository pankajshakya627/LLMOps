# 01_Distill I

Data foundations, embeddings and retrieval Session 2 of 5 · 3 hours · hands-on NexaAssist Start from the Session 1 contract. Today each pair explains chunk boundaries, demonstrates incremental ingestion and separates retrieval misses from generation problems.

---

# 02_The evidence path is the product

Preserve policy structure and tables. Retrieve the right version for the requested date. Measure expected clauses before generating answers. Similarity is a ranking signal, not policy authority. The model cannot recover a policy clause that never enters the context.

---

# 03_Today’s workshop route

25 min data/retrieval concepts + 20 min walkthrough 90 min pair experiments, including a 10 min break 25 min retrieval gate review + 20 min recap Collect the chunk-count experiment, an idempotency explanation and a retrieval score sheet. Those become part of the release file.

---

# 04_One ingestion pipeline, separate duties

Parse structure → chunk clauses → mask identifiers Enrich metadata → compare checksums Embed changed children → upsert parents and chunks The parent sections provide readable context, while smaller child chunks serve search. A checksum includes embedding compatibility so a model change invalidates old vectors. The implementation or concept reference is app/chains/ingestion.py.

---

# 05_Three forms of document noise

Artifact noise: control characters and extraction debris. Layout noise: repeated page headers and split tables. Semantic noise: obsolete or contradictory policy text. Different noise needs different remedies. Do not use a larger model as a substitute for correcting source structure or effective-date metadata.

---

# 06_Chunk around clauses, then size

Inspect how the clause-aware splitter handles oversized sections. Open app/chains/chunking.py and locate def chunk_by_clause. Read the displayed excerpt in context; it is taken directly from the application. Inspect how the clause-aware splitter handles oversized sections. The implementation or concept reference is app/chains/chunking.py.

---

# 07_Practical 1 / observe real PDF chunks

Run: python -m training.session2.chunks Compare maximum sizes 300, 1200 and 5000. Expected counts: 40, 32 and 32; tables remain visible. The corpus is local. The size setting only splits oversized clauses, so 1200 and 5000 produce the same count here. Inspect an actual table chunk before choosing a size.

---

# 08_Small search units; readable context

Child: precise clause text with metadata. Parent: the surrounding section used for generation. Budgeting must preserve required amendment evidence. Parent context can contain other clauses. A citation must not pretend the search child owns every clause in its parent. Unfittable amendments lead to safe abstention. The implementation or concept reference is app/chains/context.py; app/database/mongo.py.

---

# 09_Idempotency is an observable property

Unchanged text and embedding schema → no re-embedding. Model or dimensions change → regenerate vectors. Stable clause identity avoids renumbering unrelated data. Ask the class to distinguish a source hash from a chunk-plus-embedding checksum. Both matter, but they protect different boundaries. The implementation or concept reference is training/session2/ingest_twin.py.

---

# 10_Practical 2 / repeat ingestion offline

Run: python -m training.session2.ingest_twin Predict embedded counts before each run. Expected: 32 → 0 → 32 → 0. The embedding and stores are test doubles. This proves the incremental control flow, not Atlas writes or model-vector compatibility in a live index.

---

# 11_PII controls belong before embedding

Run: python -m training.session2.redact Inspect EMAIL, PHONE, PAN and AADHAAR placeholders. Verify loan amounts remain readable. Regex has false positives and misses free-form personal data. The lab distinguishes identifiers from grouped currency values, but cannot establish complete privacy protection. The implementation or concept reference is app/chains/redaction.py.

---

# 12_Embeddings are part of the schema

Configured model and dimensions must match indexed vectors. The Atlas index points to the embedding field. A dimension mismatch is a compatibility failure. Do not assume that changing a configuration variable transforms stored vectors. Re-embedding and compatible index configuration are required.

---

# 13_Use the official MongoDB integration

Collection, embedding and index_name are passed explicitly; index creation is manual. Open app/database/mongo.py and locate return MongoDBAtlasVectorSearch(. Read the displayed excerpt in context; it is taken directly from the application. Collection, embedding and index_name are passed explicitly; index creation is manual. The implementation or concept reference is app/database/mongo.py.

---

# 14_The index definition is already documented

Open app/database/indexes.md. Use the exact JSON matching configured dimensions. Check every metadata filter field in the live index. No new vector-store configuration is introduced by this training kit. The existing index JSON remains the authority; never infer a new cluster layout from a slide. The implementation or concept reference is app/database/indexes.md.

---

# 15_Dates and permissions constrain evidence

Run: python -m training.session2.asof Compare 2026-06-30 with 2026-07-01. Expected: the July circular enters scope on its effective date. Loan sanction date and policy lookup date are distinct. The answer chain asks for clarification when the requested lookup scope conflicts with the supplied filter.

---

# 16_Dense, hybrid and reranked retrieval

Dense search matches embedding similarity. Hybrid adds lexical evidence; reranking changes order. Evaluate each configuration on the same cases. Optional retrieval modes already exist. Avoid assuming that a hybrid configuration is better until a comparable retrieval evaluation supports that claim. The implementation or concept reference is app/chains/retrieval.py.

---

# 17_Recall and rank answer different questions

Recall@k: fraction of required references found. MRR: reciprocal rank of the first expected reference. A fee question can require more than one clause. With one required reference at rank four and k at least four, recall is one and reciprocal rank is 0.25. With two required clauses and only one found, recall is 0.5.

---

# 18_Practical 3 / score a retrieval miss

Run: python -m training.session2.recall Compare k=1, k=3 and k=5. Explain the two-clause fee case and linked amendment. These hand-authored hits exercise the real scoring function. They are scenario data, not reference scores from a live Atlas run.

---

# 19_Optional live / ingest then evaluate

Needs approved Atlas access and model credentials. Run ingestion twice; then retrieval_eval --k 5. Record configuration, missing clauses and the gate result. Use the complete commands in the handout. Query embeddings spend provider tokens. Create the existing documented index manually and confirm it is queryable before the class. The implementation or concept reference is training/session2/handout.md.

---

# 20_Treat re-indexing as a release

Build a separate compatible candidate data store. Evaluate candidate retrieval and answer quality. Switch the full configuration only after review. Blue/green is discussed, not automated here. A new index name over the same mutated collection does not preserve old data; parent sections must remain compatible as well.

---

# 21_Exit gate / evidence before eloquence

Submit chunk experiment and checksum explanation. Report recall/MRR and categorize every missing reference. Live scores remain unmeasured until the live lab runs. Use the owner-approved threshold for a real release. For the offline class, pass by explaining the measurements and their limitations rather than claiming live recall.

---

# 22_Next / control what generation may claim

Read app/chains/prompts/answer.py. Bring one unsupported question and one scope ambiguity. Keep the same retrieval cases for Session 3. The next session adds structured generation, deterministic citation checks and semantic evaluation while preserving this evidence contract.
