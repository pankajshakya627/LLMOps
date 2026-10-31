from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api import answer as answer_api
from app.core.config import Settings, get_settings
from app.core.rate_limit import SlidingWindowLimiter
from app.main import create_app
from app.models.answer import AnswerResponse
from app.models.retrieval import RetrieveTimings

BODY = {"query": "fee", "as_of": "2026-10-01"}


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_limiter_allows_up_to_the_limit_then_reports_retry_after() -> None:
    clock = Clock()
    limiter = SlidingWindowLimiter(limit=2, window_seconds=60, clock=clock)
    assert limiter.check("a") is None
    clock.now = 10
    assert limiter.check("a") is None
    clock.now = 20
    assert limiter.check("a") == pytest.approx(40)  # oldest request leaves at t=60
    assert limiter.check("b") is None  # other clients are independent


def test_limiter_frees_capacity_when_requests_age_out() -> None:
    clock = Clock()
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60, clock=clock)
    assert limiter.check("a") is None
    clock.now = 59.9
    assert limiter.check("a") is not None
    clock.now = 60.1
    assert limiter.check("a") is None


def test_limiter_forgets_idle_clients_so_memory_stays_bounded() -> None:
    clock = Clock()
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60, clock=clock, max_clients=3)
    for name in "abc":
        limiter.check(name)
    clock.now = 120
    limiter.check("d")  # triggers a purge of expired clients
    assert limiter.tracked_clients == 1


def test_active_client_capacity_rejects_new_identities_without_evicting_existing_limits() -> None:
    clock = Clock()
    limiter = SlidingWindowLimiter(limit=2, window_seconds=60, clock=clock, max_clients=3)
    for name in "abc":
        assert limiter.check(name) is None
    for number in range(100):
        assert limiter.check(f"new-{number}") is not None
    assert limiter.tracked_clients == 3
    assert limiter.check("a") is None
    assert limiter.check("a") == pytest.approx(60)


def test_new_clients_can_enter_after_capacity_expires() -> None:
    clock = Clock()
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60, clock=clock, max_clients=1)
    assert limiter.check("a") is None
    clock.now = 59
    assert limiter.check("b") is not None
    clock.now = 60
    assert limiter.check("b") is None
    assert limiter.tracked_clients == 1


def _client(settings: Settings, per_minute: int) -> TestClient:
    limited = settings.model_copy(
        update={
            "rate_limit_per_minute": per_minute,
            "feedback_reviewer_token": SecretStr("reviewer-test-token-000000000000000000"),
        }
    )
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: limited
    return TestClient(app)


def _answer() -> AnswerResponse:
    return AnswerResponse(
        as_of=date(2026, 10, 1),
        status="insufficient_evidence",
        answer="a",
        citations=[],
        retrieval_timings=RetrieveTimings(search_ms=0, parent_ms=0, total_ms=0),
        generation_ms=0,
    )


def test_answer_endpoints_share_one_bucket_and_return_429_with_retry_after(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    monkeypatch.setattr(answer_api, "answer_policy", AsyncMock(return_value=_answer()))
    # A failing evaluated answer (503) still counts against the shared answer bucket.
    monkeypatch.setattr(answer_api, "answer_with_quality", AsyncMock(side_effect=TimeoutError))
    client = _client(settings, per_minute=2)
    assert client.post("/answer", json=BODY).status_code == 200
    assert client.post("/answer/evaluated", json=BODY).status_code == 503
    blocked = client.post("/answer", json=BODY)
    assert blocked.status_code == 429
    assert blocked.json() == {"detail": "Rate limit exceeded"}
    assert 1 <= int(blocked.headers["Retry-After"]) <= 60


def test_feedback_has_its_own_bucket_and_limits_reviewer_guessing(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    monkeypatch.setattr(answer_api, "answer_policy", AsyncMock(return_value=_answer()))
    client = _client(settings, per_minute=2)
    for _ in range(2):
        assert client.get("/feedback", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get("/feedback", headers={"Authorization": "Bearer wrong"}).status_code == 429
    assert client.post("/answer", json=BODY).status_code == 200  # answer bucket untouched


def test_zero_disables_the_limit_and_operational_routes_are_never_limited(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    monkeypatch.setattr(answer_api, "answer_policy", AsyncMock(return_value=_answer()))
    off = _client(settings, per_minute=0)
    assert all(off.post("/answer", json=BODY).status_code == 200 for _ in range(5))
    on = _client(settings, per_minute=1)
    assert all(on.get("/health").status_code == 200 for _ in range(5))
