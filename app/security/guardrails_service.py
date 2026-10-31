from __future__ import annotations

import argparse
import json

from fastapi import FastAPI
from guardrails import Guard

from app.models.answer import AnswerDraft, GuardrailRequest, GuardrailResult

app = FastAPI(title="NexaAssist local output validation")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/validate")
def validate(payload: GuardrailRequest) -> GuardrailResult:
    # Guardrails may prune extras; reject invalid original JSON before normalization.
    try:
        AnswerDraft.model_validate_json(payload.llm_output)
    except ValueError:
        return GuardrailResult(validation_passed=False)
    # A fresh instance avoids sharing validation history across concurrent requests.
    guard = Guard(output_schema=AnswerDraft.model_json_schema(), use_server=False)
    guard.configure(allow_metrics_collection=False)
    result = guard.parse(llm_output=payload.llm_output, num_reasks=0)
    return GuardrailResult(validation_passed=result.validation_passed is True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Guardrails AI schema validation")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        from fastapi.testclient import TestClient

        good = {"status": "insufficient_evidence", "answer": "No evidence.", "evidence": []}
        answered = {
            "status": "answered",
            "answer": "Policy [1]",
            "evidence": [
                {"evidence_id": 1, "quote": "Policy"},
            ],
        }
        with TestClient(app) as client:
            for draft, expected in (
                (good, True),
                (answered, True),
                ({**good, "status": "approve_loan"}, False),
                ({**answered, "evidence": [{"evidence_id": -1, "quote": "Policy"}]}, False),
                ({**good, "unexpected": True}, False),
            ):
                response = client.post("/validate", json={"llm_output": json.dumps(draft)})
                assert response.status_code == 200
                assert response.json() == {"validation_passed": expected}, (draft, response.json())
        return
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8101)


if __name__ == "__main__":
    main()
