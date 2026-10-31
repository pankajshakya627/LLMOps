"""Attach a saved /answer/evaluated response to its Phoenix HTTP server span."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

import httpx
import structlog

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.models.evaluation import EvaluatedAnswerResponse

if TYPE_CHECKING:
    from phoenix.client.resources.spans import SpanAnnotationData


def load_span_id(path: Path) -> str:
    identifiers = set()
    for line in path.read_text().splitlines():
        name, separator, value = line.partition(":")
        if separator and name.strip().lower() == "x-phoenix-span-id":
            identifiers.add(value.strip().lower())
    if len(identifiers) != 1:
        raise ValueError("Expected one Phoenix span ID from the evaluated response headers")
    identifier = identifiers.pop()
    if not re.fullmatch(r"[0-9a-f]{16}", identifier) or int(identifier, 16) == 0:
        raise ValueError("Invalid Phoenix span ID")
    return identifier


def build_annotations(response: EvaluatedAnswerResponse, span_id: str) -> list[SpanAnnotationData]:
    annotations: list[SpanAnnotationData] = []
    for name, metric in response.quality.metrics.items():
        annotation: SpanAnnotationData = {
            "span_id": span_id,
            "name": f"ragas_{name}",
            "annotator_kind": "LLM" if metric.status == "scored" else "CODE",
            "result": {"label": metric.status},
            "metadata": {"reference_source": response.quality.reference_source},
        }
        if metric.status == "scored":
            assert metric.value is not None
            annotation["result"]["score"] = metric.value
        else:
            annotation["result"]["explanation"] = metric.reason or "Metric was not scored."
        annotations.append(annotation)
    return annotations


def publish_annotations(
    response: EvaluatedAnswerResponse, span_id: str, settings: Settings
) -> None:
    """Publish existing scores; never generate an answer or invoke an evaluator."""
    from phoenix.client import Client

    annotations = build_annotations(response, span_id)
    with httpx.Client(base_url=settings.phoenix_base_url, timeout=10, trust_env=False) as transport:
        client = Client(
            base_url=settings.phoenix_base_url,
            api_key=settings.phoenix_api_key.get_secret_value()
            if settings.phoenix_api_key
            else None,
            http_client=transport,
        )
        for attempt in range(6):
            try:
                client.spans.log_span_annotations(span_annotations=annotations, sync=True)
                break
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 404 or attempt == 5:
                    raise
                # A response can precede the batched server span's ingestion.
                sleep(2)
    structlog.get_logger().info(
        "phoenix_evaluations_published", span_id=span_id, count=len(annotations)
    )


def publish_annotations_safely(
    response: EvaluatedAnswerResponse, span_id: str, settings: Settings
) -> None:
    """A collector outage must not replace a completed answer with an HTTP failure."""
    try:
        publish_annotations(response, span_id, settings)
    except (ValueError, ImportError, httpx.HTTPError) as exc:
        structlog.get_logger().warning(
            "phoenix_evaluation_export_failed", span_id=span_id, error_type=type(exc).__name__
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--headers", required=True, type=Path)
    args = parser.parse_args()
    configure_logging("INFO")
    try:
        settings = get_settings()
        response = EvaluatedAnswerResponse.model_validate_json(args.response.read_text())
        publish_annotations(response, load_span_id(args.headers), settings)
    except (OSError, ValueError, ImportError, httpx.HTTPError) as exc:
        structlog.get_logger().error(
            "phoenix_evaluation_export_failed", error_type=type(exc).__name__
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
