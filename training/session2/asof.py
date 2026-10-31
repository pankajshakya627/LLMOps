"""Lab 3: show the as-of filter the retrieval chain builds, and which documents are in force.

Run from the project root: uv run --no-sync python -m training.session2.asof
No network, database or model key is used.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from typing import Any, cast

from langchain_core.stores import InMemoryStore
from langchain_core.vectorstores import VectorStore

from app.chains.retrieval import build_retrieval_chain
from app.core.config import Settings
from app.models.retrieval import RetrieveRequest
from training.console import say

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


class SpyStore:
    """Stands in for the vector database and records the filter the retrieval chain builds."""

    def __init__(self) -> None:
        self.filter: dict[str, Any] = {}

    async def asimilarity_search_with_score(
        self, query: str, k: int, pre_filter: dict[str, Any]
    ) -> list[tuple[Any, float]]:
        self.filter = pre_filter
        return []


spy = SpyStore()
chain = build_retrieval_chain(cast(VectorStore, spy), InMemoryStore(), settings)
asyncio.run(
    chain.ainvoke(
        RetrieveRequest(query="processing fee", as_of=date(2026, 6, 30), product_id="NEXA-HL")
    )
)
say("filter sent to the database for as_of=2026-06-30, product NEXA-HL:")
for clause in spy.filter["$and"]:
    say("  ", json.dumps(clause))

say("\nwhich registered documents are in force on a date (same rule as the filter)?")
register = json.loads(Path("nexa_synthetic_data/document_register.json").read_text())
for as_of in ("2023-06-01", "2024-06-01", "2026-06-30", "2026-07-01"):
    live = [
        e["doc_id"]
        for e in register
        if e["effective_from"] <= as_of <= (e["effective_to"] or "9999-12-31")
    ]
    say(f"  {as_of}: {', '.join(live)}")
