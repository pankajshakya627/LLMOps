"""Run one paid golden trial through the AWS gateway with the fixed OpenAI judge."""

import argparse
import asyncio
import json
from pathlib import Path

from app.core.config import get_settings
from app.evaluation.gates import load_gates
from app.evaluation.run import case_fingerprint, collect_records, load_cases

HERE = Path(__file__).resolve().parent


async def trial(model: str, number: int, output: Path) -> None:
    settings = get_settings().model_copy(
        update={"chat_model": model, "openai_fallback_model": None}
    )
    if (
        settings.eval_judge_model != "nexa-judge-openai"
        or settings.embedding_model != "nexa-embed-openai"
    ):
        raise ValueError("Provider comparison requires the OpenAI judge and embedding profile")
    cases = load_cases(HERE / "datasets/answer.jsonl")
    gates = load_gates(HERE / "gates.json")
    # Exclusive creation preserves prior trials. A partial file is evidence of an interrupted run.
    with output.open("x") as stream:
        for case in cases:
            row = {
                "case_id": case_fingerprint(case),
                "trial": number,
                "model": model,
                "judge_model": settings.eval_judge_model,
                "embedding_profile": settings.embedding_profile,
                "critical": case.expected_status != "answered",
            }
            try:
                (record,) = await collect_records([case], settings)
                judge = record["judge"]
                row.update(
                    passed=judge["status_matches"]
                    and judge["correctness"] >= gates.judge_correctness_min
                    and judge["groundedness"] >= gates.judge_groundedness_min,
                    actual_status=record["actual_status"],
                    expected_status=case.expected_status,
                    correctness=judge["correctness"],
                    groundedness=judge["groundedness"],
                    observed_model=(record.get("provenance") or {}).get("observed_chat_model"),
                )
            except Exception as error:  # noqa: BLE001 - keep failed cases in the paired result set.
                row.update(passed=False, error_type=type(error).__name__)
            stream.write(json.dumps(row) + "\n")
            stream.flush()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", required=True, choices=["nexa-chat-openai", "nexa-chat-anthropic"]
    )
    parser.add_argument("--trial", required=True, type=int, choices=[1, 2, 3])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(trial(args.model, args.trial, args.output))


if __name__ == "__main__":
    main()
