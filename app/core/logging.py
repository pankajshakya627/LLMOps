from __future__ import annotations

import logging
import sys
from collections.abc import MutableMapping
from typing import Any

import structlog
from structlog.typing import Processor

from app.core.telemetry import trace_log_context


def private_log(_logger: Any, _method: str, event: MutableMapping[str, Any]) -> dict[str, Any]:
    from app.core.http_monitoring import safe_content

    exception = event.pop("exc_info", None)
    if exception:
        error = (
            exception[1]
            if isinstance(exception, tuple)
            else (sys.exc_info()[1] if exception is True else exception)
        )
        event["error_type"] = type(error).__name__
    # Identifiers can contain digit sequences that resemble phone numbers.
    identity_keys = {"dd.trace_id", "dd.span_id", "llmobs.trace_id", "llmobs.span_id"}
    safe = dict(
        safe_content({key: value for key, value in event.items() if key not in identity_keys})
    )
    safe.update({key: value for key, value in event.items() if key in identity_keys})
    return safe


def configure_logging(level: str) -> None:
    """JSON stdout logs collected by the Agent with Datadog trace correlation."""
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        trace_log_context,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        private_log,
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelNamesMapping()[level]),
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, *processors],
        )
    )
    logging.getLogger().handlers = [handler]
    logging.getLogger().setLevel(level)
    for name in ("uvicorn", "uvicorn.error"):
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    # The middleware's access event omits query strings, headers and payloads.
    logging.getLogger("uvicorn.access").disabled = True
