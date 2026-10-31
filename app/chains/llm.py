from __future__ import annotations

import hashlib
import json
from typing import Any

from langchain_openai import ChatOpenAI

from app.chains.prompts.answer import ANSWER_PROMPT_SHA, ANSWER_PROMPT_VERSION
from app.core.config import OPENAI_BASE_URL, Settings
from app.core.observability import TokenUsageLogger


def get_chat_model(settings: Settings) -> ChatOpenAI:
    responses = settings.chat_api_mode == "responses"
    key = settings.provider_key(settings.chat_base_url, settings.chat_api_key)
    body: dict[str, Any] = {}
    if not responses and settings.chat_max_output_tokens is not None:
        # Ollama uses max_tokens; the SDK flattens extra_body into the request.
        body["max_tokens"] = settings.chat_max_output_tokens
    if settings.chat_cache_namespace:
        if settings.chat_base_url == OPENAI_BASE_URL:
            raise ValueError("CHAT_CACHE_NAMESPACE is only for a configured LiteLLM gateway")
        scope = {
            "namespace": settings.chat_cache_namespace,
            "credential": key.get_secret_value(),
            "institution": settings.institution,
            "jurisdiction": settings.jurisdiction,
            "confidentiality": settings.confidentiality_level,
            "database": settings.mongodb_db,
            "chunks": settings.mongodb_collection,
            "parents": settings.mongodb_parent_collection,
            "index": settings.vector_index_name,
            "embedding_model": settings.embedding_model,
            "embedding_profile": settings.embedding_profile,
            "embedding_dimensions": settings.embedding_dimensions,
            "model": settings.chat_model,
            "reasoning_effort": settings.chat_reasoning_effort,
            "prompt_version": ANSWER_PROMPT_VERSION,
            "prompt_sha": ANSWER_PROMPT_SHA,
        }
        body["metadata"] = {
            "redis_namespace": hashlib.sha256(
                json.dumps(scope, sort_keys=True).encode()
            ).hexdigest()
        }
    return ChatOpenAI(
        model=settings.chat_model,
        base_url=settings.chat_base_url,
        api_key=key,
        use_responses_api=responses,
        reasoning_effort=settings.chat_reasoning_effort,
        include_response_headers=not responses,
        max_tokens=settings.chat_max_output_tokens if responses else None,
        extra_body=body or None,
        timeout=settings.chat_timeout_seconds,
        max_retries=1,
        callbacks=[TokenUsageLogger()],
    )
