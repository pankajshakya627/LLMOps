"""Validate shipped deployment overlays with synthetic credentials, never the private .env."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import OPENAI_BASE_URL, Settings


@pytest.mark.parametrize("cloud_embeddings", [False, True])
def test_native_gateway_profiles_route_both_embeddings_and_keep_judges_independent(
    settings: Settings, tmp_path: Path, cloud_embeddings: bool
) -> None:
    base = tmp_path / ".env"
    base.write_text(
        "LITELLM_MASTER_KEY=synthetic-gateway-key\n"
        "CHAT_API_KEY=${LITELLM_MASTER_KEY}\n"
        "EMBEDDING_API_KEY=${LITELLM_MASTER_KEY}\n"
        "EVAL_JUDGE_MODEL=independent-judge\n"
        "OPENAI_FALLBACK_MODEL=stale-extra-fallback\n"
    )
    files = [base, Path("app/gateway/application.env.example")]
    if cloud_embeddings:
        files.append(Path("app/gateway/openai-embeddings.env.example"))
    configured = Settings(
        _env_file=tuple(files),
        **{
            name: getattr(settings, name)
            for name in (
                "mongodb_uri",
                "mongodb_db",
                "institution",
                "jurisdiction",
                "confidentiality_level",
            )
        },
    )
    assert configured.chat_model == "nexa-chat"
    assert configured.chat_api_key.get_secret_value() == "synthetic-gateway-key"
    assert configured.embedding_api_key.get_secret_value() == "synthetic-gateway-key"
    assert configured.embedding_model == (
        "nexa-embed-openai" if cloud_embeddings else "nexa-embed-local"
    )
    assert configured.embedding_dimensions == (1536 if cloud_embeddings else 1024)
    assert configured.embedding_profile.endswith("gateway-v1")
    assert configured.mongodb_collection.endswith("gateway_v1")
    assert configured.eval_judge_model == "independent-judge"
    assert configured.eval_embedding_base_url == OPENAI_BASE_URL
    assert configured.openai_fallback_model is None
    assert configured.chat_reasoning_effort is None
    assert configured.chat_cache_namespace


@pytest.mark.parametrize("profile", ["ollama", "openai-fallback"])
def test_shipped_profiles_keep_qwen_retrieval_and_an_independent_cloud_judge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, settings: Settings, profile: str
) -> None:
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    base = tmp_path / ".env"
    base.write_text(
        "OPENAI_API_KEY=synthetic-cloud-key\n"
        "CHAT_MODEL=approved-cloud-candidate\n"
        "CHAT_BASE_URL=https://api.openai.com/v1\n"
        "CHAT_API_MODE=responses\n"
        "EVAL_JUDGE_MODEL=independent-judge\n"
        "CHAT_API_KEY=stale-local-key\n"
        "CHAT_REASONING_EFFORT=none\n"
        "CHAT_CACHE_NAMESPACE=stale-gateway-cache\n"
    )
    configured = Settings(
        _env_file=(base, Path(f"app/gateway/{profile}.env.example")),
        **{
            name: getattr(settings, name)
            for name in (
                "mongodb_uri",
                "mongodb_db",
                "institution",
                "jurisdiction",
                "confidentiality_level",
            )
        },
    )
    assert configured.embedding_model == "qwen3-embedding:0.6b"
    assert configured.embedding_dimensions == 1024
    assert configured.embedding_profile == "qwen3-0.6b-local-v1"
    assert configured.mongodb_collection == "policy_chunks_qwen3_v1"
    assert configured.mongodb_parent_collection == "policy_sections_qwen3_v1"
    assert configured.vector_index_name == "policy_qwen3_v1"
    assert configured.eval_judge_model == "independent-judge"
    assert configured.eval_judge_base_url == OPENAI_BASE_URL
    assert configured.chat_cache_namespace is None
    key = configured.provider_key(configured.chat_base_url, configured.chat_api_key)
    if profile == "ollama":
        assert configured.chat_model == "qwen3.5:9b-mlx"
        assert configured.chat_api_mode == "chat_completions"
        assert configured.chat_reasoning_effort == "none"
        assert key.get_secret_value() == "ollama"
    else:
        assert configured.chat_model == "approved-cloud-candidate"
        assert configured.chat_api_mode == "responses"
        assert configured.chat_reasoning_effort is None
        assert key.get_secret_value() == "synthetic-cloud-key"


@pytest.mark.parametrize(
    "field,url",
    [
        ("chat_base_url", "https://provider.invalid/v1?api_key=private"),
        ("embedding_base_url", "https://provider.invalid/v1#private"),
        ("eval_judge_base_url", "https://user:private@provider.invalid/v1"),
        ("eval_embedding_base_url", "file:///tmp/private"),
        ("guardrails_base_url", "http://127.0.0.1:99999"),
        ("phoenix_base_url", "https://user:private@collector.invalid"),
    ],
)
def test_provider_and_collector_endpoints_reject_unsafe_url_configuration(
    settings: Settings, field: str, url: str
) -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({**settings.model_dump(), field: url})
