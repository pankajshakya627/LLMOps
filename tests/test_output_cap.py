from __future__ import annotations

from pathlib import Path

import yaml
from langchain_core.messages import HumanMessage

from app.chains.llm import get_chat_model
from app.core.config import Settings


def test_answer_model_requests_carry_the_configured_output_cap(settings: Settings) -> None:
    capped = settings.model_copy(update={"chat_max_output_tokens": 1234})
    payload = get_chat_model(capped)._get_request_payload([HumanMessage("question")])
    assert payload["max_output_tokens"] == 1234


def test_aws_api_can_delegate_output_limits_to_the_private_gateway(
    monkeypatch, settings: Settings
) -> None:
    compose = yaml.safe_load(Path("app/compose.aws.yaml").read_text())
    monkeypatch.setenv(
        "CHAT_MAX_OUTPUT_TOKENS",
        compose["services"]["api"]["environment"]["CHAT_MAX_OUTPUT_TOKENS"],
    )
    configured = Settings(
        **settings.model_dump(exclude={"chat_max_output_tokens", "chat_api_mode"}),
        chat_api_mode="chat_completions",
    )
    assert configured.chat_max_output_tokens is None
    assert "max_tokens" not in get_chat_model(configured)._get_request_payload(
        [HumanMessage("question")]
    ).get("extra_body", {})


def test_cap_is_on_by_default_and_can_be_removed_for_judges(settings: Settings) -> None:
    assert settings.chat_max_output_tokens is not None
    uncapped = settings.model_copy(update={"chat_max_output_tokens": None})
    payload = get_chat_model(uncapped)._get_request_payload([HumanMessage("question")])
    assert "max_output_tokens" not in payload
