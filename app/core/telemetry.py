"""Datadog setup, privacy and correlation shared by serving and evaluation."""

from __future__ import annotations

import json
import os
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit, urlunsplit

if TYPE_CHECKING:
    from ddtrace.trace import Span

    from app.core.config import Settings
    from app.models.answer import AnswerResponse

capture_content_enabled = False
statsd: Any = None


def safe_text(value: str) -> str:
    from app.core.http_monitoring import CAPTURE_LIMIT, safe_content

    if len(value.encode("utf-8")) > CAPTURE_LIMIT:
        return "[OMITTED: exceeds 64 KiB]"
    try:
        parsed = json.loads(value)
    except ValueError, RecursionError:
        return str(safe_content(value))
    return json.dumps(safe_content(parsed), ensure_ascii=False)


def private_span(span: Span) -> None:
    """Run before LLMObs serialization so both APM and LLM errors retain type only."""
    for key, value in span.get_tags().items():
        if key in {"error.message", "error.stack", "http.query.string"}:
            span.set_tag(key, "")
        elif key == "http.url":
            parts = urlsplit(value)
            span.set_tag(key, urlunsplit((parts.scheme, parts.netloc, parts.path, "", "")))
        elif key.startswith(
            ("langchain.request.", "langchain.response.", "gen_ai.input.", "gen_ai.output.")
        ):
            span.set_tag(key, safe_text(value) if capture_content_enabled else "[REDACTED]")
        else:
            span.set_tag(key, safe_text(value))

    # The SDK's public processor does not expose prompt variables or clear workflow values.
    data = span._get_struct_tag("_llmobs")
    if data:
        meta = data.get("meta", {})
        for direction in ("input", "output", "metadata"):
            content = meta.get(direction, {})
            if capture_content_enabled:
                meta[direction] = private_content(content)
            elif direction == "input" and isinstance(content, dict) and content.get("prompt"):
                meta[direction] = {
                    "prompt": {
                        key: value
                        for key, value in content["prompt"].items()
                        if key in {"id", "version", "template", "chat_template"}
                    }
                }
            else:
                meta[direction] = {}
        if span.error:
            meta["metadata"]["error_type"] = span.get_tag("error.type") or "Error"
        span._set_struct_tag("_llmobs", data)


def private_content(value: Any) -> Any:
    from app.core.http_monitoring import safe_content

    if isinstance(value, str):
        return safe_text(value)
    if isinstance(value, dict):
        return safe_content({key: private_content(item) for key, item in value.items()})
    if isinstance(value, list):
        return [private_content(item) for item in value]
    return safe_content(value)


def configure_telemetry(settings: Settings) -> None:
    """Called by the serving entry point before importing FastAPI or LangChain."""
    global capture_content_enabled, statsd
    capture_content_enabled = settings.dd_capture_content
    for name in (
        "dd_service",
        "dd_env",
        "dd_version",
        "dd_site",
        "dd_agent_host",
        "dd_trace_enabled",
    ):
        os.environ[name.upper()] = str(getattr(settings, name))
    os.environ.setdefault("DD_INSTRUMENTATION_TELEMETRY_ENABLED", "false")
    os.environ.setdefault("DD_TRACE_STARTUP_LOGS", "false")
    from ddtrace import config, patch, tracer
    from ddtrace.internal import core
    from ddtrace.llmobs import LLMObs

    config.service = settings.dd_service
    config.env = settings.dd_env
    config.version = settings.dd_version
    tracer.enabled = settings.dd_trace_enabled
    # The pinned SDK dispatches this event before constructing the LLM export payload.
    core.on("trace.span_finish", private_span, name="nexaassist.privacy")
    if settings.dd_llmobs_enabled:
        LLMObs.enable(
            ml_app=settings.dd_llmobs_ml_app,
            site=settings.dd_site,
            api_key=settings.dd_api_key.get_secret_value() if settings.dd_api_key else None,
            env=settings.dd_env,
            service=settings.dd_service,
            agentless_enabled=settings.dd_llmobs_agentless_enabled,
            integrations_enabled=False,
        )
    if settings.dd_trace_enabled or settings.dd_llmobs_enabled:
        patch(fastapi=True, langchain=True)
    if settings.dd_metrics_enabled:
        tags = [f"service:{settings.dd_service}", f"env:{settings.dd_env}"]
        tags.extend(f"{name}:{value}" for name, value in config.tags.items())
        if settings.dd_llmobs_agentless_enabled:
            from datadog import ThreadStats, initialize

            initialize(
                api_key=settings.dd_api_key.get_secret_value() if settings.dd_api_key else None,
                api_host=f"https://api.{settings.dd_site}",
            )
            statsd = ThreadStats(namespace="nexaassist", constant_tags=tags)
            statsd.start()
        else:
            from datadog import DogStatsd

            statsd = DogStatsd(
                host=settings.dd_agent_host,
                port=settings.dd_dogstatsd_port,
                namespace="nexaassist",
                constant_tags=tags,
            )


def correlate_answer(answer: AnswerResponse) -> None:
    from ddtrace.llmobs import LLMObs

    if LLMObs.enabled:
        identity = LLMObs.export_span()
        if identity:
            answer.datadog_trace_id = identity["trace_id"].zfill(32)
            answer.datadog_span_id = identity["span_id"]


def trace_log_context(
    _logger: Any, _method: str, event: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    from ddtrace import config, tracer

    span = tracer.current_span()
    if span:
        event.setdefault("dd.trace_id", f"{span.trace_id:032x}")
        event.setdefault("dd.span_id", str(span.span_id))
    event.update(service=config.service, env=config.env, version=config.version)
    return event


def record_http_metrics(method: str, route: str, status: int, duration_ms: float) -> None:
    if statsd is not None:
        tags = [f"method:{method}", f"route:{route}", f"status_code:{status}"]
        statsd.increment("http.requests", tags=tags)
        statsd.distribution("http.duration_ms", duration_ms, tags=tags)
        if status >= 500:
            statsd.increment("http.errors", tags=tags)
