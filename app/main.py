from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.answer import router as answer_router
from app.api.feedback import router as feedback_router
from app.api.operations import router as operations_router
from app.api.retrieval import router as retrieval_router
from app.chains.context import token_encoder
from app.core.config import get_settings
from app.core.http_monitoring import HTTPMonitoringMiddleware
from app.core.logging import configure_logging
from app.security.input_policy import UnsafeQueryError


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    await asyncio.to_thread(token_encoder, settings.token_encoding)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="NexaAssist", lifespan=lifespan)
    app.state.http_metrics = {}
    app.add_middleware(HTTPMonitoringMiddleware, metrics=app.state.http_metrics)

    @app.exception_handler(UnsafeQueryError)
    async def unsafe_query(_request: Request, _exc: UnsafeQueryError) -> JSONResponse:
        return JSONResponse(
            status_code=400, content={"detail": "Query blocked by security policy."}
        )

    app.include_router(operations_router)
    app.include_router(retrieval_router)
    app.include_router(answer_router)
    app.include_router(feedback_router)
    return app


app = create_app()
