from __future__ import annotations

from typing import Annotated

import httpx
import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from langchain_core.exceptions import OutputParserException
from langchain_openai.chat_models.base import OpenAIRefusalError
from openai import OpenAIError
from pymongo.errors import PyMongoError

from app.api.limits import limit_requests
from app.core.config import Settings, get_settings
from app.core.phoenix import record_result
from app.evaluation.phoenix_export import publish_annotations_safely
from app.models.answer import AnswerResponse
from app.models.evaluation import EvaluatedAnswerRequest, EvaluatedAnswerResponse
from app.models.retrieval import RetrieveRequest
from app.services.answer import answer_policy
from app.services.evaluation import answer_with_quality, score_sampled_answer, should_sample

router = APIRouter(dependencies=[Depends(limit_requests("answer"))])
logger = structlog.get_logger()


@router.post("/answer/evaluated")
async def evaluated_answer(
    request: EvaluatedAnswerRequest,
    background: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
) -> EvaluatedAnswerResponse:
    try:
        response = await answer_with_quality(request, settings)
        record_result(response, capture_content=settings.phoenix_capture_content)
        if response.answer.phoenix_span_id:
            background.add_task(
                publish_annotations_safely, response, response.answer.phoenix_span_id, settings
            )
        return response
    except (
        OpenAIError,
        OpenAIRefusalError,
        PyMongoError,
        ValueError,
        TimeoutError,
        OutputParserException,
        httpx.HTTPError,
    ) as exc:
        logger.error("evaluated_answer_failed", error_type=type(exc).__name__)
        raise HTTPException(status_code=503, detail="Answer service unavailable") from None


@router.post("/answer")
async def answer(
    request: RetrieveRequest,
    background: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AnswerResponse:
    try:
        response = await answer_policy(request, settings)
        record_result(response, capture_content=settings.phoenix_capture_content)
        if should_sample(response, settings):
            background.add_task(score_sampled_answer, request, response, settings)
        return response
    except (
        OpenAIError,
        OpenAIRefusalError,
        PyMongoError,
        ValueError,
        TimeoutError,
        OutputParserException,
        httpx.HTTPError,
    ) as exc:
        logger.error("answer_failed", error_type=type(exc).__name__)
        raise HTTPException(status_code=503, detail="Answer service unavailable") from None
