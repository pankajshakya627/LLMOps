"""Metadata-only LangChain trace trees in the session's CloudWatch log stream."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

import structlog
from langchain_core.tracers.base import BaseTracer
from langchain_core.tracers.schemas import Run

_active: ContextVar[list[Any] | None] = ContextVar("aws_trace_active", default=None)


class CloudWatchTraceLogger(BaseTracer):
    def _persist_run(self, run: Run) -> None:
        self._log_tree(run)

    def _log_tree(self, run: Run) -> None:
        # Export an allowlist; Run also holds prompts, outputs and exception messages.
        structlog.get_logger().info(
            "chain_span_completed",
            trace_id=str(run.trace_id),
            span_id=str(run.id),
            parent_span_id=str(run.parent_run_id) if run.parent_run_id else None,
            span_name=run.name,
            run_type=run.run_type,
            duration_ms=round((run.end_time - run.start_time).total_seconds() * 1000, 3)
            if run.end_time
            else None,
            failed=bool(run.error),
        )
        for child in run.child_runs:
            self._log_tree(child)


@contextmanager
def trace_callbacks(enabled: bool) -> Iterator[list[Any]]:
    """Nested service calls inherit the parent's callback without duplicate export."""
    if not enabled:
        yield []
        return
    existing = _active.get()
    if existing is not None:
        yield []
        return
    callbacks = [CloudWatchTraceLogger()]
    token = _active.set(callbacks)
    try:
        yield callbacks
    finally:
        _active.reset(token)
