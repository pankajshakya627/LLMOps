"""Registered PDFs through real ingestion, date filters, amendments and answer checks.

Embeddings, vector ranking, Mongo transport and generation are offline fakes.
"""

from __future__ import annotations

import asyncio
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import mongomock
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableLambda
from langchain_core.stores import InMemoryStore
from langchain_core.vectorstores import InMemoryVectorStore

from app.chains.answer import build_answer_chain
from app.chains.ingestion import build_ingestion_chain
from app.chains.retrieval import build_retrieval_chain
from app.core.config import Settings
from app.database import retrieval as database
from app.models.retrieval import RetrieveRequest
from app.services.ingestion import requests_from_register
from training.console import say


async def main() -> None:
    settings = Settings(
        _env_file=None,
        mongodb_uri="mongodb://unused",
        mongodb_db="unused",
        mongodb_collection="chunks",
        openai_api_key="unused",
        institution="NexaBank",
        jurisdiction="IN",
        confidentiality_level="internal",
    )
    vectors = InMemoryVectorStore(DeterministicFakeEmbedding(size=8))
    parents = InMemoryStore()
    ingest = build_ingestion_chain(vectors, parents, settings)
    storage: Any = mongomock.MongoClient().db
    for request in requests_from_register(
        Path("nexa_synthetic_data/document_register.json"), settings
    ):
        if request.doc_id in {"POL-HL-V3", "CIR-2026-07"}:
            ingested = await ingest.ainvoke({"request": request})
            for document in await vectors.aget_by_ids(ingested.chunk_ids):
                storage.chunks.insert_one(
                    {"_id": document.id, "text": document.page_content, **document.metadata}
                )

    async def search(
        _query: str, k: int, pre_filter: dict[str, Any]
    ) -> list[tuple[Document, float]]:
        rows = storage.chunks.find(
            {"$and": [pre_filter, {"doc_id": "POL-HL-V3", "clause": "6.2"}]}
        ).limit(k)
        return [
            (
                Document(
                    page_content=row["text"],
                    metadata={
                        key: value for key, value in row.items() if key not in {"_id", "text"}
                    },
                ),
                0.9,
            )
            for row in rows
        ]

    vector = Mock()
    vector.asimilarity_search_with_score = search

    def draft(prompt: Any) -> dict[str, Any]:
        human = str(prompt.to_messages()[-1].content)
        root = ET.fromstring(human.split("</request_data>")[0] + "</request_data>")
        sources = json.loads(root.findtext("retrieved_context") or "[]")
        source = sources[0]
        circular = source["matched_child"]["doc_id"] == "CIR-2026-07"
        fee = "0.30%" if circular else "0.35%"
        assert fee in source["retrieved_context"]
        number = source["evidence_id"]
        return {
            "status": "answered",
            "answer": f"Processing fee {fee} plus GST for the stated sanction date [{number}].",
            "evidence": [{"evidence_id": number, "quote": source["retrieved_context"]}],
        }

    model = Mock(spec=BaseChatModel)
    model.with_structured_output.return_value = RunnableLambda(draft)
    with patch.object(database, "_database", return_value=storage):
        retrieve = build_retrieval_chain(
            vector, parents, settings, amendment_search=database.build_amendment_search(settings)
        )
        chain = build_answer_chain(retrieve, model, settings)
        for day, expected, identifier in (
            ("2026-06-30", "0.35%", "POL-HL-V3"),
            ("2026-07-01", "0.30%", "CIR-2026-07"),
        ):
            result = await chain.ainvoke(
                RetrieveRequest(
                    query=f"What processing fee applies to a NexaHome loan sanctioned on {day}?",
                    as_of=day,
                    product_id="NEXA-HL",
                    top_k=1,
                )
            )
            assert result.status == "answered" and expected in result.answer
            assert result.citations[0].matched_child.doc_id == identifier
            say(f"{day}: fee={expected}; cited={identifier}; exact quote verified")
        empty = await chain.ainvoke(
            RetrieveRequest(query="fee", as_of="2026-07-01", product_id="NEXA-PL")
        )
        assert empty.status == "insufficient_evidence" and not empty.citations
        say("wrong product: insufficient_evidence; no model draft requested")
    say("Real registered PDFs and pipeline controls; ranking/model outputs are fixtures.")
    say("Before-cutoff sanctions retain their fee; the July lookup alone does not change it.")


if __name__ == "__main__":
    asyncio.run(main())
