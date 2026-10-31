"""Submit, review and export a curated regression case through the real API, offline."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import patch

import httpx
import mongomock
from pydantic import SecretStr

from app.core.config import Settings, get_settings
from app.database import feedback as database
from app.evaluation.answer_evaluation import load_golden
from app.main import create_app
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
        feedback_reviewer_token=SecretStr("offline-reviewer-fixture-0000000000"),
    )
    # Start from a curated local case, never from the submitted answer or correction.
    case = load_golden(Path("app/evaluation/datasets/answer.jsonl"))[0]
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    storage: Any = mongomock.MongoClient().db
    with patch.object(database, "_database", return_value=storage):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://offline"
        ) as client:
            submitted = await client.post(
                "/feedback",
                json={
                    "request": case.input.model_dump(mode="json"),
                    "helpful": False,
                    "correction": "UNVERIFIED CLAIM FROM USER",
                    "response": {
                        "as_of": case.input.as_of.isoformat(),
                        "status": "insufficient_evidence",
                        "answer": "UNTRUSTED CLIENT RESPONSE",
                        "citations": [],
                        "generation_ms": 0,
                        "retrieval_timings": {"search_ms": 0, "parent_ms": 0, "total_ms": 0},
                    },
                },
            )
            submitted.raise_for_status()
            identifier = submitted.json()["feedback_id"]
            url = f"/feedback/{identifier}/golden"
            headers = {"Authorization": "Bearer offline-reviewer-fixture-0000000000"}
            payload = case.model_dump(mode="json")
            assert (await client.post(url, json=payload)).status_code == 401
            assert (await client.post(url, json=payload, headers=headers)).status_code == 409
            reviewed = await client.post(
                f"/feedback/{identifier}/review",
                headers=headers,
                json={
                    "status": "accepted",
                    "reviewer": "Workshop SME",
                    "review_note": "Reviewed the registered policy and selected an existing curated target.",
                },
            )
            reviewed.raise_for_status()
            exported = await client.post(url, json=payload, headers=headers)
            exported.raise_for_status()
            bundle = exported.json()
            assert "UNTRUSTED" not in exported.text and "UNVERIFIED" not in exported.text
            with TemporaryDirectory() as temporary:
                path = Path(temporary) / "reviewed.jsonl"
                path.write_text(json.dumps(bundle["case"], ensure_ascii=False) + "\n")
                assert load_golden(path) == [case]
            assert bundle["review"]["reviewer"] == "Workshop SME"
            say("export without token=401; pending review=409; accepted + curated target=200")
            say("golden JSONL validated; reviewer and case hash retained in audit bundle")
            say("No shipped golden case changed. Policy meaning still requires SME verification.")


if __name__ == "__main__":
    asyncio.run(main())
