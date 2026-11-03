from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.mark.parametrize("capture", [False, True])
def test_native_datadog_monitoring_masks_content_and_correlates_models(capture):
    result = subprocess.run(
        [sys.executable, "tests/runtime/datadog_profile_check.py", str(capture).lower()],
        env={**os.environ, "PYTHONPATH": str(Path.cwd())},
        capture_output=True,
        text=True,
        timeout=40,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    logs = [json.loads(line) for line in result.stdout.splitlines() if line.startswith("{") and json.loads(line).get("event") == "http_request_completed"]
    assert logs
    assert all(re.fullmatch(r"[0-9a-f]{32}", row["dd.trace_id"]) for row in logs)
    assert all(row["dd.span_id"] == row["llmobs.span_id"] for row in logs)
    assert all(row["service"] == "nexaassist-api" for row in logs)
    assert any(row["status_code"] == 503 and row["route"] == "/unavailable" for row in logs)


def test_disabled_monitoring_keeps_local_metrics_without_claiming_trace(settings, monkeypatch):
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr("app.main.get_settings", lambda: settings)
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.json() == {"status": "ok"}
        assert not any(key.startswith("x-datadog-") for key in response.headers)
        rows = client.get("/metrics/http").json()["routes"]
    assert next(row for row in rows if row["route"] == "/health")["requests"] == 1
    assert next(row for row in rows if row["route"] == "/answer/evaluated")["requests"] == 0
