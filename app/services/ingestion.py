from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

import structlog

from app.chains.embeddings import get_embeddings
from app.chains.ingestion import build_ingestion_chain
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.database.mongo import (
    delete_stale_chunks,
    get_parent_store,
    get_vector_store,
    retire_document,
)
from app.models.ingestion import IngestRequest, IngestResponse

logger = structlog.get_logger()

DOC_TYPES = {"POL": "policy", "CIR": "circular"}


def _verify_source(path: Path, entry: dict[str, Any]) -> str:
    """Refuse a file whose bytes differ from the register's recorded sha256."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        raise ValueError(f"{entry['doc_id']}: file sha256 does not match the document register")
    return str(path)


def requests_from_register(register_path: Path, settings: Settings) -> list[IngestRequest]:
    """One IngestRequest per authoritative document in document_register.json.

    Each source file must match the register's sha256 before it can be ingested.
    """
    return [
        IngestRequest(
            source_path=_verify_source(register_path.parent / entry["file"], entry),
            doc_id=entry["doc_id"],
            title=entry["title"],
            institution=settings.institution,
            product_id=entry["product_id"],
            policy_version=entry["version"],
            effective_date=entry["effective_from"],
            effective_to=entry["effective_to"],
            supersedes=entry["supersedes"],
            jurisdiction=settings.jurisdiction,
            doc_type=DOC_TYPES[entry["doc_id"].split("-")[0]],
            confidentiality_level=settings.confidentiality_level,
        )
        for entry in json.loads(register_path.read_text())
        if entry["authoritative"]
    ]


class IngestionFailed(RuntimeError):
    """Some documents failed; the others were committed. `failed` maps doc_id to error type."""

    def __init__(self, failed: dict[str, str], responses: list[IngestResponse]) -> None:
        super().__init__(f"Ingestion failed for {len(failed)} document(s): {sorted(failed)}")
        self.failed = failed
        self.responses = responses


async def ingest(requests: list[IngestRequest]) -> list[IngestResponse]:
    """Embed only new or changed chunks, then retire chunks the source no longer has.

    One bad document does not stop the rest: each is committed on its own, a failed document
    keeps its previously indexed chunks, and the run ends with IngestionFailed.
    """
    settings = get_settings()
    vector_store = await asyncio.to_thread(get_vector_store, settings, get_embeddings(settings))
    chain = build_ingestion_chain(vector_store, get_parent_store(settings), settings)
    responses: list[IngestResponse] = []
    failed: dict[str, str] = {}
    for request in requests:
        try:
            response = await chain.ainvoke({"request": request})
        except Exception as exc:  # noqa: BLE001 - isolate one document; reported after the run
            failed[request.doc_id] = type(exc).__name__
            logger.error(
                "document_ingest_failed", doc_id=request.doc_id, error_type=type(exc).__name__
            )
            continue
        removed = await asyncio.to_thread(
            delete_stale_chunks, vector_store.collection, request.doc_id, response.chunk_ids
        )
        logger.info(
            "document_ingested",
            doc_id=response.doc_id,
            chunk_count=response.chunk_count,
            embedded_count=response.embedded_count,
            unchanged_count=response.unchanged_count,
            stale_chunks_removed=removed,
            embedding_model=response.embedding_model,
            policy_version=request.policy_version,
            effective_date=request.effective_date.isoformat(),
        )
        responses.append(response)
    if failed:
        raise IngestionFailed(failed, responses)
    return responses


def main() -> None:
    """Ingest a register, or explicitly retire one document withdrawn from it."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("register", type=Path)
    parser.add_argument("--retire-doc", help="Delete a withdrawn document from both MongoDB stores")
    args = parser.parse_args()
    settings = get_settings()
    configure_logging(settings.log_level)
    if args.retire_doc:
        entries = json.loads(args.register.read_text())
        if any(entry["doc_id"] == args.retire_doc and entry["authoritative"] for entry in entries):
            parser.error("Cannot retire a document still marked authoritative in the register")
        counts = retire_document(settings, args.retire_doc)
        logger.info("document_retired", doc_id=args.retire_doc, **counts)
    else:
        try:
            asyncio.run(ingest(requests_from_register(args.register, settings)))
        except IngestionFailed as exc:
            logger.error("ingestion_incomplete", failed=exc.failed, ingested=len(exc.responses))
            raise SystemExit(1) from None


if __name__ == "__main__":
    main()
