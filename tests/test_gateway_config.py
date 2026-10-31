from __future__ import annotations

from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize(
    "filename", ["litellm.yaml", "litellm_balanced.yaml", "litellm_cache.yaml"]
)
def test_gateway_configs_bound_retries_and_keep_embeddings_out_of_fallback(filename: str) -> None:
    config = yaml.safe_load((Path("app/gateway") / filename).read_text())
    router = config["router_settings"]
    assert router["num_retries"] <= 1 and router["timeout"] <= 30
    assert router["max_fallbacks"] == 1
    for entry in router.get("fallbacks", []):
        assert all("embed" not in alias for alias in entry)


def test_balancing_requires_two_independent_deployments() -> None:
    config = yaml.safe_load(Path("app/gateway/litellm_balanced.yaml").read_text())
    deployments = [m for m in config["model_list"] if m["model_name"] == "nexa-chat-balanced"]
    assert len(deployments) == 2
    assert len({m["litellm_params"]["api_base"] for m in deployments}) == 2
    assert config["router_settings"]["routing_strategy"] == "simple-shuffle"


def test_cache_is_opt_in_local_and_only_for_chat() -> None:
    standard = yaml.safe_load(Path("app/gateway/litellm.yaml").read_text())
    cache = yaml.safe_load(Path("app/gateway/litellm_cache.yaml").read_text())
    assert standard["litellm_settings"]["cache"] is False
    params = cache["litellm_settings"]["cache_params"]
    assert cache["litellm_settings"]["cache"] is True and params["type"] == "local"
    assert params["supported_call_types"] == ["completion", "acompletion"]
    assert params["default_in_memory_ttl"] == 300


@pytest.mark.parametrize(
    "filename", ["litellm.yaml", "litellm_balanced.yaml", "litellm_cache.yaml"]
)
def test_gateway_profiles_export_actual_model_calls_to_phoenix(filename: str) -> None:
    config = yaml.safe_load((Path("app/gateway") / filename).read_text())
    assert config["litellm_settings"]["callbacks"] == ["arize_phoenix"]


def test_gateway_phoenix_traces_keep_message_capture_disabled() -> None:
    compose = yaml.safe_load(Path("app/compose.yaml").read_text())
    gateway = compose["services"]["gateway"]
    env = gateway["environment"]
    assert env["LITELLM_OTEL_V2"] == "true"
    assert env["PHOENIX_PROJECT_NAME"] == "nexaassist-gateway"
    assert env["PHOENIX_COLLECTOR_HTTP_ENDPOINT"] == "http://phoenix:6006/v1/traces"
    assert env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] == "no_content"
    assert gateway["depends_on"]["phoenix"]["condition"] == "service_started"
