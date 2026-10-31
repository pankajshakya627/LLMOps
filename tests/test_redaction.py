from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.stores import InMemoryStore
from langchain_core.vectorstores import InMemoryVectorStore
from unstructured.documents.elements import NarrativeText, Title

from app.chains.chunking import chunk_by_clause
from app.chains.ingestion import build_ingestion_chain
from app.chains.parsing import parse_document
from app.chains.redaction import redact
from app.core.config import Settings
from app.services.ingestion import requests_from_register

REGISTER = Path("nexa_synthetic_data/document_register.json")


def test_redact_replaces_typed_identifiers_and_counts_them() -> None:
    text = "Contact priya@example.com or +91 98765 43210. PAN ABCDE1234F, Aadhaar 1234 5678 9012."
    clean, counts = redact(text)
    assert "priya@example.com" not in clean and "ABCDE1234F" not in clean
    assert "9012" not in clean and "98765" not in clean
    assert counts == {"EMAIL": 1, "PHONE": 1, "PAN": 1, "AADHAAR": 1}
    assert "[REDACTED_PAN]" in clean


def test_policy_amounts_and_clause_numbers_are_not_identifiers() -> None:
    text = "6.2 Processing fee 0.30% (min ₹5,000, max ₹10,000). Loans up to ₹7,50,00,000 for 240 months."
    assert redact(text) == (text, {})


def test_shipped_policy_documents_contain_nothing_to_redact(settings: Settings) -> None:
    for request in requests_from_register(REGISTER, settings):
        chunks = chunk_by_clause(parse_document(request.source_path), 1200, 150)
        assert all(not redact(chunk.text)[1] for chunk in chunks), request.doc_id


def test_ingestion_redacts_before_embedding_and_can_be_disabled(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    elements = [
        Title("1. Scope"),
        NarrativeText("1.1 Contact. Reach the officer at asha.rao@nexabank.example today."),
    ]
    monkeypatch.setattr("app.chains.ingestion.parse_document", lambda _path: elements)
    request = requests_from_register(REGISTER, settings)[0]

    def ingest(config: Settings) -> tuple[str, str]:
        store, parents = InMemoryVectorStore(DeterministicFakeEmbedding(size=8)), InMemoryStore()
        chain = build_ingestion_chain(store, parents, config)
        response = asyncio.run(chain.ainvoke({"request": request}))
        child = store.get_by_ids(response.chunk_ids)[0].page_content
        stored = parents.mget([f"{request.doc_id}_s01"])[0]
        assert stored is not None
        return child, stored.page_content

    child, parent = ingest(settings)
    assert "asha.rao" not in child and "asha.rao" not in parent
    assert "[REDACTED_EMAIL]" in child
    child, _ = ingest(settings.model_copy(update={"redact_pii": False}))
    assert "asha.rao@nexabank.example" in child
