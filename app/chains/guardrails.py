from __future__ import annotations

import asyncio

import httpx

from app.core.config import Settings
from app.models.answer import AnswerDraft, GuardrailRequest, GuardrailResult
from app.security.bedrock import check_content


async def validate_draft(draft: AnswerDraft, settings: Settings) -> None:
    """Use the configured Guardrails AI process; outages never bypass validation."""
    await asyncio.to_thread(check_content, draft.model_dump_json(), "OUTPUT", settings)
    if settings.guardrails_base_url is None:
        return
    payload = GuardrailRequest(llm_output=draft.model_dump_json())
    async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
        response = await client.post(
            f"{settings.guardrails_base_url}/validate", json=payload.model_dump()
        )
        response.raise_for_status()
    decision = GuardrailResult.model_validate(response.json())
    if not decision.validation_passed:
        raise ValueError("Guardrails AI rejected the generated output")
