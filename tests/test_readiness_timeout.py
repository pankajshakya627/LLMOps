from __future__ import annotations

from unittest.mock import MagicMock, Mock

import pytest
from pymongo.errors import NetworkTimeout

from app.core.config import Settings
from app.database import mongo


def test_readiness_uses_a_driver_deadline_and_propagates_failure(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    deadline = MagicMock()
    monkeypatch.setattr(mongo, "timeout", deadline, raising=False)
    database = Mock()
    database.command.side_effect = NetworkTimeout("unavailable")
    monkeypatch.setattr(mongo, "_database", lambda _: database)
    with pytest.raises(NetworkTimeout):
        mongo.ping_database(settings)
    deadline.assert_called_once_with(2)
