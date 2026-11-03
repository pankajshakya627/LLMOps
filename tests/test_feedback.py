from __future__ import annotations

import asyncio
from datetime import date
from typing import Any
from uuid import uuid4

import mongomock
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import Settings, get_settings
from app.database import feedback as database
from app.database import mongo
from app.main import create_app
from app.models.answer import AnswerResponse
from app.models.feedback import FeedbackRequest
from app.models.retrieval import RetrieveRequest, RetrieveTimings
from app.services import feedback as service


def test_feedback_review_is_closed_without_reviewer_credentials(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    from unittest.mock import AsyncMock

    listing = AsyncMock(return_value=[])
    monkeypatch.setattr(service, "list_recent", listing)
    monkeypatch.setattr(service, "review", AsyncMock(return_value=True))
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    assert client.get("/feedback").status_code == 503
    assert (
        client.post(
            f"/feedback/{uuid4()}/review",
            json={"status": "accepted", "reviewer": "Untrusted caller", "review_note": "Approve"},
        ).status_code
        == 503
    )
    listing.assert_not_awaited()


@pytest.mark.parametrize("helpful", [True, False])
@pytest.mark.parametrize("traced", [False, True])
def test_feedback_persists_review_and_prevents_overwriting(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, helpful: bool, traced: bool
) -> None:
    settings = settings.model_copy(
        update={"feedback_reviewer_token": SecretStr("reviewer-test-token-000000000000000000")}
    )
    storage: Any = mongomock.MongoClient().db
    monkeypatch.setattr(database, "_database", lambda _: storage)
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    request = FeedbackRequest(
        request=RetrieveRequest(query="fee", as_of=date(2026, 10, 1)),
        response=AnswerResponse(
            as_of=date(2026, 10, 1),
            status="insufficient_evidence",
            answer="No evidence",
            citations=[],
            generation_ms=0,
            phoenix_trace_id="1" * 32 if traced else None,
            phoenix_span_id="2" * 16 if traced else None,
            retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
        ),
        helpful=helpful,
        correction="The current circular is missing.",
    )
    response = client.post("/feedback", json=request.model_dump(mode="json"))
    assert response.status_code == 201
    identifier = response.json()["feedback_id"]
    review = {
        "status": "accepted",
        "reviewer": "Instructor",
        "review_note": "Add a regression case.",
    }
    headers = {"Authorization": "Bearer reviewer-test-token-000000000000000000"}
    assert client.get("/feedback").status_code == 401
    assert client.get("/feedback", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.post(f"/feedback/{identifier}/review", json=review).status_code == 401
    assert (
        client.post(f"/feedback/{identifier}/review", json=review, headers=headers).status_code
        == 200
    )
    assert (
        client.post(f"/feedback/{identifier}/review", json=review, headers=headers).status_code
        == 409
    )
    assert client.get("/feedback", headers=headers).json()[0]["status"] == "accepted"
    other_settings = settings.model_copy(update={"institution": "OtherBank"})
    assert database.list_feedback(other_settings, 20) == []
    assert (
        client.post(f"/feedback/{uuid4()}/review", json=review, headers=headers).status_code == 409
    )
    retry = client.post("/feedback", json=request.model_dump(mode="json"))
    assert retry.status_code == 201
    assert retry.json()["feedback_id"] == identifier
    assert retry.json()["status"] == "accepted"
    assert storage.policy_feedback.count_documents({}) == 1
    changed = request.model_dump(mode="json")
    changed["correction"] = "Different feedback using the same submission ID"
    assert client.post("/feedback", json=changed).status_code == 409
    assert response.json()["response"]["phoenix_span_id"] == ("2" * 16 if traced else None)


def test_retire_document_removes_both_stores_only_in_current_scope(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    storage: Any = mongomock.MongoClient().db
    monkeypatch.setattr(mongo, "_database", lambda _: storage)
    for name in (settings.mongodb_collection, settings.mongodb_parent_collection):
        storage[name].insert_many(
            [
                {
                    "doc_id": "OLD",
                    "institution": institution,
                    "jurisdiction": "IN",
                    "confidentiality_level": "internal",
                }
                for institution in ("NexaBank", "OtherBank")
            ]
        )
    assert mongo.retire_document(settings, "OLD") == {"chunks_removed": 1, "parents_removed": 1}
    assert storage.chunks.find_one()["institution"] == "OtherBank"


def test_concurrent_feedback_retries_create_one_record(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    storage: Any = mongomock.MongoClient().db
    monkeypatch.setattr(database, "_database", lambda _: storage)
    request = FeedbackRequest(
        request=RetrieveRequest(query="fee", as_of="2026-10-01"),
        response=AnswerResponse(
            as_of="2026-10-01",
            status="insufficient_evidence",
            answer="No evidence",
            citations=[],
            generation_ms=0,
            phoenix_span_id="2" * 16,
            retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
        ),
        helpful=True,
    )

    async def retry() -> list[Any]:
        return await asyncio.gather(*(service.submit_feedback(request, settings) for _ in range(8)))

    records = asyncio.run(retry())
    assert len({r.feedback_id for r in records}) == 1
    assert storage.policy_feedback.count_documents({}) == 1


def test_stored_feedback_survives_retired_response_fields_without_relaxing_http_validation(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    storage: Any = mongomock.MongoClient().db
    monkeypatch.setattr(database, "_database", lambda _: storage)
    request = FeedbackRequest(
        request=RetrieveRequest(query="fee", as_of="2026-10-01"),
        response=AnswerResponse(
            as_of="2026-10-01",
            status="insufficient_evidence",
            answer="No evidence",
            citations=[],
            generation_ms=0,
            retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
        ),
        helpful=False,
    )
    record = asyncio.run(service.submit_feedback(request, settings))
    storage.policy_feedback.update_one(
        {"_id": str(record.feedback_id)}, {"$set": {"response.retired_span_id": "123"}}
    )
    assert database.list_feedback(settings, 10)[0].feedback_id == record.feedback_id
    assert database.get_feedback(record.feedback_id, settings).feedback_id == record.feedback_id
    assert asyncio.run(service.submit_feedback(request, settings)).feedback_id == record.feedback_id
    assert storage.policy_feedback.find_one()["response"]["retired_span_id"] == "123"
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    payload = request.model_dump(mode="json")
    payload["response"]["unexpected_field"] = "untrusted"
    assert TestClient(app).post("/feedback", json=payload).status_code == 422
