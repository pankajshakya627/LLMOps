from __future__ import annotations

import asyncio
from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.config import Settings
from app.models.answer import AnswerDraft
from app.models.retrieval import RetrieveRequest
from app.security import bedrock


def aws_settings(settings: Settings) -> Settings:
    return settings.model_copy(
        update={
            "bedrock_guardrail_id": "test-guardrail",
            "bedrock_guardrail_version": "1",
            "bedrock_region": "ap-south-1",
        }
    )


@pytest.mark.parametrize(
    "response", [{"action": "GUARDRAIL_INTERVENED"}, {}, {"action": "unknown"}]
)
def test_bedrock_rejects_intervention_and_malformed_decisions(
    settings: Settings, monkeypatch: pytest.MonkeyPatch, response: dict[str, str]
) -> None:
    client = Mock()
    client.apply_guardrail.return_value = response
    monkeypatch.setattr(bedrock, "runtime_client", lambda _: client)
    with pytest.raises(ValueError, match="Bedrock content check failed"):
        bedrock.check_content("synthetic input", "INPUT", aws_settings(settings))


def test_bedrock_errors_never_echo_content_or_provider_diagnostics(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = Mock()
    client.apply_guardrail.side_effect = RuntimeError("private input and provider diagnostics")
    monkeypatch.setattr(bedrock, "runtime_client", lambda _: client)
    with pytest.raises(ValueError) as error:
        bedrock.check_content("private input", "OUTPUT", aws_settings(settings))
    assert "private input" not in str(error.value)
    assert "provider diagnostics" not in str(error.value)


def test_unconfigured_bedrock_does_not_create_a_client(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = Mock(side_effect=AssertionError("AWS must not be called"))
    monkeypatch.setattr(bedrock, "runtime_client", client)
    bedrock.check_content("local request", "INPUT", settings)
    client.assert_not_called()


def test_input_guard_runs_after_redaction_and_before_any_embedding(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.services import retrieval

    client = Mock()
    client.apply_guardrail.return_value = {"action": "GUARDRAIL_INTERVENED"}
    embedding = Mock(side_effect=AssertionError("Embedding must not run after rejection"))
    monkeypatch.setattr(bedrock, "runtime_client", lambda _: client)
    monkeypatch.setattr(retrieval, "get_embeddings", embedding)
    request = RetrieveRequest(
        query="Email asha@example.com about the fee?", as_of=date(2026, 10, 1)
    )
    with pytest.raises(ValueError):
        asyncio.run(retrieval.retrieve_policy(request, aws_settings(settings)))
    sent = client.apply_guardrail.call_args.kwargs
    assert "asha@example.com" not in sent["content"][0]["text"]["text"]
    assert "[REDACTED_EMAIL]" in sent["content"][0]["text"]["text"]
    assert sent["source"] == "INPUT" and sent["guardrailVersion"] == "1"
    embedding.assert_not_called()


def test_output_guard_does_not_replace_the_existing_validator(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.chains import guardrails

    client = Mock()
    client.apply_guardrail.return_value = {"action": "NONE"}
    monkeypatch.setattr(bedrock, "runtime_client", lambda _: client)
    draft = AnswerDraft(status="insufficient_evidence", answer="No supported evidence", evidence=[])
    asyncio.run(guardrails.validate_draft(draft, aws_settings(settings)))
    assert client.apply_guardrail.call_args.kwargs["source"] == "OUTPUT"


def test_bedrock_outage_stops_output_before_sidecar(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.chains import guardrails

    client = Mock()
    client.apply_guardrail.side_effect = TimeoutError()
    monkeypatch.setattr(bedrock, "runtime_client", lambda _: client)
    http = AsyncMock()
    monkeypatch.setattr(guardrails.httpx, "AsyncClient", http)
    draft = AnswerDraft(status="insufficient_evidence", answer="No supported evidence", evidence=[])
    with pytest.raises(ValueError):
        asyncio.run(guardrails.validate_draft(draft, aws_settings(settings)))
    http.assert_not_called()


@pytest.mark.parametrize(
    "updates",
    [
        {"bedrock_guardrail_id": "g"},
        {"bedrock_guardrail_id": "g", "bedrock_guardrail_version": "1"},
        {"bedrock_guardrail_version": "1"},
        {"bedrock_guardrail_id": "g", "bedrock_guardrail_version": "DRAFT", "bedrock_region": "r"},
    ],
)
def test_partial_or_draft_guardrail_configuration_is_rejected(
    settings: Settings, updates: dict[str, str]
) -> None:
    with pytest.raises(ValueError):
        Settings(_env_file=None, **(settings.model_dump() | updates))
