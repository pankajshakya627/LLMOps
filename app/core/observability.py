from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from math import ceil
from typing import Any

import structlog
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.messages import AIMessage
from langchain_core.outputs import LLMResult
from langchain_core.prompts import ChatPromptTemplate
from openinference.instrumentation import using_attributes

retrieval_latencies: deque[float] = deque(maxlen=1000)
answer_latencies: deque[float] = deque(maxlen=1000)
answer_metrics: Counter[str] = Counter()
# 1 - faithfulness of recently sampled live answers; feeds the rollback trigger.
sampled_hallucination: deque[float] = deque(maxlen=200)
_answer_usage: ContextVar[Counter[str] | None] = ContextVar("answer_usage", default=None)


@contextmanager
def track_answer_usage() -> Iterator[Counter[str]]:
    """Collect model tokens for one answer request; judge and RAGAS calls fall outside it."""
    usage: Counter[str] = Counter()
    token = _answer_usage.set(usage)
    try:
        yield usage
    finally:
        _answer_usage.reset(token)


def prompt_annotation_context(
    prompt: ChatPromptTemplate,
    variables: dict[str, str],
    *,
    prompt_id: str,
    version: str,
) -> using_attributes:
    """Attach the source prompt version to scoped OpenInference model spans."""
    return using_attributes(
        prompt_template=prompt.pretty_repr(),
        prompt_template_version=version,
        prompt_template_variables=variables,
        metadata={"prompt_id": prompt_id},
    )


def latency_summary(samples: Iterable[float] | None = None) -> dict[str, int | float]:
    values = sorted(retrieval_latencies if samples is None else samples)
    result: dict[str, int | float] = {"sample_count": len(values)}
    for label, fraction in (("p50_ms", 0.5), ("p95_ms", 0.95), ("p99_ms", 0.99)):
        result[label] = values[max(0, ceil(fraction * len(values)) - 1)] if values else 0
    return result


class TokenUsageLogger(AsyncCallbackHandler):
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        for generations in response.generations:
            for generation in generations:
                message = getattr(generation, "message", None)
                if isinstance(message, AIMessage) and message.usage_metadata:
                    structlog.get_logger().info(
                        "model_token_usage",
                        observed_model=message.response_metadata.get("model_name"),
                        **message.usage_metadata,
                    )
                    usage = _answer_usage.get()
                    if usage is not None:
                        usage["input_tokens"] += message.usage_metadata["input_tokens"]
                        usage["output_tokens"] += message.usage_metadata["output_tokens"]
