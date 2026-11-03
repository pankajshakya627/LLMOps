"""Datadog serving entry point: python -m uvicorn app.datadog_main:app."""

from app.core.config import get_settings
from app.core.telemetry import configure_telemetry

configure_telemetry(get_settings())

# Instrument frameworks before importing the application and its routers.
from app import main

app = main.app
