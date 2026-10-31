# App gateway and security delivery — 25 October 2026

The application now owns its LiteLLM gateway profiles and Guardrails AI service.
Docker Compose connects FastAPI, Streamlit, gateway, validator and Phoenix.
Ollama stays native on the host; Atlas remains external. Phoenix/Ragas remain
the observability/evaluation stack.

## Implementation

- [app/gateway](../../../app/gateway/) owns standard, cache and balanced routing,
  native application/model profiles, isolated requirements, Dockerfile and a real
  SDK self-check. Chat can fall back to the approved OpenAI route. Both local
  Qwen and OpenAI embedding aliases exist in every gateway configuration.
- Cloud routes pin the official OpenAI endpoint explicitly. Gateway profiles
  disable the separate application cloud fallback to avoid stacked routing.
  Local chat and embedding URLs are independent, allowing a chat outage drill
  while retrieval remains available. No embedding-family fallback is configured.
- Cache is opt-in, exact, five-minute, chat-only and single-worker memory. The
  existing client hashes credential, access/corpus/model/prompt scope into the
  namespace. Cached drafts retain application validation. Mixed model costs
  remain unmeasured rather than priced using one candidate's rate.
- [app/security/input_policy.py](../../../app/security/input_policy.py) adds
  explicit override/prompt-extraction checks before provider calls, including
  normalization of tested Unicode variants. `/retrieve`, `/answer` and
  `/answer/evaluated` return sanitized HTTP 400 for these requests. PII redaction
  settings cannot disable this check. Streamlit explains the rejection.
- Existing PII output checks, strict schemas, exact citations, bounded repair
  and fail-closed validator behavior remain active. The Guardrails service now
  lives under `app/security`, with its own Python 3.13 container and liveness
  probe. The old training Python entry point is a thin compatibility import.
- [app/compose.yaml](../../../app/compose.yaml) binds host ports to localhost,
  connects service names internally, waits for gateway/validator health, and
  keeps private configuration out of the UI/validator environment. Docker build
  context excludes `.env`, environments, caches and recorded results.
- The full gateway profile uses new collections/index names, preserving the
  existing direct-Qwen/OpenAI stores. The chat-only overlay remains available for
  an existing direct-Ollama corpus. An OpenAI embedding profile selects separate
  1536-dimensional collections/indexes for ingestion and serving.
- Added [HTTP examples](../../../app/examples/), [gateway guide](../../../app/gateway/README.md),
  [security guide](../../../app/security/README.md), index mappings and complete
  Docker/native commands in [README.md](../../../README.md).

## Verification

| Check | Result |
|---|---|
| Complete application/training, explicit SDK and mock API suite | **372 passed**, zero failures/errors/skips |
| Ruff | Passed across app, tests and training |
| Mypy | Passed: 102 source files |
| Lockfile | Existing application lock unchanged; offline lock check passed |
| Constraint contract | Unchanged |
| Real LiteLLM SDK | Fixture balancing across two deployments, bounded fallback, cache isolation and auth-error classification passed |
| Real Guardrails AI SDK | Five synthetic schema cases passed without model calls |
| Native proxy startup/auth | Health 200; missing key 401; invalid key rejected with 400; valid master key 200; all four aliases registered |
| Compose | Standard, cache, balanced and OpenAI-embedding variants validate without printing resolved secrets |
| Phoenix image | Pinned tag exists; manifest includes amd64/arm64 |
| Guides | Local links, shell syntax, moved code links and example payload checks passed |

Receipts: [pytest.xml](pytest.xml), [SUMMARY.json](SUMMARY.json),
[service-smoke.json](service-smoke.json) and [changed-files.json](changed-files.json).
New service-wiring tests first failed on the absent app-owned files. Twelve
adversarial HTTP cases failed before the input policy was added and then passed;
normal security/policy questions remained usable. Existing tests were preserved,
with moved-path assertions updated. No quality thresholds were lowered.

The native proxy smoke check caught an actual missing dependency: LiteLLM's auth
error handler imports Prisma even without a database configured. Missing auth
therefore produced HTTP 500. Pinning `prisma==0.15.0` in the isolated gateway
requirements restored HTTP 401. The SDK self-check now exercises that error
classification. The temporary synthetic gateway was stopped after verification. No unrelated
services were stopped. No Postgres service or gateway virtual-key database was added;
this classroom stack uses the private master key.

A private gateway key was generated locally if absent; the configured cloud
model was derived from the existing approved settings. Secrets were not printed
or copied into reports. No corpus ingestion, index mutation, live model/Atlas
call or new semantic quality evaluation was performed by this delivery.

## Review and limits

Reviewed callers, models, profiles, retries, cache scope, input/output checks,
UI behavior and container credential/endpoint wiring. Expected load is a local
classroom with one API/gateway worker. Process-local rate limits/cache/metrics are
not a multi-tenant production design. No unresolved blocking finding in this scope.

Direct gateway endpoints are administrative/protocol access and bypass FastAPI's
input/output rails. Keep their key private and send policy requests to FastAPI.
Injection rules cover explicit English patterns, not all semantic attacks. Schema
and quote validation do not prove truth. Existing live model quality limitations
remain in the [earlier report](../closing-validation-gaps-20261025/REPORT.md).

The Docker daemon is unavailable in this environment. Images were not built and
the complete Compose stack was not started. Native SDK and proxy checks do not
establish Docker build success, live Qwen/OpenAI fallback quality, physical
replica capacity, production load, penetration resistance or new browser results.
