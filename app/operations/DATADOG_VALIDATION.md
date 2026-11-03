# Datadog AWS validation — 3 November 2026

Validated the migrated application on `nexa-lab-dd-20261103` in `ap-south-1`.
The session was created for 60 minutes; scheduled expiry is **23:08:09 IST on 3 November 2026**.
The temporary [application UI](http://65.0.134.44:8501) is restricted to the saved trainer IP.
Only the registered synthetic course corpus was ingested.

## Live queries

| Case | Result | HTTP duration | Trace ID |
|---|---|---|---|
| maximum_loan | answered | 2.84 s | `6aea105c00000000d8b39744036e5b59` |
| current_processing_fee | answered | 6.21 s | `6aea105e00000000fe7a7282fdc3a07b` |
| unsupported_policy | insufficient_evidence | 2.37 s | `6aea106500000000ce7aa74d1450a3ce` |
| evaluated_maximum_loan | answered | 33.25 s | `6aea109900000000baf04541cdd1710b` |

The maximum loan answer was ₹7,50,00,000, cited to `POL-HL-V3`. The current fee answer used
`CIR-2026-07`: 0.30%, minimum ₹5,000, maximum ₹10,000, plus 18% GST. The unsupported
cryptocurrency-custody question abstained and returned no citations. Returned schemas and
response/header trace and span IDs were checked for all four successful answer requests.

## Evaluation and Datadog delivery

| Metric | Live score |
|---|---|
| Faithfulness | 1.0 |
| Answer relevancy | 0.9583824114285449 |
| Context precision | 0.11111111109999999 |
| Context recall | 1.0 |

**Context precision is low.** This single case used `top_k=20`; successful answer and pipeline checks
do not establish retrieval quality across the corpus. No evaluation threshold was lowered.

In Chrome, Datadog showed the exact [evaluated workflow](https://app.datadoghq.com/llm/traces?query=%40ml_app%3Anexaassist%20%40trace_id%3A6aea109900000000baf04541cdd1710b&fromUser=true),
span `340727592469766836`, with all four numeric scores and 44 correlated logs.
The log panel identified `/nexaassist/`, `nexaassist-datadog-forwarder`, HTTP 200 for
`/answer/evaluated`, and `datadog_evaluations_published` with count 4. The AWS Lambda
invocation time series was also visible in Datadog. Content capture stayed disabled for this session.

## Validation

- Application deployment smoke, `/health`, `/ready` and browser UI health passed.
- Invalid `top_k=0` returned 422; explicit instruction override returned 400.
- Rate limiting returned 429 with `Retry-After`; the test respected it before retrying.
- The deployed Guardrails service passed its five-case schema self-check.
- `/metrics/http` and `/metrics/answers` returned 200.
- **439 offline tests passed**; Ruff, shell syntax and all three CloudFormation template checks passed.

The live rollout exposed two deployment issues, now fixed: the bootstrap permissions boundary
omitted the exact shared log group, and extracted corpus ownership prevented UID 10001 from
reading source files. Both have regression checks. Runtime `.env` remains mode 0600.

## Artifacts and lifecycle

[Raw request results](datadog-validation-20261103.json) include statuses, answers, scores and IDs.
The private session bucket also contains `reports/datadog-20261103/live-verification.json` and
deployment health/memory reports. The immutable images used were:

```text
APP_IMAGE=227237140175.dkr.ecr.ap-south-1.amazonaws.com/nexa-lab-dd-20261103/app@sha256:9775e062603aa87250fab2c0b4ff746415c031000ee6371244cdd3b0ba28ebf9
GATEWAY_IMAGE=227237140175.dkr.ecr.ap-south-1.amazonaws.com/nexa-lab-dd-20261103/gateway@sha256:9512f5a282f593535d79fea891d901431af33fca9dd2cc265239f5690f655625
GUARDRAILS_IMAGE=227237140175.dkr.ecr.ap-south-1.amazonaws.com/nexa-lab-dd-20261103/guardrails@sha256:4e76d1ed47b84cb2dc57d3334a4c0d2de71df8a7820527fc66d40f989a197d62
```

The session owns its compute, disk, bucket and ECR repositories. Its scheduled cleanup is enabled;
successful deletion at the future expiry has not yet been observed. The approved bootstrap boundary
change, `nexa-lab-datadog` secret, Datadog integration/Forwarder and shared log group persist independently.
No load test, broad security assessment or multi-case quality benchmark was run.
