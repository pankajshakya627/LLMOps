from __future__ import annotations

import ast
import tomllib
from pathlib import Path

from app.core.config import Settings
from app.models.answer import AnswerResponse
from app.models.evaluation import AnswerQuality

ROOT = Path(__file__).resolve().parents[1]


def test_application_has_one_observability_provider() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    dependencies = project["project"]["dependencies"]
    assert not any(item.startswith("ddtrace") for item in dependencies)
    assert any(item.startswith("arize-phoenix-otel") for item in dependencies)
    for path in (ROOT / "app").rglob("*.py"):
        if "results" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                assert all(not item.name.startswith("ddtrace") for item in node.names), path
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("ddtrace"), path


def test_api_contracts_expose_phoenix_without_retired_fields() -> None:
    for model in (Settings, AnswerResponse, AnswerQuality):
        assert not any(name.startswith(("dd_", "datadog_")) for name in model.model_fields)
    assert {"phoenix_trace_id", "phoenix_span_id"} <= AnswerResponse.model_fields.keys()
