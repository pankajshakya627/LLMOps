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
def test_gateway_profiles_export_actual_model_calls_to_datadog(filename: str) -> None:
    config = yaml.safe_load((Path("app/gateway") / filename).read_text())
    assert config["litellm_settings"]["callbacks"] == ["datadog_callback.datadog_callback"]


def test_gateway_datadog_traces_keep_message_capture_disabled() -> None:
    compose = yaml.safe_load(Path("app/compose.yaml").read_text())
    gateway = compose["services"]["gateway"]
    env = gateway["environment"]
    assert env["DD_SERVICE"] == "nexaassist-gateway"
    assert env["DD_AGENT_HOST"] == "datadog-agent"
    assert env["DD_LLMOBS_AGENTLESS_ENABLED"] == "true"
    assert "datadog-agent" not in gateway.get("depends_on", {})
    for path in Path("app/gateway").glob("litellm*.yaml"):
        assert (
            yaml.safe_load(path.read_text())["litellm_settings"]["turn_off_message_logging"] is True
        )


def test_gateway_callback_keeps_error_type_without_private_details(monkeypatch):
    import runpy
    import sys
    from types import SimpleNamespace

    class BaseCallback:
        def create_llm_obs_payload(self, kwargs, start_time, end_time):
            return {"tags": ["env:dev"], "name": "provider-call"}

        def _assemble_error_info(self, payload):
            return payload

    monkeypatch.setitem(
        sys.modules,
        "litellm.integrations.datadog.datadog_llm_obs",
        SimpleNamespace(DataDogLLMObsLogger=BaseCallback),
    )
    callback = runpy.run_path("app/gateway/datadog_callback.py")["datadog_callback"]
    assert callback._assemble_error_info(None) is None
    error = callback._assemble_error_info(
        {"type": "ProviderError", "message": "private", "stack": "private"}
    )
    assert error == {"type": "ProviderError", "message": "", "stack": ""}
    monkeypatch.setenv("DD_TAGS", "session:nexa-lab-training,lab_session_id:offline-session")
    payload = callback.create_llm_obs_payload({}, None, None)
    assert payload == {
        "name": "provider-call",
        "tags": ["env:dev", "session:nexa-lab-training", "lab_session_id:offline-session"],
    }
