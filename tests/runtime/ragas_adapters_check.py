"""Explicit optional-evaluation check: pytest tests/runtime/ragas_adapters_check.py."""

from __future__ import annotations

import asyncio
from unittest.mock import Mock

import pytest
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, ValidationError

from app.evaluation.ragas_metrics import MetricEmbeddings, StructuredJudge


class Verdict(BaseModel):
    supported: bool


@pytest.mark.parametrize("asynchronous", [False, True])
def test_structured_judge_validates_the_actual_adapter_result(asynchronous: bool) -> None:
    model = Mock(spec=BaseChatModel)
    model.with_structured_output.return_value = RunnableLambda(lambda _: {"supported": True})
    judge = StructuredJudge(model)
    result = (
        asyncio.run(judge.agenerate("Question", Verdict))
        if asynchronous
        else judge.generate("Question", Verdict)
    )
    assert result.supported is True
    model.with_structured_output.assert_called_with(Verdict, method="json_schema", strict=True)


def test_judge_rejects_a_malformed_result_instead_of_scoring_it() -> None:
    model = Mock(spec=BaseChatModel)
    model.with_structured_output.return_value = RunnableLambda(lambda _: {"unknown": True})
    with pytest.raises(ValidationError):
        StructuredJudge(model).generate("Question", Verdict)


def test_metric_embeddings_preserve_sync_and_async_vectors() -> None:
    model = Mock(spec=Embeddings)
    model.embed_query.return_value = [0.1, 0.2]

    async def embed(text: str) -> list[float]:
        assert text == "Policy"
        return [0.3, 0.4]

    model.aembed_query = embed
    adapter = MetricEmbeddings(model)
    assert adapter.embed_text("Policy") == [0.1, 0.2]
    assert asyncio.run(adapter.aembed_text("Policy")) == [0.3, 0.4]
