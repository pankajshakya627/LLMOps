from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.database.postgres import compile_filter, vector_literal


def test_pgvector_settings_do_not_require_atlas() -> None:
    configured = Settings(
        _env_file=None,
        storage_backend="pgvector",
        postgres_dsn="postgresql://unused/db",
        institution="NexaBank",
        jurisdiction="IN",
        confidentiality_level="internal",
    )
    assert configured.storage_backend == "pgvector"
    assert configured.mongodb_uri is None


def test_pgvector_requires_explicit_dsn(settings: Settings) -> None:
    with pytest.raises(ValidationError, match="POSTGRES_DSN"):
        Settings.model_validate({**settings.model_dump(), "storage_backend": "pgvector"})


def test_filter_preserves_scope_and_binds_values() -> None:
    sql, values = compile_filter(
        {
            "$and": [
                {"institution": "Other' OR true --"},
                {"effective_date": {"$lte": "2026-10-01"}},
                {"effective_to_search": {"$gte": "2026-10-01"}},
                {"product_id": "NEXA-HL"},
            ]
        }
    )
    assert "Other' OR true --" not in sql
    assert "AND" in sql
    assert any(getattr(value, "obj", None) == "Other' OR true --" for value in values)
    assert values.count("2026-10-01") == 2


def test_unknown_filter_operators_fail_closed() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        compile_filter({"institution": {"$where": "true"}})


@pytest.mark.parametrize("vector", [[0.0, 0.0], [1.0], [float("nan"), 1.0], [True, 1.0]])
def test_vector_rejects_zero_wrong_dimension_and_nonfinite(vector: list[float]) -> None:
    with pytest.raises(ValueError):
        vector_literal(vector, 2)
