"""Correlate real HTTP responses with their Phoenix server spans."""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any

from opentelemetry import trace
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.models.answer import AnswerResponse


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
        span.set_attribute("openinference.span.kind", "CHAIN")


def correlate_response(span: Any, scope: dict[str, Any], message: dict[str, Any]) -> None:
    context = scope.get("nexa.phoenix")
    if message["type"] == "http.response.start" and context:
        trace_id, span_id = context
        message.setdefault("headers", []).extend(
            [(b"x-phoenix-trace-id", trace_id.encode()), (b"x-phoenix-span-id", span_id.encode())]
        )
