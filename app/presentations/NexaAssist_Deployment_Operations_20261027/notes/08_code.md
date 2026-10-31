Initialize the PostgreSQL schema and pgvector extension explicitly. The corpus is mounted read-only at /data in the API container. Ingestion verifies source paths/hashes and writes chunks, parent sections and the embedding profile. The exact cosine backend supports dense retrieval; hybrid mode is explicitly rejected. A matching embedding dimension alone is insufficient: model family and profile must also match. The saved 25 October receipt recorded 8 documents, 177 chunks and 80 parent sections; treat those as historical evidence, not as an assertion about a fresh run. A normal restart does not require re-ingestion.

The complete command sequence is in the companion lab guide.

An empty vector corpus can look like a healthy application.