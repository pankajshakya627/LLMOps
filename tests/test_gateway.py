from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx2 as httpx
import pytest
from langchain_core.runnables import RunnableLambda
from openai import APIStatusError, AsyncOpenAI

from app.api.operations import answer_metrics_summary
from app.chains.answer import build_answer_chain
from app.chains.llm import get_chat_model
from app.core.config import Settings
from app.core.observability import answer_metrics
from app.models.retrieval import RetrieveRequest, RetrieveResponse


@pytest.mark.parametrize("cache_hit", [None, "true", "false"])
def test_gateway_response_retains_observed_model_and_cache_header(
    settings: Settings, cache_hit: str | None
) -> None:
    settings = settings.model_copy(
        update={
            "chat_base_url": "http://127.0.0.1:4000/v1",
            "chat_model": "nexa-chat",
            "chat_api_key": settings.openai_api_key,
            "chat_api_mode": "chat_completions",
        }
    )
    model = get_chat_model(settings)
    retrieved = RetrieveResponse.model_validate(
        {
            "as_of": "2026-10-01",
            "results": [
                {
                    "rank": 1,
                    "score": 0.9,
                    "text": "Maximum is 7.5 crore.",
                    "parent_text": "Maximum is 7.5 crore.",
                    "citation": {
                        "doc_id": "POL-HL",
                        "title": "Home Loan",
                        "policy_version": "3",
                        "clause": "4.1",
                        "effective_date": "2025-10-01",
                    },
                }
            ],
            "timings": {"search_ms": 1, "parent_ms": 1, "total_ms": 2},
        }
    )

    def respond(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content)["model"] == "nexa-chat"
        return httpx.Response(
            200,
            headers={"x-litellm-cache-hit": cache_hit} if cache_hit else {},
            json={
                "id": "offline",
                "object": "chat.completion",
                "created": 0,
                "model": "observed-fallback-model",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": json.dumps(
                                {
                                    "status": "answered",
                                    "answer": "7.5 crore [1]",
                                    "evidence": [{"evidence_id": 1, "quote": "7.5 crore"}],
                                }
                            ),
                        },
                    }
                ],
                "usage": {"prompt_tokens": 4, "completion_tokens": 5, "total_tokens": 9},
            },
        )

    async def run() -> Any:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
            client = AsyncOpenAI(
                base_url=settings.chat_base_url, api_key="unused", http_client=transport
            )
            model.root_async_client = client
            model.async_client = client.chat.completions
            return await build_answer_chain(
                RunnableLambda(lambda _: retrieved), model, settings
            ).ainvoke(RetrieveRequest(query="Limit?", as_of=retrieved.as_of))

    response = asyncio.run(run())
    assert response.status == "answered"
    assert response.provenance.chat_model == "nexa-chat"
    assert response.provenance.observed_chat_model == "observed-fallback-model"
    assert response.provenance.gateway_cache_hit is (
        None if cache_hit is None else cache_hit == "true"
    )


def test_mixed_gateway_tokens_are_not_priced_with_one_model_pair(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(answer_metrics, "requests", 1)
    monkeypatch.setitem(answer_metrics, "input_tokens", 1000)
    monkeypatch.setitem(answer_metrics, "output_tokens", 1000)
    configured = settings.model_copy(
        update={
            "chat_base_url": "http://127.0.0.1:4000/v1",
            "chat_input_price_per_mtok": 10,
            "chat_output_price_per_mtok": 10,
        }
    )
    assert asyncio.run(answer_metrics_summary(configured))["cost_per_query_usd"] is None
    assert asyncio.run(answer_metrics_summary(configured))["input_tokens_total"] == 1000


def test_cache_namespace_covers_scope_profile_and_prompt_version(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.chains import llm

    gateway = settings.model_copy(
        update={
            "chat_base_url": "http://127.0.0.1:4000/v1",
            "chat_api_mode": "chat_completions",
            "chat_api_key": settings.openai_api_key,
            "chat_cache_namespace": "isolated-class",
        }
    )

    def namespace(config: Settings) -> str:
        body = get_chat_model(config).extra_body
        assert body is not None
        value: str = body["metadata"]["redis_namespace"]
        return value

    original = namespace(gateway)
    for field in ("institution", "confidentiality_level", "mongodb_collection", "embedding_model"):
        assert namespace(gateway.model_copy(update={field: "other"})) != original
    monkeypatch.setattr(llm, "ANSWER_PROMPT_VERSION", "test-next-version")
    assert namespace(gateway) != original


def test_gateway_exhaustion_is_bounded_and_does_not_switch_in_application(
    settings: Settings,
) -> None:
    settings = settings.model_copy(
        update={
            "chat_base_url": "http://127.0.0.1:4000/v1",
            "chat_api_mode": "chat_completions",
            "chat_api_key": settings.openai_api_key,
            "chat_model": "nexa-chat",
        }
    )
    model = get_chat_model(settings)
    attempts = []

    def fail(request: httpx.Request) -> httpx.Response:
        attempts.append(json.loads(request.content)["model"])
        return httpx.Response(500, json={"error": {"message": "Offline exhausted fixture"}})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(fail)) as transport:
            assert model.max_retries == 1
            client = AsyncOpenAI(
                base_url=settings.chat_base_url,
                api_key="unused",
                max_retries=model.max_retries,
                http_client=transport,
            )
            model.async_client = client.chat.completions
            with pytest.raises(APIStatusError):
                await model.ainvoke("Offline request")

    asyncio.run(run())
    assert attempts == ["nexa-chat", "nexa-chat"]
