"""Compatibility entry point; existing launch commands now use Datadog."""

from app import datadog_main

app = datadog_main.app
