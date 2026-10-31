# Phoenix-only observability migration — 25 October 2026

What this change does: Removes the Datadog SDK, configuration, workflow/feedback
publication, response fields and startup wrapper. Phoenix/OpenInference captures
traces and prompt versions; Ragas retains evaluation scoring and quality gates.

## Scope and review

Reviewed the connected answer, evaluation, feedback, storage, UI and serving
paths. Assumed local enterprise training with one API worker. Existing limits
and counters remain per process; this is not a fleet-wide rate-limit design.
The workspace has no Git metadata. Review used a saved pre-change source snapshot,
not a commit diff.

Looks good. Ship. No unresolved must-fix findings in the reviewed change.

## Changes

- Removed `ddtrace` and its exclusive dependencies from the project lockfile and
  synchronized application environment. Phoenix client/instrumentation versions
  are now pinned application dependencies. Removed the old tracing-only PyMongo
  upper bound without forcing an unrelated database-driver upgrade.
- Removed the retired telemetry bootstrap module, Agent compose file and setup
  guide. Docker now serves `app.phoenix_main:app` directly through uvicorn.
- Removed retired telemetry settings from `.env.example` and private `.env`.
  Preserved model, judge, database and fallback settings; no secrets are copied
  into this report or receipts.
- [Response correlation](../../../app/core/phoenix.py) uses the active HTTP server
  trace/span. Answer bodies expose `phoenix_trace_id` / `phoenix_span_id`; headers
  expose the matching `x-phoenix-*` values. JSON logs carry the active IDs.
- [Prompt context](../../../app/core/observability.py) uses native OpenInference
  attributes. Versions and templates remain separate from runtime values;
  concurrent calls and exceptions restore their previous context. The actual
  instrumentor tests verify version propagation and privacy masking.
- Removed vendor-specific fields from answer/evaluation contracts and batch
  reports. The UI displays the returned Phoenix trace ID. Saved feedback stays
  in MongoDB and is no longer submitted to an external feedback SDK.
- [Stored feedback compatibility](../../../app/database/feedback.py) projects
  persisted response snapshots onto the current fields. Existing records remain
  readable without a database rewrite. New HTTP inputs still reject unknown
  fields, and feedback review/export authorization remains intact.
- Updated current setup, teaching, component and architecture code links. Kept
  prior measured reports and binary slide artifacts as historical evidence.
  Remaining retired-provider strings in tests are absence assertions or an old
  stored-record fixture, not a runnable integration.

## Verification

| Check | Result |
|---|---|
| Complete offline run | 349 passed: 320 application/training + 22 mock API + 7 explicit SDK checks |
| Failures / errors / skips | 0 / 0 / 0 |
| Final training, Phoenix, telemetry, contract and document checks | 37 passed after the final edits |
| Ruff | Passed across app, tests and training |
| Mypy | Passed: 99 application/training source files |
| Lockfile | `uv lock --check --offline` passed |
| Installed SDK | Retired SDK absent from the application environment |
| Commands and links | Current shell examples parse; course/document and architecture-path tests pass |

Receipts: [pytest.xml](pytest.xml), [SUMMARY.json](SUMMARY.json) and
[changed-files.json](changed-files.json). The pre-change absence/contract checks
failed before implementation and passed afterward. Vendor-specific submission
checks were replaced or retired with their removed functionality; validation,
quality thresholds and unrelated tests were not weakened.

SDK checks use real FastAPI/LangChain/OpenInference instrumentors with an
in-memory exporter, controlled provider HTTP and a mocked Phoenix annotation
endpoint. They verify server/model trace identity, tokens, prompt version,
privacy masking, four metric statuses and annotation serialization without
contacting model providers, Atlas or a live collector.

## Migration notes and limits

Run `uv sync --locked --extra ui --extra evaluation`, then restart the API/UI.
Use `app.phoenix_main:app` for traced serving; `app.main.create_app()` remains an
uninstrumented factory for offline use. The current [README](../../../README.md)
and [Phoenix walkthrough](../../../training/session2/phoenix.md) contain commands.

Strict API consumers must adopt the current response fields. Old saved evaluated
JSON files containing removed fields do not match the new schema: capture a fresh
response/header pair before running `app.evaluation.phoenix_export`.

Ragas scores from `/answer/evaluated` are published through the existing explicit
Phoenix exporter. Trace collection does not compute scores, native online
evaluators are not auto-created, and registry prompt versions do not deploy the
local serving template. Batch reports remain local; sampled scores feed process
metrics/logs. MongoDB feedback is not automatically posted as Phoenix annotations.

Earlier live results remain in the
[preceding report](../closing-validation-gaps-20261025/REPORT.md). Model quality
was not changed or re-certified by this migration: pure Ollama and two measured
semantic targets still need improvement. No evaluation thresholds were lowered.

Not checked: fresh live provider/Atlas behavior, live collector receipt, real
browser flows, Docker image build, production load or penetration testing.
