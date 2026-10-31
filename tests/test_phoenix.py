from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.core.config import Settings
from app.core.phoenix import capture_request, correlate_response
from app.evaluation import phoenix_export
from app.evaluation.phoenix_export import build_annotations, load_span_id
from app.models.evaluation import EvaluatedAnswerResponse


def test_phoenix_headers_identify_the_server_span_not_the_send_span() -> None:
    server = Mock()
    server.get_span_context.return_value = SimpleNamespace(is_valid=True, trace_id=123, span_id=456)
    scope: dict = {}
    capture_request(server, scope)
    message: dict = {
        "type": "http.response.start",
        "headers": [(b"content-type", b"application/json")],
    }
    correlate_response(Mock(), scope, message)
    headers = dict(message["headers"])
    assert headers[b"x-phoenix-trace-id"] == b"0000000000000000000000000000007b"
    assert headers[b"x-phoenix-span-id"] == b"00000000000001c8"
    assert headers[b"content-type"] == b"application/json"


def test_phoenix_does_not_claim_a_trace_for_an_invalid_context() -> None:
    server = Mock()
    server.get_span_context.return_value = SimpleNamespace(is_valid=False)
    scope: dict = {}
    capture_request(server, scope)
    message: dict = {"type": "http.response.start", "headers": []}
    correlate_response(Mock(), scope, message)
    assert message["headers"] == []


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


def test_phoenix_export_keeps_unavailable_metrics_distinct_from_zero(
    evaluated_response: EvaluatedAnswerResponse,
) -> None:
    annotations = build_annotations(evaluated_response, "0123456789abcdef")
    values = {item["name"]: item for item in annotations}
    assert values["ragas_faithfulness"]["result"]["score"] == 0.9
    assert values["ragas_answer_relevancy"]["result"]["score"] == 0
    assert values["ragas_context_precision"]["result"] == {
        "label": "unavailable",
        "explanation": "No reference.",
    }
    assert values["ragas_context_recall"]["result"]["label"] == "error"
    assert all(item["span_id"] == "0123456789abcdef" for item in annotations)
    assert "Synthetic answer" not in str(annotations)


@pytest.mark.parametrize("span_id", ["", "123", "0000000000000000", "not-a-span-id"])
def test_phoenix_export_rejects_missing_or_invalid_span_ids(tmp_path: Path, span_id: str) -> None:
    headers = tmp_path / "response.headers"
    headers.write_text(f"HTTP/1.1 200 OK\r\nX-Phoenix-Span-Id: {span_id}\r\n\r\n")
    with pytest.raises(ValueError, match="Phoenix span"):
        load_span_id(headers)


def test_phoenix_export_reads_the_actual_curl_response_header(tmp_path: Path) -> None:
    headers = tmp_path / "response.headers"
    headers.write_text("HTTP/1.1 200 OK\r\nx-phoenix-span-id: 0123456789abcdef\r\n\r\n")
    assert load_span_id(headers) == "0123456789abcdef"


def test_export_cli_configures_the_actual_http_transport_and_closes_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    evaluated_response: EvaluatedAnswerResponse,
) -> None:
    response = tmp_path / "response.json"
    response.write_text(evaluated_response.model_dump_json())
    headers = tmp_path / "response.headers"
    headers.write_text("HTTP/1.1 200 OK\r\nx-phoenix-span-id: 0123456789abcdef\r\n\r\n")
    constructor = Mock()
    monkeypatch.setitem(sys.modules, "phoenix.client", SimpleNamespace(Client=constructor))
    monkeypatch.setattr(phoenix_export, "get_settings", lambda: settings)
    monkeypatch.setattr(
        sys, "argv", ["export", "--response", str(response), "--headers", str(headers)]
    )
    phoenix_export.main()
    transport = constructor.call_args.kwargs["http_client"]
    assert str(transport.base_url) == settings.phoenix_base_url
    assert transport.is_closed
    publish = constructor.return_value.spans.log_span_annotations
    assert publish.call_args.kwargs["sync"] is True
    assert len(publish.call_args.kwargs["span_annotations"]) == 4


