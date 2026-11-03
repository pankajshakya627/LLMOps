from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.retrieval import Citation, RetrieveTimings


class EvidenceQuote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: int = Field(ge=1)
    quote: str = Field(min_length=1)


class AnswerDraft(BaseModel):
    """Model output; source identities are resolved by application code."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["answered", "insufficient_evidence", "needs_clarification"]
    answer: str = Field(min_length=1)
    evidence: list[EvidenceQuote]


class GuardrailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    llm_output: str = Field(min_length=1, max_length=64000)


class GuardrailResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    validation_passed: bool


class AnswerCitation(EvidenceQuote):
    # The quote can come from another clause in the matched child's parent section.
    matched_child: Citation


class Provenance(BaseModel):
    """What produced an answer; feedback inherits it, so a rating maps to a prompt and model."""

    model_config = ConfigDict(extra="forbid")

    prompt_id: str
    prompt_version: str
    prompt_sha: str
    chat_model: str
    observed_chat_model: str | None = Field(default=None, max_length=256)
    gateway_cache_hit: bool | None = None
    fallback_from_model: str | None = None
    fallback_reason: Literal["provider_error", "unanswered"] | None = None
    embedding_model: str
    retrieval_mode: str
    rerank_enabled: bool
    evidence_refs: list[str]


class AnswerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: date
    status: Literal["answered", "insufficient_evidence", "needs_clarification"]
    answer: str
    citations: list[AnswerCitation]
    retrieval_timings: RetrieveTimings
    generation_ms: float
    datadog_trace_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{32}$")
    datadog_span_id: str | None = Field(default=None, pattern=r"^[1-9][0-9]{0,19}$")
    # Retain historical feedback payloads; new requests populate Datadog IDs only.
    phoenix_trace_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{32}$", deprecated=True)
    phoenix_span_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{16}$", deprecated=True)
    provenance: Provenance | None = None
