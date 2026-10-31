# Docker startup fixes — 25 October 2026

The built Guardrails image failed with `PermissionError` reading
`/opt/nexaassist/app/__init__.py`. Host source files/directories had modes
0600/0700; plain Docker COPY preserved them while the service ran as UID 10001.
The Dockerfile now normalizes read/traverse permissions during COPY and retains
the non-root user. The regression test failed before this change and passed after.

Two independent conflicts also prevented startup:

- Concurrent Compose recreations produced a temporary replacement-name conflict.
  After the first operation finished, the regular Guardrails container was healthy.
  No container removal was needed to clear the transient conflict.
- An older proxy already owned port 4000, and a native Python API owned 8000.
  `GATEWAY_PORT` and `API_PORT` now allow safe host overrides; the private `.env`
  selects 4001 and 8001. `UI_PORT` is also configurable, retaining default 8501.
  Internal service URLs and ports remain unchanged.

The old proxy and Postgres containers share the Compose project name and produce
an orphan warning. They were preserved, as were all volumes and the native API.
Do not use `--remove-orphans` unless intentionally retiring those older services.
Run one Compose operation at a time.

## Actual Docker verification

The images were built and the application services started. Gateway, validator,
API and UI reported healthy; Phoenix was running with a reachable UI.
[smoke.json](smoke.json) records:

- API health/docs, UI health, Phoenix UI and validator health returned HTTP 200.
- Gateway master-key authentication returned HTTP 200 and all four model aliases.
- Real Guardrails accepted a schema-valid abstention and rejected an invalid status.
- API invalid input returned 422; explicit prompt injection returned 400 with
  Phoenix trace/span correlation headers.
- The real Guardrails self-check also ran inside the container; non-root UID
  10001 could read/traverse the copied application files.

The handout integrity test was updated to recognize real `app.*` command modules
as well as training modules. It still requires referenced module files to exist;
no test was skipped and no quality target was lowered.

Full offline verification: **373 passed**, zero failures/errors/skips; Ruff and
mypy passed (102 source files). Results are in [pytest.xml](pytest.xml). No live model, Ragas score,
Atlas query or ingestion was performed during these startup checks. Health and
schema checks do not establish live answer quality or database/index readiness.

Current local URLs:

- FastAPI: http://127.0.0.1:8001/docs
- Streamlit: http://127.0.0.1:8501
- Phoenix: http://127.0.0.1:6006
- Validator: http://127.0.0.1:8101/docs
- Application gateway: http://127.0.0.1:4001 (private key required)
