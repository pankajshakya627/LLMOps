"""Correlate real HTTP responses with their Phoenix server spans."""

from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from typing import TYPE_CHECKING, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import Event, ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from pydantic import BaseModel
from starlette.datastructures import URL

if TYPE_CHECKING:
    from app.models.answer import AnswerResponse


class PrivateSpanExporter(SpanExporter):
    """Exception events bypass OpenInference masking; export their type only."""

    def __init__(self, exporter: SpanExporter) -> None:
        self.exporter = exporter

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        safe_spans = [
            ReadableSpan(
                name=span.name,
                context=span.context,
                parent=span.parent,
                resource=span.resource,
                attributes=span.attributes,
                links=span.links,
                kind=span.kind,
                instrumentation_scope=span.instrumentation_scope,
                start_time=span.start_time,
                end_time=span.end_time,
                status=trace.Status(span.status.status_code),
                events=[
                    Event(
                        event.name,
                        timestamp=event.timestamp,
                        attributes={
                            key: value
                            for key, value in (event.attributes or {}).items()
                            if key in {"exception.type", "exception.escaped"}
                        },
                    )
                    if event.name == "exception"
                    else event
                    for event in span.events
                ],
            )
            for span in spans
        ]
        return self.exporter.export(safe_spans)

    def shutdown(self) -> None:
        self.exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return self.exporter.force_flush(timeout_millis)


def correlate_answer(answer: AnswerResponse) -> None:
    context = trace.get_current_span().get_span_context()
    if context.is_valid:
        answer.phoenix_trace_id = f"{context.trace_id:032x}"
        answer.phoenix_span_id = f"{context.span_id:016x}"


def record_result(result: BaseModel, *, capture_content: bool) -> None:
    """Show the final API payload on its request span without bypassing content masking."""
    span = trace.get_current_span()
    if capture_content and span.get_span_context().is_valid:
        span.set_attribute("output.mime_type", "application/json")
        span.set_attribute("output.value", result.model_dump_json())


def trace_log_context(
    _logger: Any, _method: str, event: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    context = trace.get_current_span().get_span_context()
    if context.is_valid:
        event.update(trace_id=f"{context.trace_id:032x}", span_id=f"{context.span_id:016x}")
    return event


def capture_request(span: Any, scope: dict[str, Any]) -> None:
    if span is None or not span.is_recording():
        return
    context = span.get_span_context()
    if context.is_valid:
        scope["nexa.phoenix"] = (f"{context.trace_id:032x}", f"{context.span_id:016x}")
        scope["nexa.phoenix.span"] = span
        span.set_attribute("openinference.span.kind", "CHAIN")
        # Queries can contain credentials; request bodies have their own masked capture.
        url = str(URL(scope={**scope, "query_string": b""}))
        span.set_attribute("http.url", url)
        span.set_attribute("url.full", url)
        span.set_attribute("url.query", "")


def correlate_response(span: Any, scope: dict[str, Any], message: dict[str, Any]) -> None:
    context = scope.get("nexa.phoenix")
    if message["type"] == "http.response.start" and context:
        trace_id, span_id = context
        message.setdefault("headers", []).extend(
            [(b"x-phoenix-trace-id", trace_id.encode()), (b"x-phoenix-span-id", span_id.encode())]
        )
