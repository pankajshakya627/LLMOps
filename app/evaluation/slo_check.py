"""Deploy gate: compare a running API's /metrics/answers with the SLOs in app/evaluation/gates.json.

    python -m app.evaluation.slo_check [--base-url http://127.0.0.1:8000]

Metrics are process-local and cover the last 1000 requests; they are not a fleet-wide SLO.
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Any

import httpx
import structlog

from app.core.logging import configure_logging
from app.evaluation.gates import Gates, load_gates

ROOT = Path(__file__).resolve().parents[2]


def check_slo(metrics: dict[str, Any], gates: Gates) -> list[dict[str, Any]]:
    """Each SLO is pass, fail, or not_measured (no traffic, or cost prices unconfigured)."""
    measured = metrics["sample_count"] > 0
    sampled = metrics["sampled_count"] > 0
    targets = (
        ("p95_ms", metrics["p95_ms"], gates.p95_total_ms_max, measured),
        ("error_rate", metrics["answer_error_rate"], gates.error_rate_max, measured),
        (
            "cost_per_query_usd",
            metrics["cost_per_query_usd"],
            gates.cost_per_query_usd_max,
            measured,
        ),
        # Rollback trigger: 1 - faithfulness of sampled live answers (needs LIVE_EVAL_SAMPLE_RATE).
        (
            "hallucination_rate",
            metrics["sampled_hallucination_rate"],
            gates.hallucination_rate_rollback,
            sampled,
        ),
    )
    results = []
    for name, value, maximum, available in targets:
        if not available or value is None:
            status = "not_measured"
        else:
            status = "fail" if value > maximum else "pass"
        results.append({"slo": name, "value": value, "maximum": maximum, "status": status})
    return results


async def fetch_metrics(base_url: str) -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=base_url, timeout=10) as client:
        response = await client.get("/metrics/answers")
        response.raise_for_status()
        metrics: dict[str, Any] = response.json()
        return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Check answer SLOs against a running API")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--gates", type=Path, default=ROOT / "app/evaluation/gates.json")
    args = parser.parse_args()
    configure_logging("INFO")
    results = check_slo(asyncio.run(fetch_metrics(args.base_url)), load_gates(args.gates))
    structlog.get_logger().info("slo_check", results=results)
    if any(item["status"] == "fail" for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