@pytest.mark.parametrize("span", [None, Mock(is_recording=lambda: False)])
def test_non_recording_requests_do_not_get_phoenix_headers(span: object) -> None:
    scope: dict = {}
    capture_request(span, scope)
    message: dict = {"type": "http.response.start", "headers": []}
    correlate_response(None, scope, message)
    assert scope == {}
    assert message["headers"] == []


def test_phoenix_identity_is_request_scoped_and_never_added_to_response_body() -> None:
    server = Mock()
    server.get_span_context.return_value = SimpleNamespace(is_valid=True, trace_id=1, span_id=2)
    traced: dict = {}
    capture_request(server, traced)
    body: dict = {"type": "http.response.body", "body": b"answer"}
    correlate_response(None, traced, body)
    assert body == {"type": "http.response.body", "body": b"answer"}
    unrelated: dict = {"type": "http.response.start"}
    correlate_response(None, {}, unrelated)
    assert "headers" not in unrelated
    start: dict = {"type": "http.response.start"}
    correlate_response(None, traced, start)
    assert dict(start["headers"])[b"x-phoenix-span-id"] == b"0000000000000002"


def test_export_rejects_conflicting_header_ids_instead_of_mislabeling_a_trace(
    tmp_path: Path,
) -> None:
    headers = tmp_path / "redirected.headers"
    headers.write_text("x-phoenix-span-id: 0123456789abcdef\nX-Phoenix-Span-Id: fedcba9876543210\n")
    with pytest.raises(ValueError, match="Expected one Phoenix span"):
        load_span_id(headers)


def test_export_normalizes_equivalent_duplicate_header_ids(tmp_path: Path) -> None:
    headers = tmp_path / "response.headers"
    headers.write_text("x-phoenix-span-id: 0123456789ABCDEF\nX-Phoenix-Span-Id: 0123456789abcdef\n")
    assert load_span_id(headers) == "0123456789abcdef"


@pytest.mark.parametrize("failure", ["missing_file", "invalid_response", "http_failure"])
def test_export_failure_exits_unsuccessfully_and_closes_any_open_transport(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    evaluated_response: EvaluatedAnswerResponse,
    failure: str,
) -> None:
    import httpx

    response = tmp_path / "response.json"
    if failure != "missing_file":
        response.write_text(
            "{}" if failure == "invalid_response" else evaluated_response.model_dump_json()
        )
    headers = tmp_path / "response.headers"
    headers.write_text("x-phoenix-span-id: 0123456789abcdef\n")
    constructor = Mock()
    constructor.return_value.spans.log_span_annotations.side_effect = httpx.ConnectError("private")
    monkeypatch.setitem(sys.modules, "phoenix.client", SimpleNamespace(Client=constructor))
    monkeypatch.setattr(phoenix_export, "get_settings", lambda: settings)
    monkeypatch.setattr(
        sys, "argv", ["export", "--response", str(response), "--headers", str(headers)]
    )
    with pytest.raises(SystemExit) as stopped:
        phoenix_export.main()
    assert stopped.value.code == 1
    if failure == "http_failure":
        assert constructor.call_args.kwargs["http_client"].is_closed
    else:
        constructor.assert_not_called()


