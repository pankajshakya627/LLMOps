# Datadog observability and evaluation

Datadog replaces the Phoenix runtime. Ragas still computes scores, and existing
answer endpoints, release gates and offline labs retain their behavior. Historical
Phoenix reports and volumes are retained; history is not imported automatically.

## AWS monitoring path

The AWS runtime no longer runs a Datadog Agent container. Its signals use:

| Signal | Delivery |
|---|---|
| AWS infrastructure metrics | Datadog AWS integration / CloudWatch |
| Application logs | Session CloudWatch log group → session-owned Datadog Forwarder Lambda |
| HTTP, model and chain traces | `ddtrace` agentless LLM Observability |
| Route, answer and retrieval metrics | Datadog `ThreadStats` HTTP exporter |
| Ragas scores | Datadog v2 evaluation intake, joined to the answer workflow |

Use [Start → inspect → Destroy → Start](../../infra/aws/START_USE_DELETE_GUIDE.md)
in the existing GitHub AWS workflow. Every new lab owns `/nexaassist/STACK_NAME`,
its Forwarder Lambda, log subscription and collector role. It verifies the pinned
official ARM64 ZIP and stores an immutable version in the session artifact bucket;
there is no shared-layer, copier or separate collector stack to clean up.

Destroy and automatic expiry remove those resources together with the application.
Reusable account integration, API-key secrets and Datadog history are retained, as
selected for this setup. The workflow summary links directly to the app and Datadog.
Every creation has a unique `lab_session_id` tag, including same-name recreations;
API/gateway traces, custom metrics, logs and tagged AWS resources carry it.

The application retains its serving containers. Monitoring needs no Docker Agent
or local telemetry UI. Installing the account integration alone does not subscribe
application logs or instrument Python.

Keep credentials in the private root `.env`:

```dotenv
DD_API_KEY=your-private-api-key
DD_LLMOBS_ML_APP=nexaassist
DD_SITE=datadoghq.com
DD_ENV=dev
DD_LLMOBS_ENABLED=true
DD_LLMOBS_AGENTLESS_ENABLED=true
DD_TRACE_ENABLED=false
DD_METRICS_ENABLED=true
DD_CAPTURE_CONTENT=false
```

`DD_LLMOBS_ML_APP` is an application name, not an application key. Trace, metric and
evaluation intake use the API key. It validated successfully for `datadoghq.com`
during this migration. `DD_CAPTURE_CONTENT` replaces `PHOENIX_CAPTURE_CONTENT`;
the private file's explicit preference was preserved. Enable capture only for
approved synthetic data. Supported personal identifiers and common credential
fields are masked; the matcher is not a comprehensive sensitive-data detector.

## Historical AWS integration repair

The existing `DatadogIntegration` stack in `ap-south-1` failed on 3 November 2026.
The nested Forwarder failed because AWS denied `lambda:GetLayerVersion` for
Datadog's publisher-owned `Datadog-Forwarder:117` layer, with no resource policy
allowing access. Broadening the application's IAM permissions cannot supply the
publisher's missing resource policy.

The [prepared repair template](../../infra/aws/datadog-forwarder.yaml) uses Datadog's
official Forwarder template with `InstallAsLayer=false`. This selects the supported
ZIP installation and avoids that shared-layer dependency. It creates a Lambda,
its IAM role, storage and a private API-key secret when one is not supplied.

1. Let the failed integration stack finish rolling back. Retry the Datadog AWS
   integration from its Datadog tile with automatic Forwarder installation disabled,
   so infrastructure monitoring does not depend on the failing shared layer.
2. Deploy the repair template as a separate stack in `ap-south-1`, supplying the key
   through the console's masked parameter or an existing Secrets Manager ARN.
   Review/approve its IAM capabilities before deployment. Never put keys in source.
3. Initially leave `ApplicationLogGroupName` empty if the application is not deployed.
   Once its log group exists, update that parameter to the exact group name,
   `/nexaassist/` for this setup.
   The template grants invocation only to that account/log group and subscribes it.
