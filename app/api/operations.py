from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pymongo.errors import PyMongoError

from app.core.config import OPENAI_BASE_URL, Settings, get_settings
from app.core.http_monitoring import RouteMetrics
from app.core.observability import (
    answer_latencies,
    answer_metrics,
    latency_summary,
    sampled_hallucination,
)
from app.services.retrieval import check_ready, retrieval_metrics

router = APIRouter()
logger = structlog.get_logger()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
    try:
        await check_ready(settings)
    except PyMongoError:
        logger.warning("readiness_failed")
        raise HTTPException(status_code=503, detail="Not ready") from None
    return {"status": "ready"}


@router.get("/metrics")
async def metrics() -> dict[str, int | float]:
    return {
        "retrieval_requests_total": retrieval_metrics["requests"],
        "retrieval_errors_total": retrieval_metrics["errors"],
        "retrieval_empty_total": retrieval_metrics["empty"],
        "retrieval_latency_ms_total": retrieval_metrics["latency_us_total"] / 1000,
    }


@router.get("/metrics/latency")
async def latency_metrics() -> dict[str, int | float]:
    """Nearest-rank percentiles of the last 1000 successful requests in this process."""
    return latency_summary()


@router.get("/metrics/http")
async def http_metrics(request: Request) -> dict[str, object]:
    """Per-route counters and bounded latency windows, including routes not called yet."""
    recorded = request.app.state.http_metrics
    keys = set(recorded)
    # FastAPI may keep included routers lazy; OpenAPI resolves their public routes.
    for path, operations in request.app.openapi()["paths"].items():
        keys.update(
            (method.upper(), path)
            for method in operations
            if method in {"get", "head", "post", "put", "patch", "delete", "options", "trace"}
        )
    for route in request.app.routes:
        for method in getattr(route, "methods", ()):
            keys.add((method, route.path))
    return {
        "scope": "current API process; resets on restart; last 1000 latencies per route",
        "routes": [recorded.get(key, RouteMetrics()).snapshot(*key) for key in sorted(keys)],
    }


@router.get("/metrics/answers")
async def answer_metrics_summary(
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, int | float | None]:
    """SLO inputs from /answer: latency, error rate, tokens, priced cost, sampled hallucination."""
    requests = answer_metrics["requests"]
    cost = None
    if (
        requests
        and settings.chat_base_url == OPENAI_BASE_URL
        and settings.chat_input_price_per_mtok is not None
        and settings.chat_output_price_per_mtok is not None
    ):
        total = (
            answer_metrics["input_tokens"] * settings.chat_input_price_per_mtok
            + answer_metrics["output_tokens"] * settings.chat_output_price_per_mtok
        )
        cost = total / 1_000_000 / requests
    return {
        **latency_summary(answer_latencies),
        "answer_requests_total": requests,
        "answer_errors_total": answer_metrics["errors"],
        "answer_error_rate": answer_metrics["errors"] / requests if requests else 0,
        "input_tokens_total": answer_metrics["input_tokens"],
        "output_tokens_total": answer_metrics["output_tokens"],
        "cost_per_query_usd": cost,
        "sampled_count": len(sampled_hallucination),
        "sampled_hallucination_rate": sum(sampled_hallucination) / len(sampled_hallucination)
        if sampled_hallucination
        else None,
    }
