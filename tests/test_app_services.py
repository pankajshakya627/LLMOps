from __future__ import annotations

from pathlib import Path

import yaml


def test_application_owns_gateway_and_guardrail_services() -> None:
    for name in ("litellm.yaml", "litellm_cache.yaml", "litellm_balanced.yaml"):
        config = yaml.safe_load((Path("app/gateway") / name).read_text())
        aliases = {item["model_name"] for item in config["model_list"]}
        assert {"nexa-chat-openai", "nexa-embed-local", "nexa-embed-openai"} <= aliases
        assert config["router_settings"]["max_fallbacks"] == 1
        for route in config["model_list"]:
            if route["model_name"] in {"nexa-chat-openai", "nexa-embed-openai"}:
                assert route["litellm_params"]["api_base"] == "https://api.openai.com/v1"
    assert Path("app/security/guardrails_service.py").is_file()
    assert "training" not in Path("app/security/guardrails_service.py").read_text()


def test_compose_connects_private_services_and_keeps_one_fallback_owner() -> None:
    services = yaml.safe_load(Path("app/compose.yaml").read_text())["services"]
    assert {"api", "ui", "gateway", "guardrails", "datadog-agent"} <= services.keys()
    api = services["api"]["environment"]
    assert api["CHAT_BASE_URL"] == "http://gateway:4000/v1"
    assert api["EMBEDDING_BASE_URL"] == "http://gateway:4000/v1"
    assert api["GUARDRAILS_BASE_URL"] == "http://guardrails:8101"
    assert api["DD_LLMOBS_AGENTLESS_ENABLED"] == "true"
    assert services["datadog-agent"]["profiles"] == ["local-agent"]
    assert api["OPENAI_FALLBACK_MODEL"] == ""
    assert api["CHAT_REASONING_EFFORT"] == ""
    assert services["ui"]["environment"]["API_BASE_URL"] == "http://api:8000"
    for service in services.values():
        assert all(port.startswith("127.0.0.1:") for port in service.get("ports", []))
    assert "env_file" not in services["ui"] and "env_file" not in services["guardrails"]


def test_docker_build_context_excludes_private_configuration() -> None:
    ignored = Path(".dockerignore").read_text().splitlines()
    assert ".env" in ignored and "**/.env" in ignored and ".venv" in ignored


def test_non_root_validator_image_normalizes_copied_source_permissions() -> None:
    dockerfile = Path("app/security/Dockerfile").read_text()
    source_copies = [
        line for line in dockerfile.splitlines() if line.startswith("COPY") and "app/" in line
    ]
    assert len(source_copies) == 4
    assert all("--chmod=" in line for line in source_copies)
    assert "USER guardrails" in dockerfile
