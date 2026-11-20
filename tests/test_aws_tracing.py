from __future__ import annotations

import asyncio

import pytest
import structlog
from langchain_core.runnables import RunnableLambda
from structlog.testing import capture_logs

from app.core.aws_tracing import trace_callbacks
from app.core.logging import private_log


def test_trace_tree_preserves_parent_and_request_correlation_without_content() -> None:
    async def run() -> None:
        async def child(value: str) -> str:
            return "private output"

        async def parent(value: str) -> str:
            with trace_callbacks(True) as nested:
                assert nested == []
                return await RunnableLambda(child).ainvoke(
                    value, config={"callbacks": nested} if nested else None
                )

        with trace_callbacks(True) as callbacks:
            await RunnableLambda(parent).ainvoke("private input", config={"callbacks": callbacks})

    with (
        capture_logs(processors=[structlog.contextvars.merge_contextvars]) as logs,
        structlog.contextvars.bound_contextvars(request_id="request-1"),
    ):
        asyncio.run(run())
    spans = [row for row in logs if row["event"] == "chain_span_completed"]
    assert len(spans) == 2
    assert all(row["request_id"] == "request-1" for row in spans)
    root, child = spans
    assert child["trace_id"] == root["trace_id"]
    assert child["parent_span_id"] == root["span_id"]
    assert root["parent_span_id"] is None
    assert all(row["duration_ms"] >= 0 and row["failed"] is False for row in spans)
    assert "private input" not in str(spans) and "private output" not in str(spans)
    assert private_log(None, "info", root)["span_id"] == root["span_id"]


def test_trace_failure_omits_exception_content_and_resets_context() -> None:
    async def run() -> None:
        def fail(value: str) -> str:
            raise ValueError("private failure detail")

        with (
            trace_callbacks(True) as callbacks,
            pytest.raises(ValueError, match="private failure detail"),
        ):
            await RunnableLambda(fail).ainvoke("secret", config={"callbacks": callbacks})
        with trace_callbacks(True) as fresh:
            assert len(fresh) == 1
        with trace_callbacks(False) as disabled:
            assert disabled == []

    with capture_logs() as logs:
        asyncio.run(run())
    spans = [row for row in logs if row["event"] == "chain_span_completed"]
    assert len(spans) == 1 and spans[0]["failed"] is True
    assert "private failure detail" not in str(spans)
