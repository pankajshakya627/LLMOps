from __future__ import annotations

import pytest

from app.api.limits import reset_limiters
from app.core.config import Settings


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    # _env_file=None still reads process variables; keep offline fixtures independent of them.
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    return Settings(
        _env_file=None,
        mongodb_uri="mongodb://unused",
        mongodb_db="unused",
        mongodb_collection="chunks",
        openai_api_key="unused",
        institution="NexaBank",
        jurisdiction="IN",
        confidentiality_level="internal",
    )


@pytest.fixture(autouse=True)
def clean_rate_limits() -> None:
    reset_limiters()
