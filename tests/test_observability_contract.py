from __future__ import annotations

import ast
import tomllib
from pathlib import Path

from app.core.config import Settings
from app.models.answer import AnswerResponse

ROOT = Path(__file__).resolve().parents[1]


def test_application_has_one_observability_provider() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    dependencies = project["project"]["dependencies"]
    assert any(item.startswith("ddtrace") for item in dependencies)
    assert not any(item.startswith("arize-phoenix-otel") for item in dependencies)
    for path in (ROOT / "app").rglob("*.py"):
        if "results" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                assert all(
                    not item.name.startswith(("phoenix", "openinference")) for item in node.names
                ), path
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith(("phoenix", "openinference")), path


def test_api_contracts_expose_datadog_and_keep_historical_feedback_readable() -> None:
    assert {"datadog_trace_id", "datadog_span_id"} <= AnswerResponse.model_fields.keys()
    assert "dd_api_key" in Settings.model_fields
    assert AnswerResponse.model_fields["phoenix_trace_id"].deprecated
    assert AnswerResponse.model_fields["phoenix_span_id"].deprecated
