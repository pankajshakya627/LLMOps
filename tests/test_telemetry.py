from __future__ import annotations

import json
from unittest.mock import Mock

import pytest
import structlog
from ddtrace import tracer
from pydantic import ValidationError

from app.core import telemetry
from app.core.config import Settings
from app.core.logging import configure_logging
from app.core.observability import prompt_annotation_context


def test_json_logs_correlate_without_masking_ids_or_leaking_exceptions(capsys, monkeypatch):
    monkeypatch.setattr(tracer, "enabled", False)
    configure_logging("INFO")
    with tracer.trace("offline") as span:
        expected = f"{span.trace_id:032x}"
        try:
            raise ValueError("learner@example.com Bearer SYNTHETIC_SECRET")
        except ValueError:
            structlog.get_logger().exception("probe", api_key="SYNTHETIC_SECRET")
    structlog.get_logger().info("outside")
    inside, outside = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert inside["dd.trace_id"] == expected and inside["dd.span_id"] == str(span.span_id)
    assert inside["error_type"] == "ValueError"
    assert inside["api_key"] == "[REDACTED_SECRET]"
    assert "SYNTHETIC_SECRET" not in str(inside) and "learner@example.com" not in str(inside)
    assert "dd.trace_id" not in outside


def test_disabled_prompt_tracking_does_not_render_or_annotate():
    prompt = Mock()
    with prompt_annotation_context(prompt, {"query": "private"}, prompt_id="answer", version="1"):
        pass
    prompt.pretty_repr.assert_not_called()
    prompt.format_messages.assert_not_called()


def test_datadog_metrics_use_bounded_route_dimensions(monkeypatch):
    statsd = Mock()
    monkeypatch.setattr(telemetry, "statsd", statsd)
    telemetry.record_http_metrics("POST", "/answer", 503, 125)
    tags = ["method:POST", "route:/answer", "status_code:503"]
    statsd.increment.assert_any_call("http.requests", tags=tags)
    statsd.increment.assert_any_call("http.errors", tags=tags)
    statsd.distribution.assert_called_once_with("http.duration_ms", 125, tags=tags)


def test_datadog_settings_validate_keys_and_trusted_sites(settings):
    values = settings.model_dump()
    with pytest.raises(ValidationError, match="DD_API_KEY"):
        Settings(_env_file=None, **{**values, "dd_llmobs_enabled": True, "dd_api_key": None})
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{**values, "dd_site": "attacker.invalid"})
    assert "dd_api_key" in Settings.model_fields


def test_agentless_metrics_use_http_without_a_docker_agent(monkeypatch, settings):
    import datadog
    from ddtrace import config
    from pydantic import SecretStr

    initialize = Mock()
    thread_stats = Mock()
    monkeypatch.setattr(datadog, "initialize", initialize)
    monkeypatch.setattr(datadog, "ThreadStats", thread_stats)
    monkeypatch.setattr(telemetry, "statsd", None)
    monkeypatch.setitem(config.tags, "lab_session_id", "offline-session")
    telemetry.configure_telemetry(
        settings.model_copy(
            update={
                "dd_metrics_enabled": True,
                "dd_llmobs_agentless_enabled": True,
                "dd_api_key": SecretStr("synthetic"),
            }
        )
    )
    initialize.assert_called_once_with(api_key="synthetic", api_host="https://api.datadoghq.com")
    thread_stats.return_value.start.assert_called_once_with()
    assert "lab_session_id:offline-session" in thread_stats.call_args.kwargs["constant_tags"]
    telemetry.record_http_metrics("GET", "/health", 200, 5)
    thread_stats.return_value.distribution.assert_called_once()
