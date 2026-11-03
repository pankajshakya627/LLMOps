"""Publish existing Ragas scores to the matching Datadog workflow span."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import httpx
import structlog

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.models.evaluation import AnswerQuality, EvaluatedAnswerResponse


def load_span_id(path: Path) -> dict[str, str]:
    identity = {}
    for name, pattern in (("trace_id", r"[0-9a-f]{32}"), ("span_id", r"[1-9][0-9]{0,19}")):
        values = {
            value.strip().lower()
            for line in path.read_text().splitlines()
            for key, separator, value in [line.partition(":")]
            if separator and key.strip().lower() == f"x-datadog-{name.replace('_', '-')}"
        }
        if len(values) != 1:
            raise ValueError(f"Expected one Datadog {name} from the evaluated response headers")
        value = values.pop()
        base = 16 if name == "trace_id" else 10
        if not re.fullmatch(pattern, value) or int(value, base) == 0:
            raise ValueError(f"Invalid Datadog {name}")
        identity[name] = value
    return identity


def build_annotations(quality: AnswerQuality, identity: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "event_kind": "evaluation",
            "eval_scope": "span",
            "join_on": {"span": identity},
            "label": f"ragas_{name}" + ("" if metric.status == "scored" else "_status"),
            "metric_type": "score" if metric.status == "scored" else "categorical",
            **(
                {"score_value": metric.value}
                if metric.status == "scored"
                else {"categorical_value": metric.status}
            ),
            "timestamp_ms": int(quality.evaluated_at.timestamp() * 1000),
            "tags": [f"reference_source:{quality.reference_source}", f"status:{metric.status}"],
        }
        for name, metric in quality.metrics.items()
    ]


def publish_annotations(
    quality: AnswerQuality, identity: dict[str, str], settings: Settings
) -> None:
    if not settings.dd_api_key or not settings.dd_api_key.get_secret_value():
        raise ValueError("DD_API_KEY is required to publish Datadog evaluations")
    annotations = build_annotations(quality, identity)
    for annotation in annotations:
        annotation["ml_app"] = settings.dd_llmobs_ml_app
    with httpx.Client(timeout=10, trust_env=False) as transport:
        response = transport.post(
            f"https://api.{settings.dd_site}/api/intake/llm-obs/v2/eval-metric",
            headers={"DD-API-KEY": settings.dd_api_key.get_secret_value()},
            json={"data": {"type": "evaluation_metric", "attributes": {"metrics": annotations}}},
        )
        response.raise_for_status()
    structlog.get_logger().info("datadog_evaluations_published", **identity, count=len(annotations))


def publish_annotations_safely(response: EvaluatedAnswerResponse, settings: Settings) -> None:
    answer = response.answer
    if not settings.dd_llmobs_enabled or not (answer.datadog_trace_id and answer.datadog_span_id):
        return
    try:
        publish_annotations(
            response.quality,
            {"trace_id": answer.datadog_trace_id, "span_id": answer.datadog_span_id},
            settings,
        )
    except (ValueError, httpx.HTTPError) as exc:
        structlog.get_logger().warning(
            "datadog_evaluation_export_failed", error_type=type(exc).__name__
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--headers", required=True, type=Path)
    args = parser.parse_args()
    configure_logging("INFO")
    try:
        response = EvaluatedAnswerResponse.model_validate_json(args.response.read_text())
        identity = load_span_id(args.headers)
        if identity != {
            "trace_id": response.answer.datadog_trace_id,
            "span_id": response.answer.datadog_span_id,
        }:
            raise ValueError("Response and header files must belong to the same Datadog span")
        publish_annotations(response.quality, identity, get_settings())
    except (OSError, ValueError, httpx.HTTPError) as exc:
        structlog.get_logger().error(
            "datadog_evaluation_export_failed", error_type=type(exc).__name__
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
