from __future__ import annotations

import json
import sys
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.evaluation import datadog_export as export
from app.main import create_app
from app.models.evaluation import EvaluatedAnswerResponse

IDENTITY = {"trace_id": "1" * 32, "span_id": "1234567890123456789"}


@pytest.fixture
def evaluated_response() -> EvaluatedAnswerResponse:
    return EvaluatedAnswerResponse.model_validate(
        {
            "answer": {
                "as_of": "2026-10-01",
                "status": "answered",
                "answer": "Synthetic answer.",
                "citations": [],
                "generation_ms": 1,
                "retrieval_timings": {"search_ms": 1, "parent_ms": 0, "total_ms": 1},
            },
            "quality": {
                "metrics": {
                    "faithfulness": {"status": "scored", "value": 0.9},
                    "answer_relevancy": {"status": "scored", "value": 0.0},
                    "context_precision": {"status": "unavailable", "reason": "No reference."},
                    "context_recall": {"status": "error", "reason": "Judge timeout."},
                },
                "reference_source": "none",
                "evaluated_at": "2026-10-24T00:00:00Z",
            },
        }
    )


def test_scores_keep_zero_unavailable_and_error_distinct(evaluated_response):
    annotations = export.build_annotations(evaluated_response.quality, IDENTITY)
    values = {item["label"]: item for item in annotations}
    assert values["ragas_faithfulness"]["score_value"] == 0.9
    assert values["ragas_answer_relevancy"]["score_value"] == 0
    assert values["ragas_context_precision_status"]["categorical_value"] == "unavailable"
    assert values["ragas_context_recall_status"]["categorical_value"] == "error"
    assert "score_value" not in values["ragas_context_precision_status"]
    assert all(item["join_on"]["span"] == IDENTITY for item in annotations)
    assert "Synthetic answer" not in str(annotations)


@pytest.mark.parametrize(
    "trace_id,span_id",
    [
        ("", "123"),
        ("0" * 32, "123"),
        ("1" * 32, "0"),
        ("1" * 32, "abc"),
        ("1" * 32, "123\nx-datadog-span-id: 456"),
    ],
)
def test_export_rejects_invalid_or_conflicting_identity(tmp_path, trace_id, span_id):
    headers = tmp_path / "response.headers"
    headers.write_text(f"x-datadog-trace-id: {trace_id}\nx-datadog-span-id: {span_id}\n")
    with pytest.raises(ValueError, match="Datadog"):
        export.load_span_id(headers)


def test_export_reads_equivalent_duplicate_headers(tmp_path):
    headers = tmp_path / "response.headers"
    headers.write_text(
        "HTTP/1.1 200 OK\nX-Datadog-Trace-Id: "
        + "A" * 32
        + "\nx-datadog-trace-id: "
        + "a" * 32
        + "\nx-datadog-span-id: 123\n"
    )
    assert export.load_span_id(headers) == {"trace_id": "a" * 32, "span_id": "123"}


@pytest.mark.parametrize("status", [202, 400, 401, 403, 404, 429, 500])
def test_export_uses_correct_site_and_closes_transport(
    monkeypatch, settings, evaluated_response, status
):
    from pydantic import SecretStr

    settings = settings.model_copy(
        update={"dd_api_key": SecretStr("synthetic-key"), "dd_site": "datadoghq.eu"}
    )
    sent = []

    def respond(request):
        sent.append(request)
        return httpx.Response(status)

    transport = httpx.Client(transport=httpx.MockTransport(respond))
    monkeypatch.setattr(export.httpx, "Client", lambda **kwargs: transport)
    if status == 202:
        export.publish_annotations(evaluated_response.quality, IDENTITY, settings)
    else:
        with pytest.raises(httpx.HTTPStatusError):
            export.publish_annotations(evaluated_response.quality, IDENTITY, settings)
    assert transport.is_closed
    assert str(sent[0].url) == "https://api.datadoghq.eu/api/intake/llm-obs/v2/eval-metric"
    assert sent[0].headers["DD-API-KEY"] == "synthetic-key"
    payload = json.loads(sent[0].content)["data"]["attributes"]["metrics"]
    assert len(payload) == 4 and all(item["join_on"]["span"] == IDENTITY for item in payload)
    assert all(item["ml_app"] == settings.dd_llmobs_ml_app for item in payload)


def test_background_outage_does_not_replace_completed_answer(
    monkeypatch, settings, evaluated_response, capsys
):
    settings = settings.model_copy(update={"dd_llmobs_enabled": True})
    evaluated_response.answer.datadog_trace_id = IDENTITY["trace_id"]
    evaluated_response.answer.datadog_span_id = IDENTITY["span_id"]
    publish = Mock(side_effect=httpx.ConnectError("Bearer SYNTHETIC_SECRET"))
    monkeypatch.setattr(export, "publish_annotations", publish)
    export.publish_annotations_safely(evaluated_response, settings)
    output = capsys.readouterr().out
    assert "datadog_evaluation_export_failed" in output and "SYNTHETIC_SECRET" not in output
    publish.assert_called_once_with(evaluated_response.quality, IDENTITY, settings)


def test_disabled_export_makes_no_network_call(monkeypatch, settings, evaluated_response):
    publish = Mock()
    monkeypatch.setattr(export, "publish_annotations", publish)
    export.publish_annotations_safely(evaluated_response, settings)
    publish.assert_not_called()


def test_evaluated_api_schedules_its_own_identity(monkeypatch, settings, evaluated_response):
    from app.api import answer as api

    evaluated_response.answer.datadog_trace_id = IDENTITY["trace_id"]
    evaluated_response.answer.datadog_span_id = IDENTITY["span_id"]
    publisher = Mock()
    monkeypatch.setattr(api, "answer_with_quality", AsyncMock(return_value=evaluated_response))
    monkeypatch.setattr(api, "publish_annotations_safely", publisher)
    monkeypatch.setattr("app.main.get_settings", lambda: settings)
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as client:
        response = client.post(
            "/answer/evaluated", json={"query": "Maximum loan?", "as_of": "2026-10-01"}
        )
    assert response.status_code == 200
    assert response.json()["quality"]["metrics"]["faithfulness"]["value"] == 0.9
    publisher.assert_called_once_with(evaluated_response, settings)


@pytest.mark.parametrize(
    "failure", ["missing_file", "invalid_response", "mismatched_identity", "http_failure"]
)
def test_cli_fails_explicitly_for_invalid_recovery(
    monkeypatch, tmp_path, settings, evaluated_response, failure
):
    path = tmp_path / "response.json"
    if failure != "missing_file":
        path.write_text(
            "{}" if failure == "invalid_response" else evaluated_response.model_dump_json()
        )
    headers = tmp_path / "response.headers"
    headers.write_text(
        f"x-datadog-trace-id: {IDENTITY['trace_id']}\nx-datadog-span-id: {IDENTITY['span_id']}\n"
    )
    if failure == "http_failure":
        evaluated_response.answer.datadog_trace_id = IDENTITY["trace_id"]
        evaluated_response.answer.datadog_span_id = IDENTITY["span_id"]
        path.write_text(evaluated_response.model_dump_json())
    publish = Mock(side_effect=httpx.ConnectError("synthetic outage"))
    monkeypatch.setattr(export, "publish_annotations", publish)
    monkeypatch.setattr(export, "get_settings", lambda: settings)
    monkeypatch.setattr(sys, "argv", ["export", "--response", str(path), "--headers", str(headers)])
    with pytest.raises(SystemExit) as stopped:
        export.main()
    assert stopped.value.code == 1
    assert publish.call_count == (1 if failure == "http_failure" else 0)
