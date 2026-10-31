from __future__ import annotations

import importlib
import json
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


def test_guardrails_sidecar_validates_without_remote_server_or_reasks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    guard = Mock()
    guard.parse.return_value = SimpleNamespace(validation_passed=True)
    constructor = Mock(return_value=guard)
    monkeypatch.setitem(sys.modules, "guardrails", SimpleNamespace(Guard=constructor))
    module = importlib.import_module("app.security.guardrails_service")
    module = importlib.reload(module)
    payload = json.dumps(
        {"status": "insufficient_evidence", "answer": "No evidence.", "evidence": []}
    )
    with TestClient(module.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        constructor.assert_not_called()
        result = client.post("/validate", json={"llm_output": payload})
        assert result.status_code == 200 and result.json() == {"validation_passed": True}
        assert (
            client.post("/validate", json={"llm_output": payload, "extra": True}).status_code == 422
        )
        assert client.post("/validate", json={"llm_output": "not JSON"}).json() == {
            "validation_passed": False
        }
        assert client.post(
            "/validate", json={"llm_output": payload[:-1] + ', "extra": true}'}
        ).json() == {"validation_passed": False}
    assert constructor.call_args.kwargs["use_server"] is False
    guard.configure.assert_called_with(allow_metrics_collection=False)
    assert guard.parse.call_args.kwargs == {"llm_output": payload, "num_reasks": 0}
