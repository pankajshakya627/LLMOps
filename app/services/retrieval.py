from __future__ import annotations

import asyncio
from collections import Counter

import structlog

from app.chains.embeddings import get_embeddings
from app.chains.redaction import redact
from app.chains.rerank import build_rerank_chain
from app.chains.retrieval import build_retrieval_chain
from app.core import telemetry
from app.core.config import Settings
from app.core.observability import retrieval_latencies
from app.database.mongo import get_parent_store, get_vector_store, ping_database
from app.database.retrieval import build_amendment_search, build_hybrid_search
from app.models.retrieval import RetrieveRequest, RetrieveResponse
from app.security.bedrock import check_content
from app.security.input_policy import enforce_input_policy

logger = structlog.get_logger()
retrieval_metrics: Counter[str] = Counter()


def scrub_request(request: RetrieveRequest, settings: Settings) -> RetrieveRequest:
    """Reject explicit instruction overrides and redact supported personal identifiers."""
    enforce_input_policy(request.query)
    if not settings.redact_queries:
        return request
    query, counts = redact(request.query)
    if not counts:
        return request
    logger.warning("query_pii_redacted", counts=dict(counts))
    return request.model_copy(update={"query": query})


async def retrieve_policy(request: RetrieveRequest, settings: Settings) -> RetrieveResponse:
    request = scrub_request(request, settings)
    await asyncio.to_thread(check_content, request.query, "INPUT", settings)
    retrieval_metrics["requests"] += 1
    if telemetry.statsd is not None:
        telemetry.statsd.increment("retrieval.requests")
    try:
        vector_store = await asyncio.to_thread(get_vector_store, settings, get_embeddings(settings))
        chain = build_retrieval_chain(
            vector_store,
            get_parent_store(settings),
            settings,
            candidate_search=build_hybrid_search(vector_store, settings)
            if settings.retrieval_mode == "hybrid"
            else None,
            reranker=build_rerank_chain(settings) if settings.rerank_enabled else None,
            amendment_search=build_amendment_search(settings),
        )
        response = await chain.ainvoke(request)
    except Exception:
        retrieval_metrics["errors"] += 1
        if telemetry.statsd is not None:
            telemetry.statsd.increment("retrieval.errors")
        raise
    if not response.results:
        retrieval_metrics["empty"] += 1
        if telemetry.statsd is not None:
            telemetry.statsd.increment("retrieval.empty")
        logger.warning("retrieval_empty", as_of=request.as_of.isoformat())
    retrieval_metrics["latency_us_total"] += round(response.timings.total_ms * 1000)
    retrieval_latencies.append(response.timings.total_ms)
    if telemetry.statsd is not None:
        telemetry.statsd.distribution("retrieval.duration_ms", response.timings.total_ms)
    logger.info(
        "retrieval_completed",
        result_count=len(response.results),
        latency_ms=response.timings.total_ms,
    )
    return response


async def check_ready(settings: Settings) -> None:
    """Readiness: the chunk database answers. Model availability is not probed."""
    await asyncio.to_thread(ping_database, settings)
