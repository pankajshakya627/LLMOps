from __future__ import annotations

import asyncio
from collections import Counter
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import mongomock
import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.stores import InMemoryStore
from langchain_core.vectorstores import InMemoryVectorStore

from app.chains.ingestion import build_ingestion_chain
from app.core.config import Settings
from app.database import mongo
from app.services.ingestion import requests_from_register


def test_legacy_profile_remains_readable(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    database: Any = mongomock.MongoClient().db
    database[settings.mongodb_collection].insert_one(
        {
            "_id": "old",
            "text": "Policy",
            "embedding_model": settings.embedding_model,
            "embedding_dimensions": settings.embedding_dimensions,
        }
    )
    database[settings.mongodb_parent_collection].insert_one({"_id": "parent", "text": "Policy"})
    monkeypatch.setattr(mongo, "_database", lambda _: database)
    assert (
        mongo.get_vector_store(settings, DeterministicFakeEmbedding(size=8)).collection.name
        == settings.mongodb_collection
    )


@pytest.mark.parametrize(
    "bad",
    [
        {},
        {"embedding_model": "different-model", "embedding_dimensions": 1536},
        {"embedding_model": "text-embedding-3-small", "embedding_dimensions": 1024},
        {
            "embedding_model": "text-embedding-3-small",
            "embedding_dimensions": 1536,
            "embedding_profile": "other-deployment",
        },
    ],
)
def test_mixed_or_unknown_chunks_refused_before_any_embedding_or_write(
    settings: Settings, monkeypatch: pytest.MonkeyPatch, bad: dict[str, Any]
) -> None:
    database: Any = mongomock.MongoClient().db
    chunks = database[settings.mongodb_collection]
    chunks.insert_many(
        [
            {
                "_id": "good",
                "embedding_model": settings.embedding_model,
                "embedding_dimensions": 1536,
            },
            {"_id": "bad", **bad},
        ]
    )
    monkeypatch.setattr(mongo, "_database", lambda _: database)
    embedding = Mock(wraps=DeterministicFakeEmbedding(size=8))
    before = list(chunks.find())
    with pytest.raises(ValueError, match="embedding profile"):
        mongo.get_vector_store(settings, embedding)
    assert list(chunks.find()) == before
    assert not embedding.embed_query.called and not embedding.embed_documents.called


def test_local_profile_cannot_reuse_legacy_parent_store(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    database: Any = mongomock.MongoClient().db
    database[settings.mongodb_parent_collection].insert_one({"_id": "old-parent", "text": "Old"})
    monkeypatch.setattr(mongo, "_database", lambda _: database)
    local = settings.model_copy(
        update={
            "embedding_base_url": "http://127.0.0.1:11434/v1",
            "embedding_profile": "qwen3-local",
            "embedding_model": "qwen3-embedding:0.6b",
            "embedding_dimensions": 1024,
            "mongodb_collection": "local-chunks",
        }
    )
    with pytest.raises(ValueError, match="embedding profile"):
        mongo.get_vector_store(local, DeterministicFakeEmbedding(size=8))
    assert database[settings.mongodb_parent_collection].find_one()["text"] == "Old"
    local.mongodb_parent_collection = "local-parents"
    assert mongo.get_vector_store(local, DeterministicFakeEmbedding(size=8))


def test_custom_profile_is_required_even_for_empty_corpus(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    database: Any = mongomock.MongoClient().db
    monkeypatch.setattr(mongo, "_database", lambda _: database)
    settings.embedding_base_url = "http://127.0.0.1:11434/v1"
    with pytest.raises(ValueError, match="EMBEDDING_PROFILE"):
        mongo.get_vector_store(settings, DeterministicFakeEmbedding(size=8))


@pytest.mark.parametrize("operation", ["ingest", "retrieve"])
def test_application_services_refuse_incompatible_corpus_before_work(
    settings: Settings, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    from app.models.retrieval import RetrieveRequest
    from app.services import ingestion, retrieval

    database: Any = mongomock.MongoClient().db
    database[settings.mongodb_collection].insert_one({"_id": "unknown", "text": "Existing"})
    monkeypatch.setattr(mongo, "_database", lambda _: database)
    monkeypatch.setattr(ingestion, "get_settings", lambda: settings)
    monkeypatch.setattr(retrieval, "retrieval_metrics", Counter())
    before = list(database[settings.mongodb_collection].find())
    with pytest.raises(ValueError, match="embedding profile"):
        if operation == "ingest":
            asyncio.run(ingestion.ingest([]))
        else:
            asyncio.run(
                retrieval.retrieve_policy(
                    RetrieveRequest(query="Limit?", as_of="2026-10-01"), settings
                )
            )
    assert list(database[settings.mongodb_collection].find()) == before


def test_custom_ingestion_stamps_matching_chunk_and_parent_identity(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    local = settings.model_copy(
        update={
            "embedding_profile": "offline-qwen-fixture",
            "embedding_model": "qwen3-embedding:0.6b",
            "embedding_base_url": "http://127.0.0.1:11434/v1",
            "embedding_dimensions": 8,
        }
    )
    embedding = DeterministicFakeEmbedding(size=8)
    chunks = InMemoryVectorStore(embedding)
    parents: InMemoryStore = InMemoryStore()
    request = requests_from_register(Path("nexa_synthetic_data/document_register.json"), local)[0]
    result = asyncio.run(
        build_ingestion_chain(chunks, parents, local).ainvoke({"request": request})
    )
    children = chunks.get_by_ids(result.chunk_ids)
    assert children and parents.store
    database: Any = mongomock.MongoClient().db
    for name, documents in (
        (local.mongodb_collection, children),
        (local.mongodb_parent_collection, list(parents.store.values())),
    ):
        for document in documents:
            assert document.metadata["embedding_profile"] == "offline-qwen-fixture"
            assert document.metadata["embedding_model"] == "qwen3-embedding:0.6b"
            assert document.metadata["embedding_dimensions"] == 8
            database[name].insert_one({"_id": document.id, **document.metadata})
    monkeypatch.setattr(mongo, "_database", lambda _: database)
    assert mongo.get_vector_store(local, embedding)
