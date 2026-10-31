# MongoDB Atlas Vector Search index

The default local stack now uses **PostgreSQL/pgvector** and does not require
Atlas. Follow the [pgvector setup](PGVECTOR.md) first. Atlas-specific settings below apply only
to `STORAGE_BACKEND=mongodb`.

Create this index manually in Atlas (Atlas UI > Atlas Search > Create Search Index > Atlas Vector Search > JSON editor) on the collection named by `MONGODB_DB` / `MONGODB_COLLECTION`.

- **Index name:** `policy_chunks_v1` (must match `VECTOR_INDEX_NAME`)
- **numDimensions:** must match `EMBEDDING_DIMENSIONS` (1536 for `text-embedding-3-small`)

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    },
    { "type": "filter", "path": "institution" },
    { "type": "filter", "path": "product_id" },
    { "type": "filter", "path": "jurisdiction" },
    { "type": "filter", "path": "effective_date" },
    { "type": "filter", "path": "effective_to_search" },
    { "type": "filter", "path": "doc_type" },
    { "type": "filter", "path": "confidentiality_level" }
  ]
}
```

`effective_date` and `effective_to_search` support the inclusive as-of query `effective_date <= d AND effective_to_search >= d`. Both are ISO date strings. Open-ended documents keep `effective_to: null` as source metadata and store `effective_to_search: "9999-12-31"` for the index. Rebuild the existing Atlas index with this JSON and re-ingest the document register before using the retrieval API; re-ingestion updates the chunk checksums and metadata. Filter fields can only be used in a query if they are in the index.

Changing the embedding model or dimension means a new index version (`policy_chunks_v2`) and a full re-embed, never a mixed index.

For a different embedding family, use a **separate chunk collection and parent
collection** as well as a new index. The application now checks existing chunk
and parent metadata before constructing the vector store and refuses incompatible,
mixed or unknown profiles. A matching legacy OpenAI corpus remains readable.
Metadata scans have a two-second deadline; use an immutable corpus manifest before
scaling ingestion. This check is not a transaction or a lock for concurrent writers.

### Local Qwen example (separate corpus)

`app/gateway/ollama.env.example` names example collections
`policy_chunks_qwen3_v1` and `policy_sections_qwen3_v1`, index `policy_qwen3_v1`,
and an explicitly declared profile `qwen3-0.6b-local-v1`. Confirm the actual model
digest and output length first. The following exact JSON is for the **example
expected length of 1024**; change it and `EMBEDDING_DIMENSIONS` together if the
observed runtime contract differs. Create it on the new Qwen chunk collection.

```json
{
  "fields": [
    { "type": "vector", "path": "embedding", "numDimensions": 1024, "similarity": "cosine" },
    { "type": "filter", "path": "institution" },
    { "type": "filter", "path": "product_id" },
    { "type": "filter", "path": "jurisdiction" },
    { "type": "filter", "path": "effective_date" },
    { "type": "filter", "path": "effective_to_search" },
    { "type": "filter", "path": "doc_type" },
    { "type": "filter", "path": "confidentiality_level" }
  ]
}
```

Custom endpoints require `EMBEDDING_PROFILE`. Use a new value and new stores if the
underlying deployment/model changes, including a mutable model tag resolving to
different weights. The application validates declared identity and vector shape;
it cannot infer actual weights from an alias. Never route a Qwen query to the
existing OpenAI corpus or add embedding-family fallback. Reusing a profile label
does not make different models equivalent.

## Gateway profiles

The Docker stack and `app/gateway/application.env.example` use separate gateway
collections because stored `embedding_model` metadata records the route alias.
Even when the underlying weights are the same, do not silently reinterpret an
existing direct-Ollama corpus as a gateway-alias corpus.

| Route | Chunk collection | Parent collection | Index name | Dimensions | Profile |
|---|---|---|---|---:|---|
| `nexa-embed-local` | `policy_chunks_qwen3_gateway_v1` | `policy_sections_qwen3_gateway_v1` | `policy_qwen3_gateway_v1` | 1024, verify runtime | `qwen3-0.6b-gateway-v1` |
| `nexa-embed-openai` | `policy_chunks_openai_gateway_v1` | `policy_sections_openai_gateway_v1` | `policy_openai_gateway_v1` | 1536 | `openai-3-small-gateway-v1` |

Create the index on the selected chunk collection. Reuse the exact filter mappings
above and choose the matching vector dimension; set the index name separately in
Atlas. Wait until queryable, then ingest with the same profile used for serving.
The parent collection needs no vector index. Embedding routes never cross-fallback.

## Full-text index for hybrid retrieval

Create a second **Atlas Search** index on the same chunk collection. This is a text
index, separate from the Atlas Vector Search index above. Set its name to
`policy_text_v1` (matching `TEXT_INDEX_NAME`):

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "text": {
        "type": "string",
        "analyzer": "lucene.standard"
      }
    }
  }
}
```

Wait until both indexes are queryable, then set `RETRIEVAL_MODE=hybrid`.
`MongoDBAtlasHybridSearchRetriever` combines dense and BM25 candidates using RRF.
The vector branch uses `pre_filter`; the integration's text branch applies the
same MongoDB filter immediately after `$search`, before its candidate limit and
RRF. Text metadata filtering therefore does not require extra Atlas Search token
mappings, though this post-search filtering can cost more at scale. Both branches
enforce the same institution, date, product, jurisdiction and confidentiality restrictions.
Index creation is always manual; there is no fallback to dense search on a missing
text index. Dense mode remains available for baseline comparisons.

Existing vector indexes must also include the `institution` filter before running
the updated API. Update the existing definition in Atlas, retaining its vector
dimensions and other fields, and wait for it to be queryable.

Linked circulars are additionally read through a scoped MongoDB query on `doc_type`
and `supersedes`. Complete instruments include their applicability and grandfathering
clauses, even when their semantic rank falls outside `top_k`. They appear separately
as `amendments` in retrieval responses; `results` still respects `top_k`. No embedding
or source-document rewrite is required for this read-path change.
Circular-to-circular links are followed until no new document ID remains. Each
discovered instrument is read in full under its institution/document/version
identity and must have consistent source scope metadata across its stored chunks.
Inconsistent dates, product or other source scope fail closed with a service
error; the API does not silently answer from a partial circular. This validation
cannot detect an entirely absent chunk without a source ingestion manifest.

References: [LangChain MongoDB hybrid retriever](https://langchain-mongodb.readthedocs.io/en/latest/_modules/langchain_mongodb/retrievers/hybrid_search.html),
[MongoDB text-search stage](https://langchain-mongodb.readthedocs.io/en/latest/_modules/langchain_mongodb/pipelines.html).

## Parent sections collection

Whole sections live in a second, plain collection named by `MONGODB_PARENT_COLLECTION` (default `policy_sections`), keyed by `parent_id` (`<doc_id>_s<NN>`) in `_id`. It is not embedded and needs no search index. MongoDB creates it on the first ingest.

## Regular index for stale-chunk removal

After each document, ingestion deletes that document's leftover chunks with a query on `doc_id`. At eight documents a collection scan is fine. At scale, add a regular (not search) index on the chunk collection:

```json
{ "doc_id": 1 }
```
