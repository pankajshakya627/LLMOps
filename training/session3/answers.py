"""Replay deterministic model drafts through the real answer chain, offline."""

from __future__ import annotations

import asyncio
from datetime import date
from unittest.mock import Mock

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableLambda

from app.chains.answer import build_answer_chain
from app.core.config import Settings
from app.models.retrieval import (
    Citation,
    RetrieveHit,
    RetrieveRequest,
    RetrieveResponse,
    RetrieveTimings,
)
from training.console import say


async def main() -> None:
    settings = Settings(
        _env_file=None,
        mongodb_uri="mongodb://unused",
        mongodb_db="unused",
        mongodb_collection="unused",
        openai_api_key="unused",
        institution="NexaBank",
        jurisdiction="IN",
        confidentiality_level="internal",
    )
    text = "Maximum amount is 7.5 crore."
    hit = RetrieveHit(
        rank=1,
        score=0.9,
        text=text,
        parent_text=text,
        citation=Citation(
            doc_id="POL-HL-V3",
            title="Synthetic policy",
            policy_version="3",
            clause="4.1",
            effective_date=date(2025, 1, 1),
        ),
    )
    retrieved = RetrieveResponse(
        as_of=date(2026, 10, 1),
        results=[hit],
        timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
    )
    for label, answer, quote, expected in (
        ("valid", "The maximum is 7.5 crore [1].", text, "answered"),
        ("invented quote", "The maximum is 7.5 crore [1].", "Made up", "insufficient_evidence"),
        ("output PII", "Email staff@example.com [1].", text, "insufficient_evidence"),
    ):
        generate = Mock(
            return_value={
                "status": "answered",
                "answer": answer,
                "evidence": [{"evidence_id": 1, "quote": quote}],
            }
        )

        model = Mock(spec=BaseChatModel)
        model.with_structured_output.return_value = RunnableLambda(generate)
        chain = build_answer_chain(RunnableLambda(lambda _: retrieved), model, settings)
        result = await chain.ainvoke(RetrieveRequest(query="maximum amount", as_of=retrieved.as_of))
        assert result.status == expected
        assert generate.call_count == (2 if label == "invented quote" else 1)
        assert "staff@example.com" not in result.model_dump_json()
        say(f"{label}: status={result.status}, model_calls={generate.call_count}")


if __name__ == "__main__":
    asyncio.run(main())
