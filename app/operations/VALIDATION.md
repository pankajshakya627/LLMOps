# Application verification

For the subsequent Atlas-free storage change, see
[PostgreSQL / pgvector verification](PGVECTOR_VALIDATION.md). The results below
record the earlier runtime consolidation.

Runtime consolidation preserves service entry points, the existing Phoenix
project identifier, strict schemas, validation behavior and bounded routing.
Golden cases and quality gates are moved without changing their bytes.

## Verification recorded on 2026-10-25

| Check | Result |
|---|---|
| Application, course, Phoenix/Ragas adapter and mock API tests | 377 passed; 0 failures, errors or skips |
| Ruff (`app tests training`) | Passed |
| Mypy (`app training`) | Passed; 102 source files |
| Golden cases and gate configuration | SHA-256 hashes unchanged from before the move |
| Package dependencies | `pyproject.toml` and `uv.lock` unchanged |
| Operational Markdown links and shell examples | Local targets resolve; Bash syntax passes |
| Docker Compose configuration | Valid |
| API/UI image | Built as `nexaassist-runtime-layout:20261025` |
| Image resource check with networking disabled | Loads 10 answer cases and the gates from `app/`; no `training/` or root `evaluation/` directory present |

The [JUnit receipt](runtime-consolidation-tests.xml) records the test results.
Run the combined suite from the repository root:

```bash
RAGAS_DO_NOT_TRACK=true uv run --no-sync --with openapi-spec-validator \
  python -m pytest -q tests \
  tests/runtime/phoenix_profile_check.py tests/runtime/ragas_adapters_check.py \
  nexa_synthetic_data/api/mock_server/test_mock_api.py \
  --tb=short --junitxml=app/operations/runtime-consolidation-tests.xml
uv run --no-sync ruff check app tests training
uv run --no-sync mypy app training
```

Legacy root fixture paths are symbolic links to the canonical files in
`app/evaluation/`. They preserve callers that cached the old paths; the runtime
image does not require those links. The synthetic corpus remains an explicit,
external ingestion input.

## Limits

No live model or Atlas requests were made for this migration. Existing services
were not restarted and indexes were not changed. These checks do not establish
generated-answer quality, production load capacity or security certification.
Quality gates retain their existing `placeholder` status.

This checkout has no Git metadata or configured remote, so no commit, push or
pull request was created.