@pytest.mark.parametrize("status,recovers", [(404, True), (404, False), (401, False), (500, False)])
def test_annotation_export_retries_only_spans_pending_batch_ingestion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    evaluated_response: EvaluatedAnswerResponse,
    status: int,
    recovers: bool,
) -> None:
    import httpx

    response = tmp_path / "response.json"
    response.write_text(evaluated_response.model_dump_json())
    headers = tmp_path / "headers.txt"
    headers.write_text("x-phoenix-span-id: 0123456789abcdef\n")
    request = httpx.Request("POST", "http://collector.invalid/v1/span_annotations")
    error = httpx.HTTPStatusError(
        "Not ready", request=request, response=httpx.Response(status, request=request)
    )
    constructor = Mock()
    publish = constructor.return_value.spans.log_span_annotations
    publish.side_effect = [error, None] if recovers else error
    pause = Mock()
    monkeypatch.setattr(phoenix_export, "sleep", pause, raising=False)
    monkeypatch.setitem(sys.modules, "phoenix.client", SimpleNamespace(Client=constructor))
    monkeypatch.setattr(phoenix_export, "get_settings", lambda: settings)
    monkeypatch.setattr(
        sys, "argv", ["export", "--response", str(response), "--headers", str(headers)]
    )
    if recovers:
        phoenix_export.main()
        assert publish.call_count == 2
        pause.assert_called_once_with(2)
    else:
        with pytest.raises(SystemExit) as stopped:
            phoenix_export.main()
        assert stopped.value.code == 1
        assert publish.call_count == (6 if status == 404 else 1)
        assert pause.call_count == (5 if status == 404 else 0)
    assert constructor.call_args.kwargs["http_client"].is_closed


@pytest.mark.parametrize("capture", [False, True])
def test_request_span_records_final_response_only_when_capture_is_enabled(
    monkeypatch: pytest.MonkeyPatch,
    evaluated_response: EvaluatedAnswerResponse,
    capture: bool,
) -> None:
    import json

    from app.core.phoenix import record_result

    span = Mock()
    span.get_span_context.return_value = SimpleNamespace(is_valid=True)
    monkeypatch.setattr("app.core.phoenix.trace.get_current_span", lambda: span)
    record_result(evaluated_response, capture_content=capture)
    attributes = dict(call.args for call in span.set_attribute.call_args_list)
    if capture:
        assert attributes["output.mime_type"] == "application/json"
        payload = json.loads(attributes["output.value"])
        assert payload["answer"]["answer"] == "Synthetic answer."
        assert payload["quality"]["metrics"]["faithfulness"]["value"] == 0.9
    else:
        span.set_attribute.assert_not_called()


def test_final_response_does_not_claim_output_without_a_valid_span(
    monkeypatch: pytest.MonkeyPatch,
    evaluated_response: EvaluatedAnswerResponse,
) -> None:
    from app.core.phoenix import record_result

    span = Mock()
    span.get_span_context.return_value = SimpleNamespace(is_valid=False)
    monkeypatch.setattr("app.core.phoenix.trace.get_current_span", lambda: span)
    record_result(evaluated_response, capture_content=True)
    span.set_attribute.assert_not_called()


def test_evaluated_api_schedules_annotations_for_its_own_span(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    evaluated_response: EvaluatedAnswerResponse,
) -> None:
    from unittest.mock import AsyncMock

    from fastapi.testclient import TestClient

    from app.api import answer as api
    from app.core.config import get_settings
    from app.main import create_app

    evaluated_response.answer.phoenix_span_id = "0123456789abcdef"
    publisher = Mock()
    monkeypatch.setattr(api, "answer_with_quality", AsyncMock(return_value=evaluated_response))
    monkeypatch.setattr(api, "publish_annotations_safely", publisher)
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr("app.main.get_settings", lambda: settings)
    with TestClient(app) as client:
        response = client.post(
            "/answer/evaluated", json={"query": "Maximum loan?", "as_of": "2026-10-01"}
        )
    assert response.status_code == 200
    assert response.json()["quality"]["metrics"]["faithfulness"]["value"] == 0.9
    publisher.assert_called_once_with(evaluated_response, "0123456789abcdef", settings)


def test_annotation_background_failure_is_reported_without_raising(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    evaluated_response: EvaluatedAnswerResponse,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import httpx

    publish = Mock(side_effect=httpx.ConnectError("collector unavailable"))
    monkeypatch.setattr(phoenix_export, "publish_annotations", publish)
    phoenix_export.publish_annotations_safely(evaluated_response, "0123456789abcdef", settings)
    assert "phoenix_evaluation_export_failed" in capsys.readouterr().out
    publish.assert_called_once_with(evaluated_response, "0123456789abcdef", settings)
