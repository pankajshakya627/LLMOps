"""Phoenix serving entry point: python -m uvicorn app.phoenix_main:app."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from openinference.instrumentation import TraceConfig, TracerProvider
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from phoenix.otel import HTTPSpanExporter

from app.core.config import get_settings
from app.core.http_monitoring import CAPTURE_LIMIT, safe_content
from app.core.phoenix import PrivateSpanExporter, capture_request, correlate_response
from app.main import create_app as create_base_app


class PrivateTraceConfig(TraceConfig):
    def mask(self, key: str, value: Any, *, externalize: bool = True) -> Any:
        # OpenInference's input masking leaves template variables and metadata visible.
        if self.hide_inputs and key in {"llm.prompt_template.variables", "metadata"}:
            return None
        value = super().mask(key, value, externalize=externalize)
        if isinstance(value, str):
            if len(value.encode("utf-8")) > CAPTURE_LIMIT:
                return "[OMITTED: exceeds 64 KiB]"
            try:
                parsed = json.loads(value)
                if isinstance(parsed, (dict, list)):
                    return json.dumps(safe_content(parsed), ensure_ascii=False)
            except ValueError, RecursionError:
                pass
            return safe_content(value)
        return value


def create_app() -> FastAPI:
    settings = get_settings()
    capture = settings.phoenix_capture_content
    masking = PrivateTraceConfig(
        hide_inputs=not capture,
        hide_outputs=not capture,
        hide_input_messages=not capture,
        hide_output_messages=not capture,
        hide_retrieval_documents=not capture,
        hide_embeddings_text=not capture,
        hide_embedding_vectors=True,
        hide_llm_invocation_parameters=True,
    )
    provider = TracerProvider(
        config=masking,
        resource=Resource.create({"openinference.project.name": settings.phoenix_project_name}),
    )
    headers = (
        {"authorization": f"Bearer {settings.phoenix_api_key.get_secret_value()}"}
        if settings.phoenix_api_key
        else None
    )
    provider.add_span_processor(
        BatchSpanProcessor(
            PrivateSpanExporter(
                HTTPSpanExporter(
                    endpoint=f"{settings.phoenix_base_url}/v1/traces",
                    headers=headers,
                )
            )
        )
    )
    LangChainInstrumentor().instrument(tracer_provider=provider, config=masking)
    application = create_base_app()
    application.state.phoenix_capture_content = capture
    base_lifespan = application.router.lifespan_context

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            async with base_lifespan(app):
                yield
        finally:
            await asyncio.to_thread(provider.shutdown)

    application.router.lifespan_context = lifespan
    FastAPIInstrumentor.instrument_app(
        application,
        tracer_provider=provider,
        server_request_hook=capture_request,
        client_response_hook=correlate_response,
        excluded_urls="",
        http_capture_headers_server_request=[],
        http_capture_headers_server_response=[],
    )
    return application


app = create_app()
