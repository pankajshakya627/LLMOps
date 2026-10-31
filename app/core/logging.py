from __future__ import annotations

import logging

import structlog

from app.core.phoenix import trace_log_context


def configure_logging(level: str) -> None:
    """JSON logs on stdout with the active OpenTelemetry trace and span IDs."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            trace_log_context,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelNamesMapping()[level]),
    )