4. Verify new application events in Datadog Logs and the integration's resource
   metrics. A completed CloudFormation stack alone does not establish delivery.

The approved standalone repair was deployed as `nexaassist-datadog-forwarder` in
`ap-south-1`. The shared `/nexaassist/` group was created with seven-day
retention and connected through the template's scoped Lambda permission/subscription.
A synthetic event written to that group appeared in Datadog as `nexaassist-api`.
Those standalone repair resources are legacy to the session-owned workflow above;
new labs do not use the shared group or standalone collector. Datadog retains
exported telemetry according to its own configuration.

The failed `DatadogIntegration` stack is left untouched in `ROLLBACK_COMPLETE`.
Its deleted account-integration role was restored as `DatadogIntegrationRole` by
the separate `nexaassist-datadog-integration` stack, now `UPDATE_COMPLETE`.
The original permissions were retained. After approval, only its `ExternalId`
parameter was changed to match Datadog's manual registration for AWS account
`227237140175`. Datadog shows that account as installed, metric collection enabled,
and the restored resource-collection policy recognized. CloudTrail recorded two
successful assumptions of the restored role after connection, with no failed
assumptions in the checked hour. The existing Forwarder
is registered in its Log Collection settings; automatic log subscriptions remain
disabled because CloudFormation manages the exact `/nexaassist/` subscription.
Use the IAM role name in Datadog, not the `pankaj-admin` AWS login name.

Failure inspection used the existing console session, then the CLI login was
refreshed before deployment.
The local `dd-agent` started for the earlier Docker check was stopped after the
switch to AWS. Other projects' agents and old Phoenix volumes were not changed.

## Start and inspect the application

```bash
uv sync --all-extras --locked
uv run --no-sync --env-file .env python -m uvicorn app.datadog_main:app \
  --host 127.0.0.1 --port 8000
```

Native stdout logs stay local until a CloudWatch or other log collection path is
configured for that process. The existing AWS deployment provides that path through
its CloudWatch log driver. Native traces and custom metrics need no Agent.
`app.main:app` remains uninstrumented for offline labs; `app.phoenix_main:app`
temporarily forwards to Datadog for old launch scripts.

In Datadog, select `DD_LLMOBS_ML_APP` in LLM/Agent Observability. Metrics Explorer
exposes `nexaassist.http.requests`, `nexaassist.http.duration_ms`,
`nexaassist.http.errors`, `nexaassist.answer.*`, `nexaassist.retrieval.*`,
`nexaassist.sampled_hallucination_rate` and `nexaassist.sampled_count` when traffic
populates them. Routes use templates; unknown paths share one bucket. Local JSON
`/metrics*` endpoints remain available. Custom metrics flush in the background.
Sampling remains off unless `LIVE_EVAL_SAMPLE_RATE` enables paid judging.

LiteLLM uses the official Datadog callback with message logging disabled and a
small override stripping provider exception messages/stacks. The pinned LiteLLM
version groups its callback traces under `DD_SERVICE=nexaassist-gateway`; the
application's workflow/evaluations use `DD_LLMOBS_ML_APP`. Gateway traces can be
separate from application traces; an alias alone does not prove which provider ran.
Native gateway launches need `PYTHONPATH=app/gateway` for that privacy callback.

The local Compose Agent remains an optional `local-agent` profile for Docker
experiments. It is not started by the default stack or used by the AWS runtime.

## Correlation and evaluation recovery

Instrumented responses expose `x-datadog-trace-id` (32 hex characters) and
`x-datadog-span-id` (decimal). Answers carry matching `datadog_trace_id` and
`datadog_span_id`. These identify the LLM workflow receiving evaluations. Logs
carry both `llmobs.trace_id` and native `dd.trace_id`, which the SDK may assign
differently, plus the joining span ID. Deprecated `phoenix_*` response fields
remain readable for historical feedback and are not populated by new requests.

