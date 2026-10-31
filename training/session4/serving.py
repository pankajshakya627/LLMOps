"""Exercise the actual FastAPI app with injected offline services."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import httpx
from pymongo.errors import ServerSelectionTimeoutError

from app.core.config import Settings, get_settings
from app.main import create_app
from training.console import say


async def main() -> None:
    settings = Settings(
        _env_file=None,
        mongodb_uri="mongodb://unused",
        mongodb_db="unused",
        mongodb_collection="unused",
        openai_api_key="unused",
        institution="NexaBank",
        jurisdiction="IN",
        confidentiality_level="internal",
        rate_limit_per_minute=2,
    )
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://lab"
    ) as client:
        healthy = await client.get("/health")
        assert healthy.status_code == 200
        say("liveness:", healthy.status_code)
        with patch(
            "app.api.operations.check_ready",
            AsyncMock(side_effect=ServerSelectionTimeoutError("secret")),
        ):
            ready = await client.get("/ready")
        assert ready.status_code == 503 and "secret" not in ready.text
        say("database unavailable: readiness=503, detail hidden")
        with patch("app.api.answer.answer_policy", AsyncMock(side_effect=TimeoutError("secret"))):
            statuses = [
                (
                    await client.post("/answer", json={"query": "fee", "as_of": "2026-10-01"})
                ).status_code
                for _ in range(3)
            ]
        assert statuses == [503, 503, 429]
        say("two provider failures then rate limit:", statuses)
        invalid = await client.post("/retrieve", json={"query": "", "as_of": "2026-10-01"})
        assert invalid.status_code == 422
        say("invalid input: 422")
    say("ASGI transport does not run lifespan: telemetry startup is covered by separate tests.")


if __name__ == "__main__":
    asyncio.run(main())
