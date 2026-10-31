from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.chains.llm import get_chat_model
from app.core.config import Settings


def test_answer_model_requests_carry_the_configured_output_cap(settings: Settings) -> None:
    capped = settings.model_copy(update={"chat_max_output_tokens": 1234})
    payload = get_chat_model(capped)._get_request_payload([HumanMessage("question")])
    assert payload["max_output_tokens"] == 1234


def test_cap_is_on_by_default_and_can_be_removed_for_judges(settings: Settings) -> None:
    assert settings.chat_max_output_tokens is not None
    uncapped = settings.model_copy(update={"chat_max_output_tokens": None})
    payload = get_chat_model(uncapped)._get_request_payload([HumanMessage("question")])
    assert "max_output_tokens" not in payload
