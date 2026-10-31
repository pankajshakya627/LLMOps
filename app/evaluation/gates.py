"""Quality and SLO thresholds, kept as data so a gate failure names the metric and the case."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Fraction = Field(ge=0, le=1, allow_inf_nan=False)


class Gates(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # "placeholder" values are course examples that the owner has not yet confirmed.
    status: Literal["placeholder", "confirmed"]
    faithfulness_min: float = Fraction
    answer_relevancy_min: float = Fraction
    context_precision_min: float = Fraction
    context_recall_min: float = Fraction
    judge_correctness_min: float = Fraction
    judge_groundedness_min: float = Fraction
    status_match_rate_min: float = Fraction
    p95_total_ms_max: float = Field(gt=0, allow_inf_nan=False)
    cost_per_query_usd_max: float = Field(gt=0, allow_inf_nan=False)
    error_rate_max: float = Fraction
    hallucination_rate_rollback: float = Fraction
    # Largest tolerated drop in any aggregate metric between two evaluation runs.
    regression_tolerance: float = Fraction


def load_gates(path: Path) -> Gates:
    return Gates.model_validate_json(path.read_text())


def gate_failures(report: dict[str, Any], gates: Gates) -> list[dict[str, Any]]:
    """Offline quality gate: aggregate means plus the cases that fell short."""
    records = report["records"]
    failures: list[dict[str, Any]] = []

    def check(metric: str, value: float, minimum: float) -> None:
        if value < minimum:
            failures.append({"metric": metric, "value": round(value, 4), "minimum": minimum})

    for name, value in report["ragas"]["means"].items():
        check(name, value, getattr(gates, f"{name}_min"))
    for key in ("correctness", "groundedness"):
        if records:
            check(
                f"judge_{key}",
                sum(r["judge"][key] for r in records) / len(records),
                getattr(gates, f"judge_{key}_min"),
            )
    if records:
        rate = sum(r["judge"]["status_matches"] for r in records) / len(records)
        check("status_match_rate", rate, gates.status_match_rate_min)
    failures.extend(
        {"case": r["user_input"]}
        for r in records
        if not r["judge"]["status_matches"]
        or r["judge"]["correctness"] < gates.judge_correctness_min
        or r["judge"]["groundedness"] < gates.judge_groundedness_min
    )
    return failures
