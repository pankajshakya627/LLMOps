from __future__ import annotations

from time import perf_counter

import structlog
from langchain_core.runnables import RunnableLambda

from app.chains.answer import build_answer_chain
from app.chains.llm import get_chat_model
from app.core import telemetry
from app.core.config import Settings
from app.core.observability import answer_latencies, answer_metrics, track_answer_usage
from app.core.telemetry import correlate_answer
from app.models.answer import AnswerResponse
from app.models.retrieval import RetrieveRequest, RetrieveResponse
from app.services.retrieval import retrieve_policy, scrub_request

logger = structlog.get_logger()


async def _generate_answer(request: RetrieveRequest, settings: Settings) -> AnswerResponse:
    async def retrieve(value: RetrieveRequest) -> RetrieveResponse:
        return await retrieve_policy(value, settings)

    chain = build_answer_chain(RunnableLambda(retrieve), get_chat_model(settings), settings)
    response = await chain.ainvoke(request)
    correlate_answer(response)
    logger.info(
        "answer_completed",
        status=response.status,
        citation_count=len(response.citations),
        generation_ms=response.generation_ms,
    )
    return response


async def answer_policy(request: RetrieveRequest, settings: Settings) -> AnswerResponse:
    """Answer one question and record end-to-end latency, failures and model tokens."""
    request = scrub_request(request, settings)
    answer_metrics["requests"] += 1
    if telemetry.statsd is not None:
        telemetry.statsd.increment("answer.requests")
    started = perf_counter()
    with track_answer_usage() as usage:
        try:
            response = await _generate_answer(request, settings)
        except Exception:
            answer_metrics["errors"] += 1
            if telemetry.statsd is not None:
                telemetry.statsd.increment("answer.errors")
            raise
        finally:
            answer_metrics.update(usage)
            if telemetry.statsd is not None:
                for name in ("input_tokens", "output_tokens"):
                    telemetry.statsd.increment(f"answer.{name}", usage[name])
    answer_latencies.append(round((perf_counter() - started) * 1000, 2))
    if telemetry.statsd is not None:
        telemetry.statsd.distribution("answer.duration_ms", answer_latencies[-1])
    return response
