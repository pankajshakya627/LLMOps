from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from functools import lru_cache
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.docstores import MongoDBDocStore
from pymongo import MongoClient, ReplaceOne, timeout
from pymongo.database import Database

from app.core.config import OPENAI_BASE_URL, Settings


@lru_cache
def _client(uri: str) -> MongoClient[Any]:
    return MongoClient(uri)


def _database(settings: Settings) -> Database[Any]:
    if settings.mongodb_uri is None:
        raise ValueError("MONGODB_URI is required for mongodb storage")
    return _client(settings.mongodb_uri.get_secret_value())[settings.mongodb_db]


def ping_database(settings: Settings) -> None:
    """Bound the readiness probe without shortening normal query deadlines."""
    if settings.storage_backend == "pgvector":
        from app.database.postgres import connect

        with connect(settings) as db:
            db.execute("SELECT 1 FROM nexa_documents LIMIT 1")
        return
    with timeout(2):
        _database(settings).command("ping")


def ensure_embedding_profile(settings: Settings) -> None:
    """Reject mixed stores before query embedding or any ingestion mutation."""
    if settings.storage_backend == "pgvector":
        from app.database.postgres import ensure_profile

        ensure_profile(settings)
        return
    if settings.mongodb_collection == settings.mongodb_parent_collection:
        raise ValueError("Chunk and parent collections must differ")
    legacy = settings.embedding_base_url == OPENAI_BASE_URL and not settings.embedding_profile
    if not legacy and not settings.embedding_profile:
        raise ValueError("Custom embedding endpoint requires EMBEDDING_PROFILE")
    identity: dict[str, Any] = {
        "embedding_model": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
        "embedding_profile": {"$exists": False} if legacy else settings.embedding_profile,
    }
    parent_identity = {"embedding_profile": {"$exists": False}} if legacy else identity
    database = _database(settings)
    # shortcut: scan metadata per use; add an immutable corpus manifest before scaling ingestion.
    with timeout(2):
        for name, expected in (
            (settings.mongodb_collection, identity),
            (settings.mongodb_parent_collection, parent_identity),
        ):
            if database[name].find_one({"$nor": [expected]}, {"_id": 1}) is not None:
                raise ValueError("Incompatible or unknown embedding profile; use separate stores")


def get_vector_store(settings: Settings, embedding: Embeddings) -> Any:
    """Chunk store shared by the write path and the read path.

    The Atlas Vector Search index is created manually; see indexes.md.
    """
    if settings.storage_backend == "pgvector":
        from app.database.postgres import PostgresVectorStore

        return PostgresVectorStore(settings, embedding)
    ensure_embedding_profile(settings)
    return MongoDBAtlasVectorSearch(
        collection=_database(settings)[settings.mongodb_collection],
        embedding=embedding,
        index_name=settings.vector_index_name,
        text_key="text",
        embedding_key="embedding",
        relevance_score_fn="cosine",
        auto_create_index=False,
    )


class UpsertingParentStore(MongoDBDocStore):
    """Keep existing section keys readable while replacing their contents."""

    def insert_many(
        self, texts: Iterable[str], metadatas: Iterable[dict[str, Any]], ids: list[str]
    ) -> None:
        operations = [
            ReplaceOne(
                {"_id": key},
                {**metadata, "_id": key, self._text_key: text},
                upsert=True,
            )
            for key, text, metadata in zip(ids, texts, metadatas, strict=True)
        ]
        if operations:
            self.collection.bulk_write(operations)

    def yield_keys(self, *, prefix: str | None = None) -> Iterator[str]:
        # The integration treats prefixes as regex; BaseStore callers expect literals.
        return super().yield_keys(prefix=re.escape(prefix) if prefix is not None else None)


def get_parent_store(settings: Settings) -> Any:
    """Whole sections keyed by parent_id, in their own collection. Not embedded."""
    if settings.storage_backend == "pgvector":
        from app.database.postgres import PostgresParentStore

        return PostgresParentStore(settings)
    return UpsertingParentStore(_database(settings)[settings.mongodb_parent_collection])


def delete_stale_chunks(collection: Any, doc_id: str, keep_ids: list[str]) -> int:
    """Retire chunks of `doc_id` that the latest ingest no longer produced."""
    from app.database.postgres import PostgresVectorStore

    if isinstance(collection, PostgresVectorStore):
        return collection.delete_stale(doc_id, keep_ids)
    result = collection.delete_many({"doc_id": doc_id, "_id": {"$nin": keep_ids}})
    return result.deleted_count


def retire_document(settings: Settings, doc_id: str) -> dict[str, int]:
    """Explicitly retire one withdrawn document from both stores, scoped to this corpus."""
    if settings.storage_backend == "pgvector":
        from app.database.postgres import retire_document as retire_postgres

        return retire_postgres(settings, doc_id)
    scope = {
        "doc_id": doc_id,
        "institution": settings.institution,
        "jurisdiction": settings.jurisdiction,
        "confidentiality_level": settings.confidentiality_level,
    }
    database = _database(settings)
    return {
        "chunks_removed": database[settings.mongodb_collection].delete_many(scope).deleted_count,
        "parents_removed": database[settings.mongodb_parent_collection]
        .delete_many(scope)
        .deleted_count,
    }
