"""Bounded HTTP metrics and optional synthetic JSON capture for every API route."""

from __future__ import annotations

import json
import re
from collections import Counter, deque
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.chains.redaction import redact
from app.core.observability import latency_summary

CAPTURE_LIMIT = 65_536
SECRET_SUFFIXES = (
    "authorization",
    "cookie",
    "password",
    "secret",
    "token",
    "apikey",
    "masterkey",
    "privatekey",
    "dsn",
)
SECRET_TEXT = re.compile(r"\bsk-[A-Za-z0-9_-]+|\bBearer\s+[A-Za-z0-9._~-]+", re.IGNORECASE)


def safe_content(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED_SECRET]"
            if re.sub(r"[^a-z0-9]", "", key.lower()).endswith(SECRET_SUFFIXES)
            or (key == "input" and {"loc", "type"} <= value.keys())
            else safe_content(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [safe_content(item) for item in value]
    if isinstance(value, str):
        return SECRET_TEXT.sub("[REDACTED_SECRET]", redact(value)[0])
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        masked, counts = redact(str(value))
        return masked if counts else value
    return value


def record_payload(span: Any, direction: str, body: bytearray, complete: bool) -> None:
    if not complete:
        span.set_attribute(f"nexa.{direction}.capture", "omitted: exceeds 64 KiB or incomplete")
        return
    if not body:
        return
    try:
        value = json.dumps(safe_content(json.loads(body)), ensure_ascii=False)
    except ValueError, UnicodeError, RecursionError:
        span.set_attribute(f"nexa.{direction}.capture", "omitted: invalid JSON")
        return
    span.set_attribute(f"{direction}.mime_type", "application/json")
    span.set_attribute(f"{direction}.value", value)


@dataclass
class RouteMetrics:
    requests: int = 0
    statuses: Counter[int] = field(default_factory=Counter)
    latency_ms_total: float = 0
    latencies: deque[float] = field(default_factory=lambda: deque(maxlen=1000))

    def snapshot(self, method: str, route: str) -> dict[str, Any]:
        return {
            "method": method,
            "route": route,
            "requests": self.requests,
            "client_errors": sum(n for status, n in self.statuses.items() if 400 <= status < 500),
            "server_errors": sum(n for status, n in self.statuses.items() if status >= 500),
            "status_counts": dict(self.statuses),
            "latency_ms_total": self.latency_ms_total,
            **latency_summary(self.latencies),
        }


class HTTPMonitoringMiddleware:
    def __init__(self, app: ASGIApp, metrics: dict[tuple[str, str], RouteMetrics]) -> None:
        self.app = app
        self.metrics = metrics

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = perf_counter()
        responded_at: float | None = None
        status = 500
        request_body, response_body = bytearray(), bytearray()
        request_complete = response_complete = False
        span = scope.get("nexa.phoenix.span")
        capture = bool(getattr(scope["app"].state, "phoenix_capture_content", False) and span)
        request_json = b"application/json" in dict(scope.get("headers", [])).get(
            b"content-type", b""
        )
        response_json = False

        async def monitored_receive() -> Message:
            nonlocal request_complete
            message = await receive()
            if capture and request_json and message["type"] == "http.request":
                # shortcut: JSON capture is capped at 64 KiB; use external artifacts for larger payloads.
                request_body.extend(
                    message.get("body", b"")[: max(0, CAPTURE_LIMIT + 1 - len(request_body))]
                )
                request_complete = (
                    not message.get("more_body", False) and len(request_body) <= CAPTURE_LIMIT
                )
            return message

        async def monitored_send(message: Message) -> None:
            nonlocal status, response_complete, response_json, responded_at
            if message["type"] == "http.response.start":
                status = message["status"]
                response_json = b"application/json" in dict(message.get("headers", [])).get(
                    b"content-type", b""
                )
            elif message["type"] == "http.response.body" and capture:
                if response_json:
                    response_body.extend(
                        message.get("body", b"")[: max(0, CAPTURE_LIMIT + 1 - len(response_body))]
                    )
                    response_complete = (
                        not message.get("more_body", False) and len(response_body) <= CAPTURE_LIMIT
                    )
                if not message.get("more_body", False):
                    if request_json:
                        record_payload(span, "input", request_body, request_complete)
                    if response_json:
                        record_payload(span, "output", response_body, response_complete)
            await send(message)
            if message["type"] == "http.response.body" and not message.get("more_body", False):
                responded_at = perf_counter()

        try:
            await self.app(scope, monitored_receive, monitored_send)
        finally:
            elapsed = (
                (responded_at if responded_at is not None else perf_counter()) - started
            ) * 1000
            route = getattr(scope.get("route"), "path", "__unmatched__")
            method = (
                scope["method"]
                if scope["method"]
                in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"}
                else "OTHER"
            )
            row = self.metrics.setdefault((method, route), RouteMetrics())
            row.requests += 1
            row.statuses[status] += 1
            row.latency_ms_total += elapsed
            row.latencies.append(elapsed)
            identity = scope.get("nexa.phoenix")
            structlog.get_logger().info(
                "http_request_completed",
                method=method,
                route=route,
                status_code=status,
                server_error=int(status >= 500),
                duration_ms=round(elapsed, 3),
                **({"trace_id": identity[0], "span_id": identity[1]} if identity else {}),
            )
