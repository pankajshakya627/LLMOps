from __future__ import annotations

import asyncio
from typing import Any

import httpx
import pytest

from app.core.config import Settings
from app.models.answer import AnswerDraft


@pytest.mark.parametrize("result", ["pass", "reject", "malformed", "error"])
def test_configured_guard_fails_closed(
    settings: Settings, monkeypatch: pytest.MonkeyPatch, result: str
) -> None:
    from app.chains.guardrails import validate_draft

    settings = settings.model_copy(update={"guardrails_base_url": "http://127.0.0.1:8101"})
    draft = AnswerDraft(
        status="insufficient_evidence", answer="No supported evidence.", evidence=[]
    )
    client_class = httpx.AsyncClient
    seen = []

    def respond(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if result == "error":
            raise httpx.ConnectError("offline", request=request)
        return httpx.Response(
            200,
            json=(
                {"validation_passed": result == "pass"}
                if result != "malformed"
                else {"validation_passed": "true"}
            ),
        )

    def client(**kwargs: Any) -> httpx.AsyncClient:
        return client_class(transport=httpx.MockTransport(respond), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client)
    if result == "pass":
        asyncio.run(validate_draft(draft, settings))
    else:
        with pytest.raises((ValueError, httpx.HTTPError)):
            asyncio.run(validate_draft(draft, settings))
    assert str(seen[0].url) == "http://127.0.0.1:8101/validate"


def test_unconfigured_guard_keeps_current_pydantic_path(settings: Settings) -> None:
    from app.chains.guardrails import validate_draft

    draft = AnswerDraft(status="insufficient_evidence", answer="No evidence.", evidence=[])
    asyncio.run(validate_draft(draft, settings))
