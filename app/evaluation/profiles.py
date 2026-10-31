from __future__ import annotations

from app.core.config import DEFAULT_CHAT_MODEL, Settings


def judge_settings(settings: Settings) -> Settings:
    """Keep evaluator endpoint and credentials independent from the candidate."""
    return settings.model_copy(
        update={
            "chat_model": settings.eval_judge_model or DEFAULT_CHAT_MODEL,
            "chat_base_url": settings.eval_judge_base_url,
            "chat_api_key": settings.eval_judge_api_key,
            "chat_api_mode": settings.eval_judge_api_mode,
            "chat_cache_namespace": None,
            "chat_max_output_tokens": None,
            "chat_reasoning_effort": None,
            "openai_fallback_model": None,
        }
    )


def metric_settings(settings: Settings) -> Settings:
    return settings.model_copy(
        update={
            "embedding_model": settings.eval_embedding_model,
            "embedding_dimensions": settings.eval_embedding_dimensions,
            "embedding_base_url": settings.eval_embedding_base_url,
            "embedding_api_key": settings.eval_embedding_api_key,
            "embedding_profile": settings.eval_embedding_profile,
        }
    )
