from __future__ import annotations

from typing import Any

import mongomock
import pytest

from app.core.config import Settings
from app.database import diagnostics


def test_snapshot_reports_actual_vector_lengths_without_returning_vectors(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    storage: Any = mongomock.MongoClient().db
    collection = storage[settings.mongodb_collection]
    collection.insert_many(
        [
            {"_id": "valid", "embedding": [0.1, 0.2]},
            {"_id": "missing"},
            {"_id": "malformed", "embedding": "not-a-vector"},
        ]
    )
    storage[settings.mongodb_parent_collection].insert_one(
        {"text": "Policy section", "embedding": [0.3, 0.4]}
    )
    monkeypatch.setattr(diagnostics, "_database", lambda _: storage)
    monkeypatch.setattr(
        collection,
        "list_search_indexes",
        lambda: [{"name": "test-index", "status": "READY", "queryable": True}],
        raising=False,
    )
    snapshot = diagnostics.read_rag_snapshot(settings)
    assert {row["_id"]: row["_actual_dimensions"] for row in snapshot["chunks"]} == {
        "valid": 2,
        "missing": -1,
        "malformed": -1,
    }
    assert all("embedding" not in row for row in snapshot["chunks"] + snapshot["parents"])
    assert snapshot["indexes"][0]["queryable"] is True
    assert collection.find_one({"_id": "valid"})["embedding"] == [0.1, 0.2]
