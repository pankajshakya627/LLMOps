from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from contextlib import nullcontext
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal

import httpx
import structlog
from ddtrace.llmobs import LLMObs
from langchain_core.runnables import RunnableLambda
from langchain_core.tracers.run_collector import RunCollectorCallbackHandler
from pydantic import BaseModel, ConfigDict, Field

from app.chains.answer import build_answer_chain
from app.chains.context import assemble_context
from app.chains.embeddings import get_embeddings
from app.chains.llm import get_chat_model
from app.chains.prompts.answer import ANSWER_PROMPT_ID, ANSWER_PROMPT_SHA, ANSWER_PROMPT_VERSION
from app.chains.prompts.judge import JUDGE_PROMPT, JUDGE_PROMPT_ID, JUDGE_VERSION
from app.chains.redaction import redact
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.observability import prompt_annotation_context
from app.database.retrieval import resolve_reference_contexts
from app.evaluation.answer_evaluation import ExpectedEvidence
from app.evaluation.datadog_export import publish_annotations
from app.evaluation.gates import gate_failures, load_gates
from app.evaluation.profiles import judge_settings, metric_settings
from app.evaluation.retrieval_eval import classify_failure, score_retrieval
from app.models.evaluation import METRIC_NAMES, AnswerQuality, QualityScore
from app.models.retrieval import RetrieveRequest, RetrieveResponse
from app.services.retrieval import retrieve_policy, scrub_request

ROOT = Path(__file__).resolve().parents[2]
logger = structlog.get_logger()


class GoldenCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input: RetrieveRequest
    expected_output: str
    context: list[dict[str, Any]]
    expected_status: Literal["answered", "insufficient_evidence", "needs_clarification"] = (
        "answered"
    )


class JudgeScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    correctness: float = Field(ge=0, le=1, allow_inf_nan=False)
    groundedness: float = Field(ge=0, le=1, allow_inf_nan=False)
    rationale: str


