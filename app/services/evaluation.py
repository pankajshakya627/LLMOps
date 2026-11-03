from __future__ import annotations

import random
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import structlog
from langchain_core.runnables import RunnableLambda

from app.chains.answer import build_answer_chain
from app.chains.context import assemble_context
from app.chains.llm import get_chat_model
from app.chains.redaction import redact
from app.core import telemetry
from app.core.config import Settings
from app.core.observability import sampled_hallucination
from app.core.telemetry import correlate_answer
from app.evaluation.datadog_export import publish_annotations_safely
from app.evaluation.live import score_answer
from app.evaluation.run import load_cases
from app.models.answer import AnswerResponse
from app.models.evaluation import AnswerQuality, EvaluatedAnswerRequest, EvaluatedAnswerResponse
from app.models.retrieval import RetrieveRequest
from app.services.retrieval import retrieve_policy, scrub_request

logger = structlog.get_logger()
GOLDEN_DATASET = Path(__file__).resolve().parents[2] / "app/evaluation/datasets/answer.jsonl"


async def answer_with_quality(
    request: EvaluatedAnswerRequest, settings: Settings
) -> EvaluatedAnswerResponse:
    policy_request = scrub_request(
        RetrieveRequest.model_validate(request.model_dump(exclude={"reference_answer"})), settings
    )
    reference = request.reference_answer
    if reference and settings.redact_queries:
        reference = redact(reference)[0]
    source: Literal["provided", "golden_dataset", "none"] = "provided" if reference else "none"
    if reference is None and GOLDEN_DATASET.is_file():
        try:
            cases = load_cases(GOLDEN_DATASET)
        except (OSError, ValueError) as exc:
            logger.warning("golden_reference_unavailable", error_type=type(exc).__name__)
            cases = []
        for case in cases:
            if (
                case.expected_status == "answered"
                and case.input.query.casefold().rstrip("?") == request.query.casefold().rstrip("?")
                and case.input.as_of == request.as_of
                and case.input.product_id == request.product_id
                and case.input.jurisdiction == request.jurisdiction
            ):
                reference, source = case.expected_output, "golden_dataset"
                break

    retrieved = await retrieve_policy(policy_request, settings)
    chain = build_answer_chain(
        RunnableLambda(lambda _: retrieved), get_chat_model(settings), settings
    )
    answer = await chain.ainvoke(policy_request)
    contexts = [
        hit.parent_text
        for hit in assemble_context(
            retrieved.evidence, settings.context_max_tokens, settings.token_encoding
        ).values()
    ]
    metrics = await score_answer(policy_request.query, answer, contexts, reference, settings)
    quality = AnswerQuality(
        metrics=metrics,
        reference_source=source,
        reference_answer=reference,
        evaluated_at=datetime.now(UTC),
    )
    correlate_answer(answer)
    logger.info(
        "answer_quality_completed",
        reference_source=source,
        metric_statuses={name: metric.status for name, metric in metrics.items()},
    )
    return EvaluatedAnswerResponse(answer=answer, quality=quality)


def should_sample(answer: AnswerResponse, settings: Settings) -> bool:
    """Only answered responses carry claims to check; abstentions are skipped."""
    return answer.status == "answered" and random.random() < settings.live_eval_sample_rate


async def score_sampled_answer(
    request: RetrieveRequest, answer: AnswerResponse, settings: Settings
) -> None:
    """Background reference-free judging of live traffic; failures are logged, never raised.

    Faithfulness is measured against the answer's cited quotes (the evidence it claims to rest
    on) rather than the full retrieved context, so no second retrieval is needed.
    Without a reference answer, context precision and recall are not applicable.
    """
    try:
        request = scrub_request(request, settings)
        contexts = [citation.quote for citation in answer.citations]
        metrics = await score_answer(request.query, answer, contexts, None, settings)
        scored = {
            name: m.value
            for name, m in metrics.items()
            if m.status == "scored" and m.value is not None
        }
        if "faithfulness" in scored:
            sampled_hallucination.append(1 - scored["faithfulness"])
            if telemetry.statsd is not None:
                telemetry.statsd.gauge(
                    "sampled_hallucination_rate",
                    sum(sampled_hallucination) / len(sampled_hallucination),
                )
                telemetry.statsd.gauge("sampled_count", len(sampled_hallucination))
        publish_annotations_safely(
            EvaluatedAnswerResponse(
                answer=answer,
                quality=AnswerQuality(
                    metrics=metrics, reference_source="none", evaluated_at=datetime.now(UTC)
                ),
            ),
            settings,
        )
        logger.info(
            "sampled_answer_scored",
            scores=scored,
            prompt_version=answer.provenance.prompt_version if answer.provenance else None,
            answer_span_id=answer.datadog_span_id,
        )
    except Exception as exc:  # noqa: BLE001 - background scoring must never affect the answer
        logger.warning("sampled_scoring_failed", error_type=type(exc).__name__)
