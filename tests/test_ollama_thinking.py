from __future__ import annotations

from pathlib import Path

import yaml
from langchain_core.messages import HumanMessage

from app.chains.llm import get_chat_model
from app.core.config import Settings
from app.evaluation.profiles import judge_settings


def test_local_structured_output_disables_thinking_without_removing_the_cap(
    settings: Settings,
) -> None:
    local = Settings.model_validate(
        {
            **settings.model_dump(),
            "chat_base_url": "http://127.0.0.1:11434/v1",
            "chat_api_key": "ollama",
            "chat_api_mode": "chat_completions",
            "chat_reasoning_effort": "none",
        }
    )
    payload = get_chat_model(local)._get_request_payload([HumanMessage("Synthetic question")])
    assert payload["reasoning_effort"] == "none"
    assert payload["extra_body"]["max_tokens"] == 2000


def test_local_thinking_control_does_not_change_the_judge(settings: Settings) -> None:
    candidate = settings.model_copy(
        update={"chat_reasoning_effort": "none", "openai_fallback_model": "cloud-fallback"}
    )
    assert judge_settings(candidate).chat_reasoning_effort is None
    assert judge_settings(candidate).openai_fallback_model is None


def test_gateway_can_clear_the_candidate_thinking_override(settings: Settings) -> None:
    gateway = Settings.model_validate({**settings.model_dump(), "chat_reasoning_effort": ""})
    assert gateway.chat_reasoning_effort is None


def test_gateway_thinking_policy_applies_only_to_local_chat_deployments() -> None:
    for name in ("litellm.yaml", "litellm_balanced.yaml", "litellm_cache.yaml"):
        config = yaml.safe_load((Path("app/gateway") / name).read_text())
        for deployment in config["model_list"]:
            params = deployment["litellm_params"]
            if params["model"].startswith("ollama_chat/"):
                assert params["reasoning_effort"] == "none"
            else:
                assert "reasoning_effort" not in params
