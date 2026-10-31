# Development tooling guide

Use the project's existing layers and [constraints](CONSTRAINTS.md).
[APP_COMPONENT_GUIDE.md](APP_COMPONENT_GUIDE.md) maps modules and boundaries;
[README.md](README.md) contains current execution commands.

## Environment

The application uses Python 3.14+, `uv`, FastAPI, Streamlit, MongoDB Atlas,
Phoenix/OpenInference and Ragas. Keep the Phoenix collector and Guardrails
service in their documented separate Python 3.13 environments.

```bash
uv sync --locked --extra ui --extra evaluation
```

Private `.env` credentials stay outside version control and projected screens.
Configure model endpoints explicitly. Do not redirect OpenAI credentials to a
custom endpoint or mix incompatible query/corpus embedding profiles.

## Checks

```bash
RAGAS_DO_NOT_TRACK=true uv run --locked --no-sync python -m pytest -q tests
uv run --locked --no-sync ruff check app tests training
uv run --locked --no-sync mypy app training
```

Offline tests use controlled providers, local storage and in-memory trace
exporters. They must not contact model services, Atlas or a collector. Tests in
`tests/runtime/` can be run explicitly as shown in [README.md](README.md#testing).
Required behavior and quality thresholds must not be weakened to clear a check.

## Runtime debugging

Start `app.phoenix_main:app` for instrumented serving. Correlate the response's
Phoenix trace/span IDs with server spans and structured JSON logs. Inspect
prompt/model provenance, reported token usage and operation timings.

Ragas computes scores; tracing alone does not. Export a saved evaluated response
with `python -m app.evaluation.phoenix_export` to attach its scores/statuses to
the exact request span. Use [the Phoenix walkthrough](app/observability/README.md)
for startup, privacy settings, publication and troubleshooting.

`app.main.create_app()` exposes the same business routes without registering an
exporter, for offline use. No other observability SDK is configured.

## Change review

Trace callers, schemas, configuration, storage, UI and tests when changing an
interface. Keep the strict API boundary and the existing fail-closed validators.
Preserve stored feedback and explicit metric error/unavailable states. Review
model quality separately from functional test success.

The current workspace has no Git metadata. Commit hooks and commit-history
analysis require an actual Git checkout; do not initialize one merely to run a
review. Source-based comparisons and saved verification receipts remain usable.