`POST /answer/evaluated` publishes existing Ragas results after responding. Sampled
`/answer` judging also publishes against the original answer. Export failure does
not replace a completed response. Scored zero remains zero; unavailable/error
results use categorical `ragas_<metric>_status` evaluations without invented scores.
Questions, reference answers and evaluator error text are not evaluation metadata.

```bash
curl --fail --silent --show-error http://127.0.0.1:8000/answer/evaluated \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is the maximum loan amount for a NexaHome Loan?","as_of":"2026-10-01","product_id":"NEXA-HL","top_k":5,"reference_answer":"The maximum loan amount is 7.5 crore."}' \
  -D /tmp/datadog-evaluated.headers -o /tmp/datadog-evaluated.json

uv run --no-sync --env-file .env python -m app.evaluation.datadog_export \
  --response /tmp/datadog-evaluated.json --headers /tmp/datadog-evaluated.headers
```

Recovery validates that both saved files identify the same workflow and fails
explicitly on invalid files or HTTP failures. `datadog_evaluations_published`
means intake accepted the request; verify the matching workflow after ingestion.

HTTP JSON capture is bounded to 64 KiB per direction. Invalid/large payloads are
omitted without changing responses. Model text is bounded and embedding vectors
are not exported. Exception telemetry and application/uvicorn JSON logs retain
error type while omitting exception messages/stacks. Request logs omit query
strings, headers and bodies. The SDK is pinned because its export hook must also
sanitize prompt variables and workflow values unavailable to its public processor.

## Verification

```bash
uv run --no-sync python -m pytest -q tests
uv run --no-sync ruff check .
uv run --no-sync mypy --explicit-package-bases app training infra
```

Phoenix-specific tests were replaced by Datadog SDK and intake checks. Offline
checks use synthetic providers and intercepted export queues. No evaluation gate
was lowered. Full-repository `mypy .` has existing module-discovery/test typing
issues; application, training and infrastructure checks use explicit package bases.

Migration verification on 3 November 2026: **437 offline tests passed**, Ruff passed,
Mypy passed for 110 application/training/infrastructure files, and both changed
CloudFormation templates passed `cfn-lint`. Live synthetic agentless workflows
appeared in Datadog; metrics and categorical evaluation intake returned HTTP 202.
A CloudWatch event traversed the real Forwarder subscription and appeared in Logs.
Subsequent [live AWS validation](../operations/DATADOG_VALIDATION.md) deployed a
60-minute application session, verified three representative queries, one Ragas
evaluation, exact trace IDs, four attached numeric scores, correlated application
logs and an AWS metric time series. The updated offline suite passed 439 tests.
The rollout also fixed the shared-log permission boundary and corpus ownership.
Session lifecycle and unique-tag changes subsequently passed **446 offline tests**,
including bounded Forwarder-code provisioning and deletion checks. The repository's
workflow stack-update prohibition remains enforced.
Load testing and a broad quality benchmark were not run; one-case context precision
was low (0.111) despite a correct cited answer.

AWS application sessions additionally fetch `nexa-lab-datadog` from Secrets Manager.
Pass `--datadog-secret-arn` at creation, or configure GitHub `aws-lab` variables
`DATADOG_API_KEY_SECRET_ARN`, `DD_SITE` and `DD_LLMOBS_ML_APP`. Release archives
contain only the secret ARN. Recreate pre-migration disposable application sessions
to acquire their new secret permission; the Datadog integration is separate.

Official references: [AWS integration](https://docs.datadoghq.com/integrations/amazon-web-services/),
[Forwarder template and ZIP option](https://github.com/DataDog/datadog-serverless-functions/blob/master/aws/logs_monitoring/template.yaml),
[Datadog SDK](https://docs.datadoghq.com/llm_observability/instrument/sdk/),
[external evaluations](https://docs.datadoghq.com/llm_observability/investigate/evaluations/external_evaluations/).
