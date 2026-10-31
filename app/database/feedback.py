from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.config import Settings
from app.database.mongo import _database
from app.models.answer import AnswerResponse
from app.models.feedback import FeedbackRecord, FeedbackReview


def _record(row: dict[str, Any]) -> FeedbackRecord:
    payload = {key: value for key, value in row.items() if key not in {"_id", "institution"}}
    # Stored snapshots outlive telemetry fields; HTTP input still uses the strict schema.
    payload["response"] = {
        key: value
        for key, value in payload["response"].items()
        if key in AnswerResponse.model_fields
    }
    return FeedbackRecord.model_validate(payload)


def save_feedback(record: FeedbackRecord, settings: Settings) -> FeedbackRecord | None:
    if settings.storage_backend == "pgvector":
        from app.database import postgres_feedback

        return postgres_feedback.save_feedback(record, settings)
    previous = _database(settings)[settings.mongodb_feedback_collection].find_one_and_update(
        {"_id": str(record.feedback_id), "institution": settings.institution},
        {
            "$setOnInsert": {
                "_id": str(record.feedback_id),
                "institution": settings.institution,
                **record.model_dump(mode="json"),
            }
        },
        upsert=True,
    )
    if previous is None:
        return None
    return _record(previous)


def list_feedback(settings: Settings, limit: int) -> list[FeedbackRecord]:
    if settings.storage_backend == "pgvector":
        from app.database import postgres_feedback

        return postgres_feedback.list_feedback(settings, limit)
    rows = (
        _database(settings)[settings.mongodb_feedback_collection]
        .find({"institution": settings.institution}, {"_id": 0, "institution": 0})
        .sort("created_at", -1)
        .limit(limit)
    )
    return [_record(row) for row in rows]


def get_feedback(feedback_id: UUID, settings: Settings) -> FeedbackRecord | None:
    if settings.storage_backend == "pgvector":
        from app.database import postgres_feedback

        return postgres_feedback.get_feedback(feedback_id, settings)
    row = _database(settings)[settings.mongodb_feedback_collection].find_one(
        {"_id": str(feedback_id), "institution": settings.institution},
        {"_id": 0, "institution": 0},
    )
    return _record(row) if row is not None else None


def review_feedback(feedback_id: UUID, review: FeedbackReview, settings: Settings) -> bool:
    if settings.storage_backend == "pgvector":
        from app.database import postgres_feedback

        return postgres_feedback.review_feedback(feedback_id, review, settings)
    result = _database(settings)[settings.mongodb_feedback_collection].update_one(
        {"_id": str(feedback_id), "institution": settings.institution, "status": "pending"},
        {"$set": review.model_dump(mode="json")},
    )
    return result.modified_count == 1
