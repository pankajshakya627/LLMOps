"""PostgreSQL document storage and exact cosine retrieval using pgvector."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Iterator, Sequence
from math import isfinite
from typing import Any

import psycopg
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.stores import BaseStore
from langchain_core.vectorstores import VectorStore
from psycopg.types.json import Jsonb

from app.core.config import Settings, get_settings


def connect(settings: Settings) -> psycopg.Connection[Any]:
    if settings.postgres_dsn is None:
        raise ValueError("POSTGRES_DSN is required")
    return psycopg.connect(
        settings.postgres_dsn.get_secret_value(),
        connect_timeout=3,
        options="-c statement_timeout=30000",
    )


def initialize(settings: Settings) -> None:
    """Explicit provisioning; request paths never create extensions or tables."""
    with connect(settings) as db:
        db.execute("CREATE EXTENSION IF NOT EXISTS vector")
        db.execute("""CREATE TABLE IF NOT EXISTS nexa_corpora (
            name text PRIMARY KEY, identity jsonb NOT NULL)""")
        db.execute("""CREATE TABLE IF NOT EXISTS nexa_documents (
            namespace text NOT NULL REFERENCES nexa_corpora(name),
            id text NOT NULL, text text NOT NULL, metadata jsonb NOT NULL,
            embedding vector, PRIMARY KEY(namespace, id))""")
        db.execute("""CREATE TABLE IF NOT EXISTS nexa_feedback (
            institution text NOT NULL, id text NOT NULL, payload jsonb NOT NULL,
            PRIMARY KEY(institution, id))""")


def ensure_profile(settings: Settings) -> None:
    if settings.mongodb_collection == settings.mongodb_parent_collection:
        raise ValueError("Chunk and parent namespaces must differ")
    if not settings.embedding_profile:
        raise ValueError("pgvector requires an explicit EMBEDDING_PROFILE")
    identity = {
        "model": settings.embedding_model,
        "dimensions": settings.embedding_dimensions,
        "profile": settings.embedding_profile,
    }
    with connect(settings) as db:
        for name, kind in (
            (settings.mongodb_collection, "chunks"),
            (settings.mongodb_parent_collection, "parents"),
        ):
            expected = {**identity, "kind": kind}
            db.execute(
                "INSERT INTO nexa_corpora VALUES (%s,%s) ON CONFLICT DO NOTHING",
                (name, Jsonb(expected)),
            )
            row = db.execute("SELECT identity FROM nexa_corpora WHERE name=%s", (name,)).fetchone()
            if row is None or row[0] != expected:
                raise ValueError("Incompatible embedding profile; use separate namespaces")


def compile_filter(query: dict[str, Any]) -> tuple[str, list[Any]]:
    """Translate only the application's metadata filter vocabulary; bind every value."""
    clauses: list[str] = []
    values: list[Any] = []
    for key, value in query.items():
        if key in {"$and", "$or"}:
            children = [compile_filter(item) for item in value]
            clauses.append(
                "(" + (" AND " if key == "$and" else " OR ").join(sql for sql, _ in children) + ")"
                if children
                else ("TRUE" if key == "$and" else "FALSE")
            )
            values.extend(param for _, params in children for param in params)
        elif key.startswith("$"):
            raise ValueError("Unsupported logical filter")
        elif isinstance(value, dict):
            for op, operand in value.items():
                if op in {"$lte", "$gte"}:
                    clauses.append(
                        "COALESCE(metadata ->> %s "
                        + ("<=" if op == "$lte" else ">=")
                        + " %s, FALSE)"
                    )
                    values.extend([key, operand])
                elif op == "$in":
                    clauses.append("COALESCE(metadata ->> %s = ANY(%s::text[]), FALSE)")
                    values.extend([key, operand])
                elif op == "$regex":
                    clauses.append("COALESCE(metadata ->> %s ~ %s, FALSE)")
                    values.extend([key, operand])
                else:
                    raise ValueError("Unsupported metadata filter")
        else:
            clauses.append("COALESCE(metadata -> %s = %s::jsonb, FALSE)")
            values.extend([key, Jsonb(value)])
    return " AND ".join(clauses) or "TRUE", values


def vector_literal(vector: list[float], dimensions: int) -> str:
    if (
        len(vector) != dimensions
        or any(
            isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v)
            for v in vector
        )
        or not any(v != 0 for v in vector)
    ):
        raise ValueError("Embedding must be finite, nonzero and match the configured dimensions")
    return json.dumps(vector)


def find_chunks(settings: Settings, query: dict[str, Any]) -> list[dict[str, Any]]:
    where, params = compile_filter(query)
    with connect(settings) as db:
        rows = db.execute(
            "SELECT id, text, metadata FROM nexa_documents WHERE namespace=%s AND "
            + where
            + " ORDER BY id",
            [settings.mongodb_collection, *params],
        ).fetchall()
    return [{**metadata, "_id": key, "text": text} for key, text, metadata in rows]


