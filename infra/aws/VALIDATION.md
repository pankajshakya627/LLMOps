# AWS lab verification — 31 October 2026

## OpenAI default update

The active AWS profile now defaults to OpenAI chat/judging and
`text-embedding-3-small` embeddings at 1536 dimensions. Optional Bedrock uses a
separate Compose overlay and requires both `EnableBedrock=true` in the bootstrap
and `model_provider=bedrock` in the workflow. Default template conditions omit
Bedrock resources, invocation rights and guardrail rights. The API's default
settings do not construct a Bedrock client.

Verification completed without live AWS, OpenAI or Bedrock calls:

- **401 tests passed**, including default routing, conditional resources and
  permissions, provider-change refusal, legacy-session evaluation refusal,
  missing credentials, private secret loading and malformed-key rejection.
- Repository Ruff checks and the existing CI Mypy scope (`app infra/aws/lab.py`)
  passed. No quality thresholds, tests or constraint rules were removed or weakened.
- Both CloudFormation templates passed `cfn-lint`; both workflows passed
  `actionlint`; the host script passed Bash syntax validation.
- Actual Docker Compose rendering passed for OpenAI and explicit Bedrock,
  including `.env`-based `COMPOSE_FILE` selection. No containers were started.
- Diff-scoped, redacted Gitleaks scanning found no secrets.

The broader `mypy .` command stops at a **pre-existing module-discovery issue**:
`infra/aws/lab.py` is found as both `lab` and `infra.aws.lab`. The identical error
was reproduced on unchanged commit `e32f2c3`; it is not suppressed by this change.
The CI-scoped type check passes. The constraints and evaluation datasets/gates
remain unchanged.

Live deployment and provider compatibility remain unverified. Before starting,
create the documented plaintext OpenAI credential secret, set its ARN in GitHub,
and apply the bootstrap with `EnableBedrock=false`. The reusable OpenAI secret is
outside session deletion; remove it separately when no longer needed.

## Initial implementation snapshot

Status: **implementation prepared and verified offline; no AWS session launched**.
Selected Region: **ap-south-1**. No AWS profile, credential file or environment
credential configuration was available. The checkout has no Git metadata, so no
commit, push or GitHub workflow execution was performed.

| Check | Result |
| --- | --- |
| Complete offline pytest suite | **389 passed**, zero failures, errors or skips |
| Ruff formatting of changed Python files | Passed |
| Ruff lint: `app tests infra/aws` | Passed |
| Mypy: `app infra/aws/lab.py` | Passed, 76 files |
| `cfn-lint==1.46.0`: session and OIDC bootstrap templates | Passed |
| Checksum-verified `actionlint==1.7.8`: both workflows | Passed; external ShellCheck integration unavailable |
| `bash -n infra/aws/host.sh` | Passed |
| `docker compose config --quiet`: AWS Compose with offline placeholders | Passed; no daemon or live credentials used |
| Dependency resolution | Four AWS SDK packages added; `uv.lock` updated and locked sync passed |
| GitHub Actions supply-chain refs | Official release refs resolved and pinned to immutable commit SHAs |

The durable [JUnit receipt](validation-tests.xml) records the complete test run.
New AWS tests exercise fail-closed input/output decisions and outages, redaction
before any query embedding, published-version configuration, credential-free
release manifests and digest validation, own-stack deletion, S3 versions and
delete markers, cleanup refusal on S3 errors, already-terminated instances,
duplicate-start receipts and refusal to delete a replacement stack. Existing
application, security, retrieval, feedback, UI, evaluation and telemetry tests
also passed. A first full run used `OTEL_SDK_DISABLED=true`, which disabled the
telemetry fixture and caused one failure; that CI setting was removed, and the
complete final run passed with test instrumentation enabled.

No model calls were made and no local running services or databases were changed.
The Docker daemon socket is unavailable inside the workspace sandbox, so full
Linux image builds were left to the authenticated GitHub deployment workflow.
Template validation establishes schema correctness, not complete live IAM or
service compatibility.

Live gates remaining before claiming a working AWS session:

1. Bootstrap OIDC and the bounded CloudFormation execution role in the selected
   sandbox account; configure the GitHub repository/environment variables.
2. Confirm Mumbai model access, current prices and quotas, approved inference
   profile destinations, the pinned LiteLLM response format and Guardrails policy.
3. Build/push the Linux images, execute one session, verify SSM access, pgvector
   ingestion, a cited structured answer and private trace receipt.
4. Run the optional one-case Ragas exercise and inspect actual metric statuses;
   the existing thresholds remain course placeholders.
5. Replay explicit deletion and timed expiry, confirm `DELETE_COMPLETE`, inspect
   account resources for leftovers, and compare the actual bill with the allowance.

The original quality data and thresholds were preserved:

| File | SHA-256 |
| --- | --- |
| `app/evaluation/gates.json` | `c6250feae99b190f5f072726555432c77b60fb4814b34b55a649f9f3069f1305` |
| `app/evaluation/datasets/answer.jsonl` | `69a0b957e445f5beaf8122a1d435da27286022fddf2da396922d58c49d64199e` |
| `app/evaluation/datasets/retrieval.jsonl` | `d7b01ddbe93ec642a7f805a5a70e3400279e14f4feaebe0888f97ee5c4860eab` |

The [append-only decision ledger](decisions.jsonl) retains the architecture marks
and explicitly withholds live promotion. Dollar cost and automatic deletion are
unmeasured until the account replay above is performed. Expiry deletes the cloud
session's synthetic state; the reusable IAM/OIDC bootstrap can be deleted
separately after all sessions are gone.
