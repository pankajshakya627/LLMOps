# Phoenix profile verification — 24 October 2026

Historical verification record. The current application uses Phoenix/OpenInference
and Ragas only; use [phoenix.md](../../app/observability/README.md) for current startup and contracts.

## Implemented

- Optional FastAPI entry point `app.phoenix_main:app` instruments the existing
  application with Phoenix/OpenInference. The default Datadog application entry
  point is unchanged. The optional SDKs use an isolated uv overlay.
- HTTP response headers identify the root HTTP server trace/span. Child send
  spans do not replace the correlation identity.
- `app.evaluation.phoenix_export` validates a saved `/answer/evaluated` response
  and its saved correlation header, then synchronously posts four annotations
  using the actual Phoenix client. It preserves unavailable/error labels without
  numeric scores, and preserves a measured zero as a score.
- Default content masking includes prompt-template variables and metadata:
  In the tested SDK combination, input masking did not hide the synthetic marker in
  `llm.prompt_template.variables` by itself. Explicit synthetic-content capture
  remains an instructor-controlled setting.

## Checks

| Check | Result |
|---|---|
| Full offline suite | **265 passed**, 36.34 seconds |
| Phoenix-specific tests | **9 passed**, covering correlation, invalid contexts/IDs, metric statuses, transport URL and cleanup |
| Ruff | Passed |
| Base-environment mypy | Passed: 137 source files |
| Optional-SDK mypy on serving/export modules | Passed with the actual optional SDK types installed |
| Real FastAPI/LangChain SDK fixture | HTTP statuses 200/422/200; 14 captured spans; real model span reports 11 fixture tokens; 4 annotations sent to a mocked Phoenix API |
| Default content masking | Synthetic input/output markers absent from exported span attributes |
| Guide checks | Local file links, shell syntax and request model validation passed |
| Protected files | `CONSTRAINTS.md`, `pyproject.toml` and `uv.lock` unchanged |

The SDK fixture uses an in-memory span exporter, HTTP mock model and HTTP mock
annotation endpoint. No live model, Atlas, Datadog or Phoenix collector was
contacted. It proves framework behavior and request/annotation construction,
not live service receipt, answer quality, index readiness or UI appearance.
The SDK-typed annotation construction was refined after the full-suite run;
the focused Phoenix tests and both type-checking environments were rerun.

The guide documents that process metrics, gateway internals and the separate
Guardrails service are not automatically additional Phoenix spans or quality
annotations. The export command handles the live endpoint response format,
not batch evaluation reports.

Pinned optional SDKs and runnable commands are in [phoenix.md](../../app/observability/README.md) and
[requirements-phoenix.txt](../../app/observability/requirements-client.txt).
