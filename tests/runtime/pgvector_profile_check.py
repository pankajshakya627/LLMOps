"""Real pgvector checks; run explicitly against the local configured PostgreSQL service."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.core.config import Settings, get_settings
from app.database import feedback
from app.database.mongo import (
    delete_stale_chunks,
    get_parent_store,
    get_vector_store,
    retire_document,
)
from app.database.postgres import connect, initialize
from app.database.retrieval import build_amendment_search, resolve_reference_contexts
from app.main import create_app
from app.models.answer import AnswerResponse
from app.models.feedback import FeedbackRecord, FeedbackReview
from app.models.retrieval import RetrieveRequest, RetrieveTimings


class FixedEmbedding(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


@pytest.fixture
def pg_settings() -> Any:
    token = uuid4().hex
    settings = get_settings().model_copy(
        update={
            "storage_backend": "pgvector",
            "mongodb_uri": None,
            "embedding_model": "fixture-model",
            "embedding_profile": "fixture-v1",
            "embedding_dimensions": 3,
            "mongodb_collection": f"test_chunks_{token}",
            "mongodb_parent_collection": f"test_parents_{token}",
            "institution": f"test_{token}",
        }
    )
    initialize(settings)
    try:
        yield settings
    finally:
        with connect(settings) as db:
            names = [settings.mongodb_collection, settings.mongodb_parent_collection]
            db.execute("DELETE FROM nexa_documents WHERE namespace=ANY(%s::text[])", (names,))
            db.execute("DELETE FROM nexa_corpora WHERE name=ANY(%s::text[])", (names,))
            db.execute("DELETE FROM nexa_feedback WHERE institution=%s", (settings.institution,))


def metadata(s: Settings, **changes: Any) -> dict[str, Any]:
    return {
        "institution": s.institution,
        "jurisdiction": s.jurisdiction,
        "confidentiality_level": s.confidentiality_level,
        "product_id": "NEXA-HL",
        "doc_id": "POL-HL",
        "policy_version": "3",
        "title": "Home loan",
        "clause": "4.1",
        "effective_date": "2026-01-01",
        "effective_to": None,
        "effective_to_search": "9999-12-31",
        "parent_id": "POL-HL_s01",
        "doc_type": "policy",
        "supersedes": None,
        "checksum": "fixed",
        **changes,
    }


def test_real_vector_search_enforces_all_scope_filters_and_parent_order(
    pg_settings: Settings,
) -> None:
    s = pg_settings
    store = get_vector_store(s, FixedEmbedding())
    documents = [Document(id="valid", page_content="Maximum 7.5 crore", metadata=metadata(s))]
    for key, changes in {
        "foreign": {"institution": "OtherBank"},
        "expired": {"effective_to_search": "2025-01-01"},
        "future": {"effective_date": "2027-01-01"},
        "product": {"product_id": "NEXA-PL"},
        "jurisdiction": {"jurisdiction": "OTHER"},
        "confidential": {"confidentiality_level": "restricted"},
    }.items():
        documents.append(Document(id=key, page_content="Excluded", metadata=metadata(s, **changes)))
    store.add_documents(documents, ids=[d.id for d in documents])
    filters = {
        k: metadata(s)[k]
        for k in ("institution", "jurisdiction", "confidentiality_level", "product_id")
    }
    filters.update(
        effective_date={"$lte": "2026-10-01"}, effective_to_search={"$gte": "2026-10-01"}
    )
    results = store.similarity_search_with_score("max", k=20, pre_filter=filters)
    assert [doc.id for doc, _ in results] == ["valid"]
    assert results[0][1] == pytest.approx(1)
    assert len(store.get_by_ids(["valid", "missing"])) == 1
    parents = get_parent_store(s)
    parents.mset([("POL-HL_s01", documents[0]), ("literal_%", documents[0])])
    assert parents.mget(["missing", "POL-HL_s01"])[0] is None
    assert parents.mget(["POL-HL_s01"])[0].page_content == "Maximum 7.5 crore"
    assert list(parents.yield_keys(prefix="literal_%")) == ["literal_%"]
    parents.mdelete(["literal_%"])
    assert list(parents.yield_keys(prefix="literal_%")) == []
    initialize(s)
    assert store.get_by_ids(["valid"])[0].page_content == "Maximum 7.5 crore"


def test_profile_change_is_rejected_before_embedding(pg_settings: Settings) -> None:
    get_vector_store(pg_settings, FixedEmbedding())
    with pytest.raises(ValueError, match="Incompatible"):
        get_vector_store(
            pg_settings.model_copy(update={"embedding_dimensions": 4}), FixedEmbedding()
        )


def test_stale_cleanup_and_retirement_preserve_foreign_scope(pg_settings: Settings) -> None:
    s = pg_settings
    store = get_vector_store(s, FixedEmbedding())
    docs = [
        Document(id=key, page_content=key, metadata=metadata(s, **changes))
        for key, changes in [("keep", {}), ("stale", {}), ("foreign", {"institution": "OtherBank"})]
    ]
    store.add_documents(docs, ids=[d.id for d in docs])
    assert delete_stale_chunks(store.collection, "POL-HL", ["keep"]) == 1
    assert {d.id for d in store.get_by_ids(["keep", "stale", "foreign"])} == {"keep", "foreign"}
    get_parent_store(s).mset([("parent", docs[0])])
    assert retire_document(s, "POL-HL") == {"chunks_removed": 1, "parents_removed": 1}
    assert store.get_by_ids(["foreign"])


def test_linked_circular_and_golden_context_use_postgres(pg_settings: Settings) -> None:
    s = pg_settings
    store = get_vector_store(s, FixedEmbedding())
    docs = [
        Document(id="base", page_content="Base policy", metadata=metadata(s)),
        Document(
            id="circ",
            page_content="Fee 0.30%",
            metadata=metadata(
                s,
                doc_id="CIR-1",
                doc_type="circular",
                supersedes="POL-HL (clause 6.2)",
                clause="6.2",
            ),
        ),
    ]
    store.add_documents(docs, ids=[d.id for d in docs])
    assert resolve_reference_contexts(s, [{"doc_id": "POL-HL", "clause": "4.1"}]) == ["Base policy"]
    circulars = asyncio.run(
        build_amendment_search(s).ainvoke(
            {"doc_ids": ["POL-HL"], "pre_filter": {"institution": s.institution}}
        )
    )
    assert [d.page_content for d in circulars] == ["Fee 0.30%"]
    store.add_documents(
        [
            Document(
                id="bad",
                page_content="Hidden bad scope",
                metadata=metadata(
                    s,
                    doc_id="CIR-1",
                    doc_type="circular",
                    supersedes="POL-HL (clause 6.2)",
                    jurisdiction="OTHER",
                ),
            )
        ],
        ids=["bad"],
    )
    with pytest.raises(ValueError, match="Inconsistent amendment"):
        asyncio.run(
            build_amendment_search(s).ainvoke(
                {
                    "doc_ids": ["POL-HL"],
                    "pre_filter": {"institution": s.institution, "jurisdiction": s.jurisdiction},
                }
            )
        )


def test_feedback_idempotency_scope_and_review_transition(pg_settings: Settings) -> None:
    s = pg_settings
    request = RetrieveRequest(query="Maximum loan?", as_of="2026-10-01")
    response = AnswerResponse(
        as_of=request.as_of,
        status="insufficient_evidence",
        answer="No evidence",
        generation_ms=0,
        citations=[],
        retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
    )
    record = FeedbackRecord(
        request=request,
        response=response,
        helpful=False,
        feedback_id=uuid4(),
        created_at=datetime.now(UTC),
    )
    assert feedback.save_feedback(record, s) is None
    assert feedback.save_feedback(record, s) == record
    assert feedback.get_feedback(record.feedback_id, s) == record
    assert feedback.list_feedback(s, 10) == [record]
    assert (
        feedback.get_feedback(record.feedback_id, s.model_copy(update={"institution": "OtherBank"}))
        is None
    )
    review = FeedbackReview(status="accepted", reviewer="SME", review_note="Source checked")
    assert feedback.review_feedback(record.feedback_id, review, s)
    assert not feedback.review_feedback(record.feedback_id, review, s)
    assert feedback.get_feedback(record.feedback_id, s).status == "accepted"


def test_fastapi_retrieval_uses_pgvector_without_atlas(
    pg_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.services import retrieval

    s = pg_settings
    store = get_vector_store(s, FixedEmbedding())
    store.add_documents(
        [Document(id="valid", page_content="Maximum loan 7.5 crore", metadata=metadata(s))],
        ids=["valid"],
    )
    monkeypatch.setattr(retrieval, "get_embeddings", lambda _: FixedEmbedding())
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: s
    with TestClient(app) as client:
        assert client.get("/ready").status_code == 200
        result = client.post(
            "/retrieve",
            json={"query": "Maximum loan?", "as_of": "2026-10-01", "product_id": "NEXA-HL"},
        )
    assert result.status_code == 200
    assert result.json()["results"][0]["citation"]["doc_id"] == "POL-HL"


def test_ingestion_is_idempotent_and_updates_changed_chunks(
    pg_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    from unstructured.documents.elements import NarrativeText, Title

    from app.chains import ingestion
    from app.models.ingestion import IngestRequest

    class CountingEmbedding(FixedEmbedding):
        count = 0

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            self.count += len(texts)
            return super().embed_documents(texts)

    elements = [Title("4. Loan terms"), NarrativeText("4.1 Maximum amount. 7.5 crore.")]
    monkeypatch.setattr(ingestion, "parse_document", lambda _: elements)
    s = pg_settings
    embedding = CountingEmbedding()
    vector = get_vector_store(s, embedding)
    chain = ingestion.build_ingestion_chain(vector, get_parent_store(s), s)
    request = IngestRequest(
        source_path="synthetic.md",
        doc_id="POL-HL",
        title="Home Loan",
        institution=s.institution,
        product_id="NEXA-HL",
        policy_version="3",
        effective_date="2026-01-01",
        jurisdiction=s.jurisdiction,
        doc_type="policy",
        confidentiality_level=s.confidentiality_level,
    )
    first = asyncio.run(chain.ainvoke({"request": request}))
    calls = embedding.count
    second = asyncio.run(chain.ainvoke({"request": request}))
    assert first.embedded_count > 0
    assert second.embedded_count == 0 and second.unchanged_count == first.chunk_count
    assert embedding.count == calls
    elements[1] = NarrativeText("4.1 Maximum amount. 8 crore.")
    third = asyncio.run(chain.ainvoke({"request": request}))
    assert third.embedded_count == 1
    assert "8 crore" in vector.get_by_ids(third.chunk_ids)[0].page_content