def load_cases(path: Path) -> list[GoldenCase]:
    cases = [
        GoldenCase.model_validate_json(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]
    if not cases:
        raise ValueError("Evaluation dataset is empty")
    return cases


def case_fingerprint(case: GoldenCase) -> str:
    canonical = json.dumps(case.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def trace_summary(runs: list[Any]) -> list[dict[str, Any]]:
    spans = []
    for run in runs:
        spans.append(
            {
                "name": run.name,
                "run_type": run.run_type,
                "duration_ms": round((run.end_time - run.start_time).total_seconds() * 1000, 2)
                if run.end_time
                else None,
                "failed": bool(run.error),
            }
        )
        spans.extend(trace_summary(run.child_runs))
    return spans


async def collect_records(cases: list[GoldenCase], settings: Settings) -> list[dict[str, Any]]:
    """Generate once per case; evaluate the exact evidence passed to that generation."""
    model = get_chat_model(settings)
    judge_config = judge_settings(settings)
    judge = JUDGE_PROMPT | get_chat_model(judge_config).with_structured_output(
        JudgeScore, method="json_schema", strict=True
    )
    records = []
    for case in cases:
        request = scrub_request(case.input, settings)
        reference_contexts = await asyncio.to_thread(
            resolve_reference_contexts, settings, case.context
        )
        collector = RunCollectorCallbackHandler()

        async def retrieve(request: RetrieveRequest) -> RetrieveResponse:
            return await retrieve_policy(request, settings)

        retrieved = (
            await RunnableLambda(retrieve)
            .with_config(run_name="evaluation_retrieval")
            .ainvoke(request, config={"callbacks": [collector]})
        )
        sources = assemble_context(
            retrieved.evidence, settings.context_max_tokens, settings.token_encoding
        )

        def replay(
            _request: RetrieveRequest, evidence: RetrieveResponse = retrieved
        ) -> RetrieveResponse:
            return evidence

        chain = build_answer_chain(RunnableLambda(replay), model, settings)
        answer = await chain.ainvoke(request, config={"callbacks": [collector]})
        record: dict[str, Any] = {
            "case_id": case_fingerprint(case),
            "user_input": request.query,
            "response": answer.answer,
            "reference": redact(case.expected_output)[0]
            if settings.redact_queries
            else case.expected_output,
            "reference_contexts": reference_contexts,
            "retrieved_contexts": [hit.parent_text for hit in sources.values()],
            "expected_status": case.expected_status,
            "actual_status": answer.status,
        }
        judge_variables = {"record": json.dumps(record, ensure_ascii=False)}
        with prompt_annotation_context(
            JUDGE_PROMPT,
            judge_variables,
            prompt_id=JUDGE_PROMPT_ID,
            version=JUDGE_VERSION,
        ):
            score = JudgeScore.model_validate(await judge.ainvoke(judge_variables))
        retrieval = (
            score_retrieval(
                retrieved,
                [ExpectedEvidence.model_validate(item) for item in case.context],
                case.input.top_k,
            )
            if case.context
            else None
        )
        record.update(
            request=request.model_dump(mode="json"),
            provenance=answer.provenance.model_dump() if answer.provenance else None,
            retrieval_timings=retrieved.timings.model_dump(),
            generation_ms=answer.generation_ms,
            trace=trace_summary(collector.traced_runs),
            judge={
                **score.model_dump(),
                "status_matches": answer.status == case.expected_status,
            },
            retrieval=retrieval,
        )
        record["failure_type"] = classify_failure(
            case.expected_status,
            retrieval["recall_at_k"] if retrieval else None,
            record["judge"],
        )
        records.append(record)
    return records


async def evaluate_ragas(records: list[dict[str, Any]], settings: Settings) -> dict[str, Any]:
    from app.evaluation.ragas_metrics import RagasScorer

    eligible = [record for record in records if record["expected_status"] == "answered"]
    if not eligible:
        return {"status": "not_applicable", "case_count": 0, "scores": [], "means": {}}
    scores = []
    scorer = RagasScorer(
        get_chat_model(judge_settings(settings)), get_embeddings(metric_settings(settings))
    )
    for record in eligible:
        question, response = record["user_input"], record["response"]
        contexts, reference = record["retrieved_contexts"], record["reference"]
        if not contexts:
            # Retrieval failed for an answerable case. Do not give abstention a free pass.
            scores.append(dict.fromkeys(METRIC_NAMES, 0.0))
            continue
        results = await asyncio.gather(
            *(
                asyncio.wait_for(
                    scorer.metrics[name].ascore(
                        user_input=question,
                        **({"retrieved_contexts": contexts} if name != "answer_relevancy" else {}),
                        **(
                            {"response": response}
                            if name in ("faithfulness", "answer_relevancy")
                            else {"reference": reference}
                        ),
                    ),
                    timeout=120,
                )
                for name in METRIC_NAMES
            )
        )
        row = {}
        for name, result in zip(METRIC_NAMES, results, strict=True):
            metric = QualityScore(status="scored", value=float(result.value))
            assert metric.value is not None  # A scored QualityScore always has a value.
            row[name] = metric.value
        scores.append(row)
    means = {key: sum(row[key] for row in scores) / len(scores) for key in scores[0]}
    return {"status": "completed", "case_count": len(scores), "scores": scores, "means": means}


def quality_gate(report: dict[str, Any], minimum: float | None) -> bool:
    if minimum is None:
        return True
    values = list(report["ragas"]["means"].values())
    values.extend(
        record["judge"][key]
        for record in report["records"]
        for key in ("correctness", "groundedness")
    )
    return (
        bool(values)
        and all(value >= minimum for value in values)
        and all(record["judge"]["status_matches"] for record in report["records"])
    )


async def run(cases: list[GoldenCase], settings: Settings) -> dict[str, Any]:
    with LLMObs.workflow(name="evaluation.batch") if LLMObs.enabled else nullcontext():
        records = await collect_records(cases, settings)
        ragas = await evaluate_ragas(records, settings)
        exported = LLMObs.export_span() if LLMObs.enabled else None
        identity = (
            {"trace_id": exported["trace_id"].zfill(32), "span_id": exported["span_id"]}
            if exported else None
        )
        if identity:
            LLMObs.annotate(tags={"evaluation_scope": "batch_mean", "case_count": str(len(cases))})
            quality = AnswerQuality(
                metrics={
                    name: QualityScore(status="scored", value=ragas["means"][name])
                    if ragas["status"] == "completed"
                    else QualityScore(status="unavailable")
                    for name in METRIC_NAMES
                },
                reference_source="golden_dataset",
                evaluated_at=datetime.now(UTC),
            )
            try:
                publish_annotations(quality, identity, settings)
            except (ValueError, httpx.HTTPError) as exc:
                logger.warning("datadog_evaluation_export_failed", error_type=type(exc).__name__)
    return {
        "status": "completed",
        "datadog_span": identity,
        "captured_at": datetime.now(UTC).isoformat(),
        "dataset_sha256": hashlib.sha256(
            "\n".join(sorted(case_fingerprint(case) for case in cases)).encode()
        ).hexdigest(),
        "answer_prompt": {
            "id": ANSWER_PROMPT_ID,
            "version": ANSWER_PROMPT_VERSION,
            "sha": ANSWER_PROMPT_SHA,
        },
        "model": settings.chat_model,
        "judge_model": judge_settings(settings).chat_model,
        "evaluation_profiles": {
            "judge_endpoint": settings.eval_judge_base_url,
            "judge_api_mode": settings.eval_judge_api_mode,
            "metric_embedding_model": settings.eval_embedding_model,
            "metric_embedding_dimensions": settings.eval_embedding_dimensions,
            "metric_embedding_endpoint": settings.eval_embedding_base_url,
            "metric_embedding_profile": settings.eval_embedding_profile,
        },
        "judge_prompt_version": JUDGE_VERSION,
        "judge_limitation": "Stochastic scoring; review with humans."
        + (
            " Same-model self-preference is possible."
            if judge_settings(settings).chat_model == settings.chat_model
            else " A separate judge model does not guarantee independent errors."
        ),
        "retrieval_mode": settings.retrieval_mode,
        "rerank_enabled": settings.rerank_enabled,
        "rerank_model": settings.rerank_model if settings.rerank_enabled else None,
        "ragas_version": version("ragas"),
        "empty_context_policy": "Answerable cases with no evidence receive zero metrics.",
        "records": records,
        "ragas": ragas,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 1 RAGAS and LLM-as-Judge evaluation")
    parser.add_argument("--dataset", type=Path, default=ROOT / "app/evaluation/datasets/answer.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "app/evaluation/results/latest.json")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--gates", type=Path, default=ROOT / "app/evaluation/gates.json", help="Per-metric thresholds"
    )
    parser.add_argument(
        "--min-score",
        type=float,
        help="Uniform 0–1 minimum; replaces the per-metric thresholds in --gates",
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    if args.min_score is not None and not 0 <= args.min_score <= 1:
        parser.error("--min-score must be between 0 and 1")
    configure_logging("INFO")
    try:
        cases = load_cases(args.dataset)
        settings = get_settings()
        if settings.dd_llmobs_enabled:
            from app.core.telemetry import configure_telemetry

            configure_telemetry(settings)
        report = asyncio.run(run(cases[: args.limit], settings))
        report["dataset"] = str(args.dataset)
        if args.min_score is not None:
            passed = quality_gate(report, args.min_score)
            report["gate"] = {"minimum": args.min_score, "status": "passed" if passed else "failed"}
        else:
            gates = load_gates(args.gates)
            failures = gate_failures(report, gates)
            report["gate"] = {
                "source": str(args.gates),
                "thresholds": gates.status,
                "status": "failed" if failures else "passed",
                "failures": failures,
            }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
        structlog.get_logger().info(
            "evaluation_completed",
            output=str(args.output),
            cases=len(report["records"]),
            gate=report["gate"],
        )
    except Exception as exc:
        logger.exception("evaluation_failed", error_type=type(exc).__name__)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(
                {
                    "status": "failed",
                    "captured_at": datetime.now(UTC).isoformat(),
                    "error_type": type(exc).__name__,
                    "gate": {"status": "failed"},
                },
                indent=2,
            )
        )
        raise SystemExit(1) from None
    finally:
        if LLMObs.enabled:
            LLMObs.flush()
    if report["gate"]["status"] == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
