from __future__ import annotations

import re
from html import escape
from time import perf_counter
from typing import Any, Literal

import structlog
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable, RunnableLambda
from openai import OpenAIError

from app.chains.context import assemble_context, render_context
from app.chains.guardrails import validate_draft
from app.chains.llm import get_chat_model
from app.chains.prompts.answer import (
    ANSWER_PROMPT,
    ANSWER_PROMPT_ID,
    ANSWER_PROMPT_SHA,
    ANSWER_PROMPT_VERSION,
)
from app.chains.redaction import redact
from app.core.config import OPENAI_BASE_URL, Settings
from app.core.observability import prompt_annotation_context
from app.models.answer import AnswerCitation, AnswerDraft, AnswerResponse, Provenance
from app.models.retrieval import RetrieveRequest, RetrieveResponse

logger = structlog.get_logger()
INSUFFICIENT_EVIDENCE = (
    "I cannot answer this question reliably from the retrieved policy evidence. "
    "Check the selected product and policy date, and specify the policy term you want to check."
)


def build_answer_chain(
    retriever: Runnable[RetrieveRequest, RetrieveResponse],
    llm: BaseChatModel,
    settings: Settings,
) -> Runnable[RetrieveRequest, AnswerResponse]:
    """Retrieve evidence, generate a draft, and validate its citation references."""
    if settings.openai_fallback_model is not None and (
        settings.chat_base_url != OPENAI_BASE_URL
        or settings.chat_model != settings.openai_fallback_model
    ):

        async def answer_with_fallback(request: RetrieveRequest) -> AnswerResponse:
            retrieved = await retriever.ainvoke(request)
            replay: Runnable[RetrieveRequest, RetrieveResponse] = RunnableLambda(
                lambda _: retrieved
            )
            primary_settings = settings.model_copy(update={"openai_fallback_model": None})
            primary = build_answer_chain(replay, llm, primary_settings)
            response = None
            reason: Literal["provider_error", "unanswered"] = "unanswered"
            started = perf_counter()
            try:
                response = await primary.ainvoke(request)
                if (
                    response.status == "answered"
                    or response.generation_ms == 0
                    or not response.provenance
                    or not response.provenance.evidence_refs
                ):
                    return response
            except OpenAIError:
                reason = "provider_error"
                if not retrieved.evidence:
                    raise
            primary_ms = round((perf_counter() - started) * 1000, 2)
            cloud_settings = primary_settings.model_copy(
                update={
                    "chat_model": settings.openai_fallback_model,
                    "chat_base_url": OPENAI_BASE_URL,
                    "chat_api_key": None,
                    "chat_api_mode": "responses",
                    "chat_reasoning_effort": None,
                    "chat_cache_namespace": None,
                }
            )
            cloud = build_answer_chain(replay, get_chat_model(cloud_settings), cloud_settings)
            result = await cloud.with_config(run_name="openai_policy_fallback").ainvoke(request)
            if result.provenance is not None:
                result.provenance.fallback_from_model = settings.chat_model
                result.provenance.fallback_reason = reason
            result.generation_ms += primary_ms
            logger.info(
                "answer_model_fallback",
                primary_model=settings.chat_model,
                model=cloud_settings.chat_model,
                reason=reason,
            )
            return result

        return RunnableLambda(answer_with_fallback).with_config(run_name="answer_policy")

    generation = ANSWER_PROMPT | llm.with_structured_output(
        AnswerDraft, method="json_schema", strict=True, include_raw=True
    )

    async def validate_output(draft: AnswerDraft) -> dict[str, bool]:
        await validate_draft(draft, settings)
        return {"validation_passed": True}

    validator = RunnableLambda(validate_output).with_config(run_name="validate_output")

    async def answer(request: RetrieveRequest) -> AnswerResponse:
        retrieved = await retriever.ainvoke(request)
        sources = assemble_context(
            retrieved.evidence, settings.context_max_tokens, settings.token_encoding
        )

        response = AnswerResponse(
            as_of=request.as_of,
            status="insufficient_evidence",
            answer=INSUFFICIENT_EVIDENCE,
            citations=[],
            retrieval_timings=retrieved.timings,
            generation_ms=0,
            provenance=Provenance(
                prompt_id=ANSWER_PROMPT_ID,
                prompt_version=ANSWER_PROMPT_VERSION,
                prompt_sha=ANSWER_PROMPT_SHA,
                chat_model=settings.chat_model,
                embedding_model=settings.embedding_model,
                retrieval_mode=settings.retrieval_mode,
                rerank_enabled=settings.rerank_enabled,
                evidence_refs=[
                    f"{hit.citation.doc_id}:{hit.citation.policy_version}:"
                    f"{hit.citation.clause or 'full'}"
                    for hit in sources.values()
                ],
            ),
        )
        if not sources or any(
            not any(source.parent_text == amendment.parent_text for source in sources.values())
            for amendment in retrieved.amendments
        ):
            return response

        started = perf_counter()
        for attempt in range(2):
            variables = {
                "query": request.query,
                "as_of": request.as_of.isoformat(),
                "product_id": request.product_id or "",
                "context": render_context(sources),
                "citation_feedback": ""
                if attempt == 0
                else "The previous draft failed citation validation. Copy exact contiguous "
                "quotes and ensure every evidence ID matches its inline markers.",
            }
            variables = {name: escape(value, quote=False) for name, value in variables.items()}
            with prompt_annotation_context(
                ANSWER_PROMPT,
                variables,
                prompt_id=ANSWER_PROMPT_ID,
                version=ANSWER_PROMPT_VERSION,
            ):
                raw: Any = await generation.ainvoke(variables)
            if isinstance(raw, dict) and isinstance(raw.get("raw"), AIMessage):
                metadata = raw["raw"].response_metadata
                observed = metadata.get("model_name") or metadata.get("model")
                if response.provenance is not None:
                    response.provenance.observed_chat_model = (
                        observed if isinstance(observed, str) else None
                    )
                    cache_hit = metadata.get("headers", {}).get("x-litellm-cache-hit")
                    if cache_hit in {"true", "false"}:
                        response.provenance.gateway_cache_hit = cache_hit == "true"
                if raw.get("parsing_error") is not None:
                    raise ValueError("Generated output failed schema validation")
                raw = raw.get("parsed")
            response.generation_ms = round((perf_counter() - started) * 1000, 2)
            draft = AnswerDraft.model_validate(raw)
            if any(redact(text)[1] for text in (draft.answer, *(e.quote for e in draft.evidence))):
                logger.warning("answer_output_pii_blocked")
                return response
            await validator.ainvoke(draft)
            if draft.status == "insufficient_evidence":
                return response
            if draft.status == "needs_clarification":
                response.status = "needs_clarification"
                response.answer = (
                    "Which product and policy date should I use, "
                    "and what specific rate or policy term do you want to check?"
                )
                return response

            markers = {int(number) for number in re.findall(r"\[(\d+)\]", draft.answer)}
            evidence_ids = {item.evidence_id for item in draft.evidence}
            if (
                not evidence_ids
                or markers != evidence_ids
                or any(
                    item.evidence_id not in sources
                    or not item.quote.strip()
                    or item.quote not in sources[item.evidence_id].parent_text
                    for item in draft.evidence
                )
            ):
                logger.warning("answer_citation_validation_failed", attempt=attempt + 1)
                continue

            response.status = "answered"
            response.answer = draft.answer
            response.citations = [
                AnswerCitation(
                    **item.model_dump(), matched_child=sources[item.evidence_id].citation
                )
                for item in draft.evidence
            ]
            return response
        return response

    return RunnableLambda(answer).with_config(run_name="answer_policy")
