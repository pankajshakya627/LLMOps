from __future__ import annotations

from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_CHAT_MODEL = "gpt-6-luna"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    storage_backend: Literal["mongodb", "pgvector"] = "mongodb"
    postgres_dsn: SecretStr | None = None
    mongodb_uri: SecretStr | None = None
    mongodb_db: str = "nexaassist"
    mongodb_collection: str = "policy_chunks"
    vector_index_name: str = "policy_chunks_v1"
    mongodb_parent_collection: str = "policy_sections"
    mongodb_feedback_collection: str = "policy_feedback"
    feedback_reviewer_token: SecretStr | None = Field(default=None, min_length=32)

    @field_validator(
        "feedback_reviewer_token",
        "chat_reasoning_effort",
        "openai_fallback_model",
        "chat_cache_namespace",
        mode="before",
    )
    @classmethod
    def empty_optional_setting(cls, value: object) -> object:
        return None if value == "" else value

    openai_api_key: SecretStr | None = None
    chat_base_url: str = OPENAI_BASE_URL
    chat_api_key: SecretStr | None = None
    chat_api_mode: Literal["responses", "chat_completions"] = "responses"
    chat_reasoning_effort: Literal["none"] | None = None
    chat_cache_namespace: str | None = Field(default=None, min_length=1)
    embedding_base_url: str = OPENAI_BASE_URL
    embedding_api_key: SecretStr | None = None
    # Required for custom embedding deployments; aliases alone are not model identities.
    embedding_profile: str | None = Field(default=None, min_length=1)
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = Field(default=1536, gt=0)
    embedding_batch_size: int = Field(default=100, ge=1, le=100)
    chat_model: str = DEFAULT_CHAT_MODEL
    openai_fallback_model: str | None = Field(default=None, min_length=1)
    eval_judge_model: str | None = None
    eval_judge_base_url: str = OPENAI_BASE_URL
    eval_judge_api_key: SecretStr | None = None
    eval_judge_api_mode: Literal["responses", "chat_completions"] = "responses"
    eval_embedding_model: str = "text-embedding-3-small"
    eval_embedding_dimensions: int = Field(default=1536, gt=0)
    eval_embedding_base_url: str = OPENAI_BASE_URL
    eval_embedding_api_key: SecretStr | None = None
    eval_embedding_profile: str | None = None
    # Hard cap on answer generation (denial-of-wallet guard); judges are not capped.
    chat_max_output_tokens: int | None = Field(default=2000, ge=64)
    chat_timeout_seconds: float = Field(default=60, ge=1, le=180)
    retrieval_mode: Literal["dense", "hybrid"] = "dense"
    text_index_name: str = "policy_text_v1"
    retrieval_candidates: int = Field(default=20, ge=20, le=50)
    rerank_enabled: bool = False
    context_max_tokens: int = Field(default=6000, ge=256)
    rerank_model: str = "nexaassist-reranker:0.6b-mlx"
    rerank_api: Literal["ollama", "openai"] = "ollama"
    rerank_base_url: str = "http://127.0.0.1:11434"
    rerank_api_key: SecretStr = SecretStr("ollama")
    rerank_max_tokens: int = Field(default=4000, ge=256)
    token_encoding: str = "o200k_base"
    # Share of answered /answer requests scored in the background; 0 disables sampling.
    live_eval_sample_rate: float = Field(default=0.0, ge=0, le=1)
    # Requests per client address per minute on /answer* and /feedback; 0 disables the limit.
    rate_limit_per_minute: int = Field(default=30, ge=0)
    # USD per million tokens. Unset means /metrics/answers reports no cost.
    chat_input_price_per_mtok: float | None = Field(default=None, ge=0)
    chat_output_price_per_mtok: float | None = Field(default=None, ge=0)

    # Mask emails, phones, PAN and Aadhaar numbers before chunks are hashed and embedded.
    redact_pii: bool = True
    # Mask the same identifiers in user questions before any embedding or model call.
    redact_queries: bool = True
    guardrails_base_url: str | None = None
    bedrock_guardrail_id: str | None = Field(default=None, min_length=1)
    bedrock_guardrail_version: str | None = Field(default=None, pattern=r"^[1-9][0-9]*$")
    bedrock_region: str | None = Field(default=None, min_length=1)
    chunk_max_characters: int = Field(default=1200, gt=0)
    chunk_overlap_characters: int = Field(default=150, ge=0)

    # Corpus-wide metadata that the document register does not carry.
    institution: str
    jurisdiction: str
    confidentiality_level: str

    log_level: str = "INFO"
    dd_llmobs_enabled: bool = False
    dd_llmobs_ml_app: str = Field(default="nexaassist", min_length=1)
    dd_api_key: SecretStr | None = None
    dd_site: Literal[
        "datadoghq.com",
        "us3.datadoghq.com",
        "us5.datadoghq.com",
        "datadoghq.eu",
        "ap1.datadoghq.com",
        "ap2.datadoghq.com",
        "uk1.datadoghq.com",
        "ddog-gov.com",
        "us2.ddog-gov.com",
    ] = "datadoghq.com"
    dd_service: str = Field(default="nexaassist-api", min_length=1)
    dd_env: str = Field(default="dev", min_length=1)
    dd_version: str = "0.1.0"
    dd_llmobs_agentless_enabled: bool = True
    dd_trace_enabled: bool = False
    dd_capture_content: bool = False
    dd_agent_host: str = "127.0.0.1"
    dd_dogstatsd_port: int = Field(default=8125, ge=1, le=65535)
    dd_metrics_enabled: bool = False

    @field_validator(
        "chat_base_url",
        "embedding_base_url",
        "eval_judge_base_url",
        "eval_embedding_base_url",
        "guardrails_base_url",
    )
    @classmethod
    def valid_endpoint(cls, value: str | None) -> str | None:
        if value is None:
            return None
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("API base URL must be HTTP(S) without credentials, query or fragment")
        _ = parsed.port
        return value.rstrip("/")

    def provider_key(self, base_url: str, explicit: SecretStr | None) -> SecretStr:
        if explicit is not None and explicit.get_secret_value():
            return explicit
        if base_url.rstrip("/") != OPENAI_BASE_URL:
            raise ValueError("Custom endpoint requires an explicit endpoint API_KEY")
        if self.openai_api_key is None or not self.openai_api_key.get_secret_value():
            raise ValueError("OPENAI_API_KEY is required for this OpenAI operation")
        return self.openai_api_key

    @model_validator(mode="after")
    def valid_overlap(self) -> Settings:
        if (
            (self.dd_llmobs_enabled or self.dd_metrics_enabled)
            and self.dd_llmobs_agentless_enabled
            and (not self.dd_api_key or not self.dd_api_key.get_secret_value().strip())
        ):
            raise ValueError("DD_API_KEY is required for agentless Datadog observability")
        if self.bedrock_guardrail_id and not (
            self.bedrock_guardrail_version and self.bedrock_region
        ):
            raise ValueError("Bedrock Guardrails requires a published version and explicit Region")
        if self.bedrock_guardrail_version and not self.bedrock_guardrail_id:
            raise ValueError("BEDROCK_GUARDRAIL_ID is required with its version")
        if self.storage_backend == "pgvector":
            if self.postgres_dsn is None or not self.postgres_dsn.get_secret_value():
                raise ValueError("POSTGRES_DSN is required for pgvector storage")
            if self.retrieval_mode != "dense":
                raise ValueError("pgvector currently supports RETRIEVAL_MODE=dense only")
        elif self.mongodb_uri is None or not self.mongodb_uri.get_secret_value():
            raise ValueError("MONGODB_URI is required for mongodb storage")
        if self.chunk_overlap_characters >= self.chunk_max_characters:
            raise ValueError("CHUNK_OVERLAP_CHARACTERS must be smaller than CHUNK_MAX_CHARACTERS")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


class UISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_base_url: str = "http://127.0.0.1:8000"
    ui_timezone: str = "Asia/Kolkata"


@lru_cache
def get_ui_settings() -> UISettings:
    return UISettings()
