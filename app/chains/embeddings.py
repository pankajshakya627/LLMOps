from __future__ import annotations

from math import isfinite
from typing import Any

from langchain_openai import OpenAIEmbeddings
from pydantic import Field

from app.core.config import OPENAI_BASE_URL, Settings


class CheckedEmbeddings(OpenAIEmbeddings):
    expected_dimensions: int = Field(gt=0)

    def _validate_vectors(self, vectors: list[list[float]], count: int) -> list[list[float]]:
        if len(vectors) != count or any(
            len(vector) != self.expected_dimensions
            or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                for value in vector
            )
            for vector in vectors
        ):
            raise ValueError("Invalid embedding count, dimensions or non-finite values")
        return vectors

    def embed_documents(
        self, texts: list[str], chunk_size: int | None = None, **kwargs: Any
    ) -> list[list[float]]:
        return self._validate_vectors(
            super().embed_documents(texts, chunk_size=chunk_size, **kwargs), len(texts)
        )

    async def aembed_documents(
        self, texts: list[str], chunk_size: int | None = None, **kwargs: Any
    ) -> list[list[float]]:
        return self._validate_vectors(
            await super().aembed_documents(texts, chunk_size=chunk_size, **kwargs), len(texts)
        )


def get_embeddings(settings: Settings) -> OpenAIEmbeddings:
    """Ingestion and retrieval must share this model and dimension."""
    key = settings.provider_key(settings.embedding_base_url, settings.embedding_api_key)
    official = settings.embedding_base_url == OPENAI_BASE_URL
    if not official and not settings.embedding_profile:
        raise ValueError("Custom embedding endpoint requires EMBEDDING_PROFILE")
    return CheckedEmbeddings(
        model=settings.embedding_model,
        openai_api_base=settings.embedding_base_url,
        dimensions=settings.embedding_dimensions if official else None,
        expected_dimensions=settings.embedding_dimensions,
        chunk_size=settings.embedding_batch_size,
        openai_api_key=key,
        check_embedding_ctx_length=official,
    )
