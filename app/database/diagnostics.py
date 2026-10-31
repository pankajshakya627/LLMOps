"""Read-only storage observations for the Session 5 teaching examples."""

from __future__ import annotations

from typing import Any

from pymongo import timeout

from app.core.config import Settings
from app.database.mongo import _database


def read_rag_snapshot(settings: Settings) -> dict[str, Any]:
    """Read index definitions and chunk payloads, replacing vectors with their lengths.

    The lesson caller runs this synchronous database work in a worker thread.
    """
    if settings.storage_backend == "pgvector":
        from app.database.postgres import connect

        with connect(settings) as db:
            rows = db.execute(
                "SELECT namespace,id,text,metadata,vector_dims(embedding) FROM nexa_documents WHERE namespace=ANY(%s::text[])",
                ([settings.mongodb_collection, settings.mongodb_parent_collection],),
            ).fetchall()
        chunks = [
            {**metadata, "_id": key, "text": text, "_actual_dimensions": dimensions}
            for namespace, key, text, metadata, dimensions in rows
            if namespace == settings.mongodb_collection
        ]
        parents = [
            {**metadata, "_id": key, "text": text}
            for namespace, key, text, metadata, _ in rows
            if namespace == settings.mongodb_parent_collection
        ]
        return {
            "indexes": [],
            "chunks": chunks,
            "parents": parents,
            "backend": "pgvector",
            "search": "exact cosine",
        }
    collection = _database(settings)[settings.mongodb_collection]
    with timeout(30):
        parents = list(
            _database(settings)[settings.mongodb_parent_collection].find({}, {"embedding": 0})
        )
        indexes = [
            {
                key: row.get(key)
                for key in ("name", "type", "status", "queryable", "latestDefinition")
            }
            for row in collection.list_search_indexes()
        ]
        chunks = list(
            collection.aggregate(
                [
                    {
                        "$set": {
                            "_actual_dimensions": {
                                "$cond": [
                                    {"$isArray": "$embedding"},
                                    {"$size": "$embedding"},
                                    -1,
                                ]
                            }
                        }
                    },
                    {"$project": {"embedding": 0}},
                ]
            )
        )
    return {"indexes": indexes, "chunks": chunks, "parents": parents}
