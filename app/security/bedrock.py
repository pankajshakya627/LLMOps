"""Optional, fail-closed Bedrock checks; local deployments do not import the AWS SDK."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

from app.core.config import Settings


@lru_cache
def runtime_client(region: str) -> Any:
    import boto3
    from botocore.config import Config

    return boto3.client(
        "bedrock-runtime",
        region_name=region,
        config=Config(connect_timeout=3, read_timeout=10, retries={"total_max_attempts": 2}),
    )


def check_content(text: str, source: Literal["INPUT", "OUTPUT"], settings: Settings) -> None:
    if settings.bedrock_guardrail_id is None:
        return
    try:
        result = runtime_client(str(settings.bedrock_region)).apply_guardrail(
            guardrailIdentifier=settings.bedrock_guardrail_id,
            guardrailVersion=settings.bedrock_guardrail_version,
            source=source,
            content=[{"text": {"text": text}}],
        )
        if result.get("action") != "NONE":
            raise ValueError("Bedrock guardrail rejected content")
    except Exception:  # noqa: BLE001 - SDK/import/response failures must all fail closed.
        # Keep provider diagnostics and potentially echoed content out of application logs.
        raise ValueError("Bedrock content check failed") from None
