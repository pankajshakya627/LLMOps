from __future__ import annotations

import asyncio
import hashlib
from datetime import UTC, datetime
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from app.chains.redaction import redact
from app.core.config import Settings
from app.database import feedback as database
from app.evaluation.answer_evaluation import GoldenAnswer
from app.models.feedback import FeedbackRecord, FeedbackRequest, FeedbackReview


async def submit_feedback(request: FeedbackRequest, settings: Settings) -> FeedbackRecord:
    record = FeedbackRecord(
        **request.model_dump(),
        feedback_id=uuid5(
            NAMESPACE_URL, f"{settings.institution}:{request.submitter_id}:{request.submission_id}"
        ),
        created_at=datetime.now(UTC),
    )
    previous = await asyncio.to_thread(database.save_feedback, record, settings)
    if previous is not None:
        if previous.model_dump(include=set(FeedbackRequest.model_fields)) != request.model_dump():
            raise ValueError("Submission ID already used for different feedback")
        return previous
    return record


async def list_recent(settings: Settings, limit: int) -> list[FeedbackRecord]:
    return await asyncio.to_thread(database.list_feedback, settings, limit)


async def review(feedback_id: UUID, request: FeedbackReview, settings: Settings) -> bool:
    return await asyncio.to_thread(database.review_feedback, feedback_id, request, settings)


async def export_golden(
    feedback_id: UUID,
    case: GoldenAnswer,
    settings: Settings,
) -> dict[str, Any]:
    """Export an explicit SME target; client answers and corrections are never copied."""
    record = await asyncio.to_thread(database.get_feedback, feedback_id, settings)
    if record is None:
        raise LookupError("Feedback not found")
    if record.status != "accepted" or not record.reviewer or not record.review_note.strip():
        raise ValueError("Accepted feedback with a reviewer and review note is required")
    if case.input != record.request:
        raise ValueError("Golden input must match the reviewed feedback request")
    if case.expected_status == "answered" and not case.context:
        raise ValueError("An answered golden case requires source references")
    if redact(case.model_dump_json())[1]:
        raise ValueError("Remove personal identifiers from the curated golden case")
    return {
        "case": case.model_dump(mode="json"),
        "review": {
            "feedback_id": str(record.feedback_id),
            "institution": settings.institution,
            "reviewer": record.reviewer,
            "review_note": record.review_note,
            "exported_at": datetime.now(UTC).isoformat(),
            "case_sha256": hashlib.sha256(case.model_dump_json().encode()).hexdigest(),
            "limitation": "Reviewer-curated target; source accuracy requires SME verification. "
            "Submitted answers and corrections are not authenticated generation records.",
        },
    }
