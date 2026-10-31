from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx2 as httpx
import pytest
from langchain_core.messages import HumanMessage
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.chains.embeddings import get_embeddings
from app.chains.llm import get_chat_model
from app.core.config import Settings


def configured(settings: Settings, **changes: Any) -> Settings:
    return Settings.model_validate({**settings.model_dump(), **changes})


def test_local_chat_uses_explicit_key_endpoint_and_bounded_payload(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_BASE_URL", "https://unrelated.invalid/v1")
    local = configured(
        settings,
        openai_api_key=None,
        chat_model="qwen3.5:9b-mlx",
        chat_base_url="http://127.0.0.1:11434/v1",
        chat_api_key="ollama",
        chat_api_mode="chat_completions",
        chat_max_output_tokens=1234,
    )
    model = get_chat_model(local)
    seen: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        payload = json.loads(request.content)
        assert payload["model"] == "qwen3.5:9b-mlx"
        assert payload["max_tokens"] == 1234
        assert "max_completion_tokens" not in payload
        return httpx.Response(
            200,
            json={
                "id": "offline",
                "object": "chat.completion",
                "created": 0,
                "model": "qwen3.5:9b-mlx",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "ok"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
            },
        )

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
            client = AsyncOpenAI(
                base_url=local.chat_base_url, api_key="ollama", http_client=transport
            )
            model.async_client = client.chat.completions
            result = await model.ainvoke([HumanMessage("question")])
            assert result.usage_metadata and result.usage_metadata["output_tokens"] == 2

    asyncio.run(run())
    assert str(seen[0].url) == "http://127.0.0.1:11434/v1/chat/completions"
    assert seen[0].headers["authorization"] == "Bearer ollama"
    assert model.max_retries == 1 and model.request_timeout == 60


@pytest.mark.parametrize("kind", ["chat", "embedding"])
def test_custom_endpoint_never_inherits_openai_key(settings: Settings, kind: str) -> None:
    changes: dict[str, Any] = {f"{kind}_base_url": "https://other.invalid/v1"}
    if kind == "embedding":
        changes["embedding_profile"] = "other-deployment"
    custom = configured(settings, **changes)
    with pytest.raises(ValueError, match="explicit.*API_KEY"):
        (get_chat_model if kind == "chat" else get_embeddings)(custom)


@pytest.mark.parametrize("url", ["ftp://host/v1", "https://user:password@host/v1", "not-a-url"])
def test_endpoint_validation(settings: Settings, url: str) -> None:
    with pytest.raises(ValidationError):
        configured(settings, chat_base_url=url)


@pytest.mark.parametrize("bad", [[0.1], [float("nan"), 0.2], [float("inf"), 0.2]])
def test_local_embedding_validates_results_and_sends_text(
    settings: Settings, bad: list[float]
) -> None:
    local = configured(
        settings,
        openai_api_key=None,
        embedding_model="qwen3-embedding:0.6b",
        embedding_base_url="http://127.0.0.1:11434/v1",
        embedding_api_key="ollama",
        embedding_profile="qwen3-0.6b-test",
        embedding_dimensions=2,
    )
    embedding = get_embeddings(local)
    seen: list[dict[str, Any]] = []
    vector = [0.1, 0.2]

    def respond(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        seen.append(payload)
        assert payload["input"] == ["Policy text"]
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "data": [{"object": "embedding", "index": 0, "embedding": vector}],
                    "model": "qwen3-embedding:0.6b",
                    "usage": {"prompt_tokens": 2, "total_tokens": 2},
                }
            ),
        )

    async def run() -> None:
        nonlocal vector
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
            client = AsyncOpenAI(
                base_url=local.embedding_base_url, api_key="ollama", http_client=transport
            )
            embedding.async_client = client.embeddings
            assert await embedding.aembed_documents(["Policy text"]) == [[0.1, 0.2]]
            assert await embedding.aembed_query("Policy text") == [0.1, 0.2]
            vector = bad
            with pytest.raises(ValueError, match="embedding"):
                await embedding.aembed_query("Policy text")

    asyncio.run(run())
    assert len(seen) == 3


def test_evaluator_profiles_do_not_inherit_candidate_endpoint(settings: Settings) -> None:
    from app.evaluation.profiles import judge_settings, metric_settings

    local = configured(
        settings,
        chat_model="qwen3.5:9b-mlx",
        chat_base_url="http://127.0.0.1:4000/v1",
        chat_api_key="gateway-key",
        chat_api_mode="chat_completions",
        embedding_model="nexa-embed-local",
        embedding_profile="qwen3-0.6b-test",
        embedding_base_url="http://127.0.0.1:4000/v1",
        embedding_api_key="gateway-key",
        embedding_dimensions=1024,
        eval_judge_model="fixed-openai-judge",
    )
    judge = judge_settings(local)
    metric = metric_settings(local)
    assert judge.chat_model == "fixed-openai-judge"
    assert judge.chat_base_url == "https://api.openai.com/v1"
    assert judge.chat_api_key is None and judge.chat_api_mode == "responses"
    assert judge.chat_max_output_tokens is None
    assert metric.embedding_model == "text-embedding-3-small"
    assert metric.embedding_dimensions == 1536
    assert metric.embedding_base_url == "https://api.openai.com/v1"
    assert metric.embedding_api_key is None


def test_default_openai_endpoint_overrides_ambient_sdk_endpoint(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_API_BASE", "https://other.invalid/v1")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://other.invalid/v1")
    assert str(get_chat_model(settings).root_async_client.base_url) == "https://api.openai.com/v1/"
    assert get_embeddings(settings).openai_api_base == "https://api.openai.com/v1"
