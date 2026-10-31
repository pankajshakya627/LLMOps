"""Lab 2: run the real ingestion chain in memory with a counting fake embedding model.

Run from the project root: uv run --no-sync python -m training.session2.ingest_twin
No network, database or model key is used.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.stores import InMemoryStore
from langchain_core.vectorstores import InMemoryVectorStore

from app.chains.ingestion import build_ingestion_chain
from app.core.config import Settings
from app.services.ingestion import requests_from_register
from training.console import say


class CountingEmbedding(DeterministicFakeEmbedding):
    """A fake embedding model that counts how many texts it was asked to embed (no network)."""

    embedded: int = 0

    def embed_documents(self, texts):
        self.embedded += len(texts)
        return super().embed_documents(texts)


settings = Settings(
    _env_file=None,
    mongodb_uri="mongodb://unused",
    mongodb_db="d",
    mongodb_collection="c",
    openai_api_key="unused",
    institution="NexaBank",
    jurisdiction="IN",
    confidentiality_level="internal",
)
request = next(
    r
    for r in requests_from_register(Path("nexa_synthetic_data/document_register.json"), settings)
    if r.doc_id == "POL-HL-V3"
)

embeddings = CountingEmbedding(size=8)
store, parents = InMemoryVectorStore(embeddings), InMemoryStore()


def run(config: Settings, label: str):
    before = embeddings.embedded
    response = asyncio.run(
        build_ingestion_chain(store, parents, config).ainvoke({"request": request})
    )
    say(
        f"{label:<34} chunks={response.chunk_count:>3} embedded={response.embedded_count:>3} "
        f"unchanged={response.unchanged_count:>3} (embedding calls: {embeddings.embedded - before})"
    )
    return response


first = run(settings, "run 1: first ingest")
run(settings, "run 2: same data again")
run(
    settings.model_copy(update={"embedding_model": "text-embedding-3-large"}),
    "run 3: embedding model changed",
)
run(
    settings.model_copy(update={"embedding_model": "text-embedding-3-large"}),
    "run 4: ... and run once more",
)

chunk = store.get_by_ids([first.chunk_ids[8]])[0]
say("\n--- one stored chunk ---")
say("id:", chunk.id)
say(chunk.page_content[:150].replace("\n", " / "))
keep = (
    "doc_id",
    "policy_version",
    "effective_date",
    "effective_to_search",
    "clause",
    "parent_id",
    "section_type",
    "checksum",
)
for key in keep:
    say(f"  {key:<20}", str(chunk.metadata[key])[:40])
section = parents.mget([chunk.metadata["parent_id"]])[0]
assert section is not None
say("\nparent section", chunk.metadata["parent_id"], "has", len(section.page_content), "characters")
