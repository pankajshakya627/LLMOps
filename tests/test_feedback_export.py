from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import mongomock
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from pymongo.errors import ConnectionFailure

from app.core.config import Settings, get_settings
from app.database import feedback as database
from app.evaluation.answer_evaluation import GoldenAnswer, load_golden
from app.main import create_app
from app.models.answer import AnswerResponse
from app.models.feedback import FeedbackRequest, FeedbackReview
from app.models.retrieval import RetrieveRequest, RetrieveTimings
from app.services import feedback as service


def test_reviewed_export_uses_server_review_and_separate_curated_answer(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    tmp_path: Path,
) -> None:
    storage: Any = mongomock.MongoClient().db
    monkeypatch.setattr(database, "_database", lambda _: storage)
    settings = settings.model_copy(
        update={"feedback_reviewer_token": SecretStr("test-review-token")}
    )
    request = FeedbackRequest(
        request=RetrieveRequest(
            query="Maximum home loan?", as_of="2026-10-01", product_id="NEXA-HL"
        ),
        response=AnswerResponse(
            as_of="2026-10-01",
            status="insufficient_evidence",
            answer="UNTRUSTED CLIENT ANSWER",
            citations=[],
            generation_ms=0,
            retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
        ),
        helpful=False,
        correction="UNVERIFIED USER CORRECTION",
    )
    record = asyncio.run(service.submit_feedback(request, settings))
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    headers = {"Authorization": "Bearer test-review-token"}
    url = f"/feedback/{record.feedback_id}/golden"
    candidate: dict[str, Any] = GoldenAnswer.model_validate(
        {
            "input": request.request.model_dump(mode="json"),
            "expected_output": "The maximum is 7.5 crore under clause 4.1.",
            "context": [{"doc_id": "POL-HL-V3", "clause": "4.1"}],
            "expected_status": "answered",
        }
    ).model_dump(mode="json")
    assert client.post(url, json=candidate).status_code == 401
    assert client.post(url, json=candidate, headers=headers).status_code == 409
    assert (
        client.post(f"/feedback/{uuid4()}/golden", json=candidate, headers=headers).status_code
        == 404
    )
    review = FeedbackReview(
        status="accepted", reviewer="Policy SME", review_note="Checked source clause 4.1"
    )
    assert asyncio.run(service.review(record.feedback_id, review, settings))
    exported = client.post(url, json=candidate, headers=headers)
    assert exported.status_code == 200
    bundle = exported.json()
    assert bundle["case"] == candidate
    assert bundle["review"]["feedback_id"] == str(record.feedback_id)
    assert bundle["review"]["reviewer"] == "Policy SME"
    assert bundle["review"]["review_note"] == review.review_note
    assert len(bundle["review"]["case_sha256"]) == 64
    assert "UNTRUSTED" not in exported.text and "UNVERIFIED" not in exported.text
    path = tmp_path / "reviewed.jsonl"
    path.write_text(json.dumps(bundle["case"]) + "\n")
    assert load_golden(path)[0].expected_output == candidate["expected_output"]
    # Export is read-only and retries leave the authoritative feedback unchanged.
    assert client.post(url, json=candidate, headers=headers).json()["case"] == candidate
    assert storage.policy_feedback.count_documents({}) == 1
    for changed in (
        {**candidate, "input": {**candidate["input"], "as_of": "2025-01-01"}},
        {**candidate, "expected_output": "Contact staff@example.com"},
        {**candidate, "context": []},
    ):
        assert client.post(url, json=changed, headers=headers).status_code == 409
    assert (
        client.post(url, json={**candidate, "extra": "forbidden"}, headers=headers).status_code
        == 422
    )
    app.dependency_overrides[get_settings] = lambda: settings.model_copy(
        update={"institution": "OtherBank"}
    )
    assert client.post(url, json=candidate, headers=headers).status_code == 404
    app.dependency_overrides[get_settings] = lambda: settings

    def unavailable(*_: Any) -> None:
        raise ConnectionFailure("private-db-host")

    monkeypatch.setattr(database, "get_feedback", unavailable)
    failed = client.post(url, json=candidate, headers=headers)
    assert failed.status_code == 503 and "private-db-host" not in failed.text