class PostgresVectorStore(VectorStore):
    def __init__(self, settings: Settings, embedding: Embeddings) -> None:
        ensure_profile(settings)
        self.settings = settings
        self.embedding = embedding
        # Ingestion passes this handle to the shared stale-chunk cleanup function.
        self.collection = self

    @property
    def embeddings(self) -> Embeddings:
        return self.embedding

    @classmethod
    def from_texts(
        cls,
        texts: list[str],
        embedding: Embeddings,
        metadatas: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> PostgresVectorStore:
        store = cls(kwargs.pop("settings"), embedding)
        store.add_texts(texts, metadatas, **kwargs)
        return store

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: list[dict[str, Any]] | None = None,
        *,
        ids: list[str] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        items = list(texts)
        if ids is None or metadatas is None or not (len(ids) == len(items) == len(metadatas)):
            raise ValueError("Explicit IDs and metadata are required for every chunk")
        vectors = self.embedding.embed_documents(items)
        if len(vectors) != len(items):
            raise ValueError("Embedding count mismatch")
        rows = [
            (
                self.settings.mongodb_collection,
                key,
                text,
                Jsonb(metadata),
                vector_literal(vector, self.settings.embedding_dimensions),
            )
            for key, text, metadata, vector in zip(ids, items, metadatas, vectors, strict=True)
        ]
        with connect(self.settings) as db, db.cursor() as cursor:
            cursor.executemany(
                """INSERT INTO nexa_documents VALUES (%s,%s,%s,%s,%s::vector)
                    ON CONFLICT(namespace,id) DO UPDATE SET text=EXCLUDED.text,
                    metadata=EXCLUDED.metadata, embedding=EXCLUDED.embedding""",
                rows,
            )
        return ids

    def get_by_ids(self, ids: Sequence[str], /) -> list[Document]:
        with connect(self.settings) as db:
            rows = db.execute(
                """SELECT id,text,metadata FROM nexa_documents
                WHERE namespace=%s AND id=ANY(%s::text[])""",
                (self.settings.mongodb_collection, list(ids)),
            ).fetchall()
        return [
            Document(id=key, page_content=text, metadata=metadata) for key, text, metadata in rows
        ]

    def similarity_search_with_score(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[tuple[Document, float]]:
        vector = vector_literal(
            self.embedding.embed_query(query), self.settings.embedding_dimensions
        )
        where, params = compile_filter(kwargs.get("pre_filter", {}))
        with connect(self.settings) as db:
            # shortcut: exact search suits the reference corpus; benchmark HNSW before scaling.
            rows = db.execute(
                """SELECT id,text,metadata,1-(embedding <=> %s::vector) AS score
                FROM nexa_documents WHERE namespace=%s AND embedding IS NOT NULL AND """
                + where
                + " ORDER BY embedding <=> %s::vector, id LIMIT %s",
                [vector, self.settings.mongodb_collection, *params, vector, k],
            ).fetchall()
        return [
            (Document(id=key, page_content=text, metadata=metadata), float(score))
            for key, text, metadata, score in rows
        ]

    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> list[Document]:
        return [doc for doc, _ in self.similarity_search_with_score(query, k, **kwargs)]

    def delete_stale(self, doc_id: str, keep_ids: list[str]) -> int:
        with connect(self.settings) as db:
            result = db.execute(
                """DELETE FROM nexa_documents WHERE namespace=%s
                AND metadata->>'doc_id'=%s AND metadata->>'institution'=%s
                AND metadata->>'jurisdiction'=%s AND metadata->>'confidentiality_level'=%s
                AND NOT(id=ANY(%s::text[]))""",
                (
                    self.settings.mongodb_collection,
                    doc_id,
                    self.settings.institution,
                    self.settings.jurisdiction,
                    self.settings.confidentiality_level,
                    keep_ids,
                ),
            )
            return result.rowcount


class PostgresParentStore(BaseStore[str, Document]):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.namespace = settings.mongodb_parent_collection

    def mget(self, keys: Sequence[str]) -> list[Document | None]:
        with connect(self.settings) as db:
            rows = db.execute(
                "SELECT id,text,metadata FROM nexa_documents WHERE namespace=%s AND id=ANY(%s::text[])",
                (self.namespace, list(keys)),
            ).fetchall()
        found = {
            key: Document(id=key, page_content=text, metadata=metadata)
            for key, text, metadata in rows
        }
        return [found.get(key) for key in keys]

    def mset(self, key_value_pairs: Sequence[tuple[str, Document]]) -> None:
        with connect(self.settings) as db, db.cursor() as cursor:
            cursor.executemany(
                """INSERT INTO nexa_documents(namespace,id,text,metadata)
                    VALUES (%s,%s,%s,%s) ON CONFLICT(namespace,id) DO UPDATE
                    SET text=EXCLUDED.text,metadata=EXCLUDED.metadata""",
                [
                    (self.namespace, key, doc.page_content, Jsonb(doc.metadata))
                    for key, doc in key_value_pairs
                ],
            )

    def mdelete(self, keys: Sequence[str]) -> None:
        with connect(self.settings) as db:
            db.execute(
                "DELETE FROM nexa_documents WHERE namespace=%s AND id=ANY(%s::text[])",
                (self.namespace, list(keys)),
            )

    def yield_keys(self, *, prefix: str | None = None) -> Iterator[str]:
        with connect(self.settings) as db:
            rows = db.execute(
                """SELECT id FROM nexa_documents WHERE namespace=%s
                AND starts_with(id,%s) ORDER BY id""",
                (self.namespace, prefix or ""),
            ).fetchall()
        yield from (row[0] for row in rows)


def retire_document(settings: Settings, doc_id: str) -> dict[str, int]:
    result = {}
    with connect(settings) as db:
        for kind, name in (
            ("chunks", settings.mongodb_collection),
            ("parents", settings.mongodb_parent_collection),
        ):
            deleted = db.execute(
                """DELETE FROM nexa_documents WHERE namespace=%s
                AND metadata->>'doc_id'=%s AND metadata->>'institution'=%s
                AND metadata->>'jurisdiction'=%s AND metadata->>'confidentiality_level'=%s""",
                (
                    name,
                    doc_id,
                    settings.institution,
                    settings.jurisdiction,
                    settings.confidentiality_level,
                ),
            )
            result[kind + "_removed"] = deleted.rowcount
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision the local PostgreSQL/pgvector schema")
    parser.add_argument("action", choices=["init"])
    parser.parse_args()
    initialize(get_settings())
    print("PostgreSQL schema and pgvector extension are ready")


if __name__ == "__main__":
    main()
