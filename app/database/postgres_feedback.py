"""Institution-scoped feedback persistence for PostgreSQL deployments."""

from __future__ import annotations

from uuid import UUID

from psycopg.types.json import Jsonb

from app.core.config import Settings
from app.database.postgres import connect
from app.models.feedback import FeedbackRecord, FeedbackReview


def save_feedback(record: FeedbackRecord, settings: Settings) -> FeedbackRecord | None:
    with connect(settings) as db:
        inserted = db.execute(
            """INSERT INTO nexa_feedback VALUES (%s,%s,%s)
            ON CONFLICT DO NOTHING RETURNING id""",
            (settings.institution, str(record.feedback_id), Jsonb(record.model_dump(mode="json"))),
        ).fetchone()
        if inserted is not None:
            return None
        row = db.execute(
            "SELECT payload FROM nexa_feedback WHERE institution=%s AND id=%s",
            (settings.institution, str(record.feedback_id)),
        ).fetchone()
        if row is None:
            raise RuntimeError("Concurrent feedback removal; retry submission")
        return FeedbackRecord.model_validate(row[0])


def list_feedback(settings: Settings, limit: int) -> list[FeedbackRecord]:
    with connect(settings) as db:
        rows = db.execute(
            """SELECT payload FROM nexa_feedback WHERE institution=%s
            ORDER BY payload->>'created_at' DESC,id LIMIT %s""",
            (settings.institution, limit),
        ).fetchall()
    return [FeedbackRecord.model_validate(row[0]) for row in rows]


def get_feedback(feedback_id: UUID, settings: Settings) -> FeedbackRecord | None:
    with connect(settings) as db:
        row = db.execute(
            "SELECT payload FROM nexa_feedback WHERE institution=%s AND id=%s",
            (settings.institution, str(feedback_id)),
        ).fetchone()
    return FeedbackRecord.model_validate(row[0]) if row else None


def review_feedback(feedback_id: UUID, review: FeedbackReview, settings: Settings) -> bool:
    with connect(settings) as db:
        result = db.execute(
            """UPDATE nexa_feedback SET payload=payload || %s::jsonb
            WHERE institution=%s AND id=%s AND payload->>'status'='pending'""",
            (Jsonb(review.model_dump(mode="json")), settings.institution, str(feedback_id)),
        )
        return result.rowcount == 1
