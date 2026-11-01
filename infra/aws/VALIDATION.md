# AWS lab verification

## Automatic trainer-restricted UI access — 1 November 2026

Prepared future-session access on `http://PUBLIC_IP:8501`: required global IPv4
`/32`, CloudFormation-owned ingress, public UI Docker binding, private backend
ports, and a browser link in the successful workflow summary. Older stacks are
rejected before release builds/uploads; their administrative status, capacity,
evaluation and cleanup remain available. No existing application session was
modified and no new EC2 instance was launched for this change.

| Check | Result |
| --- | --- |
| TDD before implementation | 30 failures, 19 passes in the expanded AWS tests |
| Final focused AWS tests | **51 passed**, including legacy evaluation/deletion |
| Complete offline suite | **440 passed**, zero failures, errors or skips |
| Required training/answer/readiness subset | **53 passed** |
| Deployment CLI line coverage | **80%** of `lab.py`; all **22/22** changed executable lines covered |
| Repository Ruff; CI-scoped Mypy | Passed; Mypy checked 78 files |
| CloudFormation / actionlint / host shell syntax | Passed; external ShellCheck unavailable |
| Both AWS Compose profiles | Rendered with temporary fake credentials; only UI 8501 public, API/Phoenix loopback, other services unpublished |
| Code and security reviews | No actionable findings; guides also reviewed |
| Redacted secret scan | No changed-file findings; one existing tracked trace-ID false positive; ignored local credential files were not uploaded |
| Diff whitespace | Passed |

The first broad test run could not download its public tokenizer vocabulary.
Caching that vocabulary in a temporary directory resolved the environmental
failures; the final suite passed without test skips or changes to dependencies,
thresholds, constraints or unrelated application code. Temporary coverage tools
were also installed outside the repository. Plain `mypy .` still encounters the
previously documented duplicate-module discovery issue; the CI command passes.

The approved one-time configuration was applied and verified: `nexa-ci-bootstrap`
reached **UPDATE_COMPLETE**; the only template difference was adding the two
ingress actions to CloudFormationRole, scoped to this account/Region and
`Session=nexa-lab-*` security groups. Its dependent GitHubRole ARN reference
was reevaluated without a policy change or replacement. All existing parameters,
including the stack-owned OIDC setting and `EnableBedrock=false`, were preserved.
The trainer Mac's current IPv4 `/32` was saved as the `aws-lab` environment secret
`AWS_UI_ALLOWED_CIDR`; only its metadata was subsequently verified.

Live provisioning and browser reachability for this new template remain
unverified until the code is published and a fresh session is started. HTTP has
no TLS or application login; users behind the same allowed public IP can reach
the UI. An IP change requires refreshing the saved secret before a fresh session;
SSM forwarding remains available during the current session. The saved IP is
masked in GitHub logs but visible to authorized AWS readers.

## Final chargeable-resource cleanup — 31 October 2026, 23:30 IST

The latest session from run `41211732355` reached `DELETE_COMPLETE` at
21:20:38 IST. A subsequent private audit ran 840 inventory checks across all
17 enabled Regions and global services. No nonterminated EC2 instances, EBS
volumes, owned snapshots, Elastic IPs, NAT gateways, VPC endpoints, network
interfaces, load balancers, ECR repositories, Lambda functions, log groups,
alarms or schedules were found. Accessible database, container, search, cache,
file-storage, API, notebook/job, WAF, domain-zone and commitment checks returned
no active resources. Customer-managed KMS key checks found none.

Two chargeable leftovers were addressed: the reusable OpenAI secret was marked
for deletion with a seven-day recovery window, and the sole remaining S3 object
and bucket were deleted. The object was verified byte-for-byte against the
repository's bootstrap template before removal. A fresh global S3 listing was
empty; the secret's deletion marker was confirmed. Restore the secret before
the next lab start if still within its recovery window.

Only the IAM/OIDC bootstrap stack remains active; it contains no running
compute/storage. The tagging API retained a historical instance entry, but the
live EC2 inventory had no nonterminated instance. No GitHub jobs were active
at the audit check. Audit reports are private local files, not published account
inventory.

Limitations: 86 checks could not enumerate Kinesis, FSx, Redshift or registered
domains because the account was unsubscribed or its Free plan disallowed the
service. No service subscriptions or plan upgrades were enabled. Other audit
checks returned without unexpected failures. This is a broad inventory of
common billable services, not an exhaustive guarantee covering every AWS SKU.
Cost Explorer returned an estimated USD 0 with no service groups for the day;
the final bill and separate OpenAI usage are not reconciled. Billing can update
after cleanup. [AWS billing refresh](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html).

The earlier sections are historical deployment and validation receipts.

## Successful live application deployment

[Run 41204777838](https://github.com/pankajshakya627/LLMOps/actions/runs/41204777838)
completed successfully on 31 October 2026, using OpenAI and the Free-plan
`m7i-flex.large` host in Mumbai. The account plan was not upgraded.

The prior SSM error was retrieved using the user's newly configured local AWS
profile: the OpenAI credential secret contained a JSON wrapper. Its single key
was normalized to plaintext in a new secret version, retaining the same key and
ARN. No key was printed; the private temporary request file was deleted. This
format correction did not rotate the OpenAI key. A read-only OpenAI model-list
request authenticated successfully and confirmed the configured chat model.

Live verification passed: GitHub CI, OIDC authentication, stack creation, all
three image builds/pushes, secret loading, corpus ingestion, container health,
API readiness and the cited-answer smoke. SSM reported the new host `Online`.
The Streamlit health endpoint responded successfully; all six containers were
running with zero restarts and no OOM-killed flags. A post-start sample recorded
1,878,663,168 bytes used and 5,867,839,488 bytes available out of 8,157,741,056
bytes usable RAM (about 1.8 GiB used and 5.5 GiB available).

This verifies a small synthetic session, not peak concurrency or load capacity.
No separate Ragas evaluation was requested. Interactive browser tunneling still
requires the local Session Manager plugin. Earlier failed-session cleanup
succeeded. Timed expiry of the successful session was subsequently verified:
the exact CloudFormation stack reported `DELETE_COMPLETE` with deletion time
31 October 2026 at 19:49:23 IST (14:19:23 UTC), following its 19:48 IST scheduled
expiry. EC2 reported its host `terminated`, and lookup by the active stack name
reported that the stack no longer exists. All three lab workflow runs were
confirmed `completed`; their GitHub history is not active compute.
The reusable bootstrap and OpenAI credential secret remain outside session
teardown. No final bill or account-wide resource inventory was checked.

The user subsequently selected direct public-IP access limited to their own IP.
A temporary UI-only Compose override and TCP 8501 `/32` security-group rule were
applied to the live session. Rendered configuration assertions verified that
the API/Phoenix stayed on loopback and other backend ports were not published.
The live security group was checked to contain only this single inbound rule.
Both the public UI page and `/_stcore/health` returned HTTP 200 from the allowed
IP. This manual runtime exception leaves the repository's private deployment
defaults and the original expiry unchanged. No TLS, public authentication or
internet-wide ingress was added.

The historical attempts and offline snapshots below describe their state at
the time, before this successful deployment.

## First live attempt and Free-plan correction

[Run 41200237918](https://github.com/pankajshakya627/LLMOps/actions/runs/41200237918)
passed offline checks and authenticated to AWS through GitHub OIDC. CloudFormation
failed at `Host`: EC2 rejected `t3.xlarge` as not Free Tier eligible. The user
provided the resource-level error from stack events. Workflow cleanup reported
successful deletion of the session stack. Images, ingestion and model calls were
not reached; this was not a successful application deployment.

The user chose to keep the Free account plan. The corrected template defaults
to the AWS-listed eligible `m7i-flex.large` x86 instance and removes T3-specific
CPU-credit configuration. The host records memory snapshots and container
memory usage for capacity review. Failed starts now print failed resource reasons
before deleting the owned stack. Live capacity and corrected deployment remain
unverified until a new run succeeds; no account-plan upgrade was performed.
The AWS UI also uses the existing local Streamlit health probe, rather than
inheriting the shared image's FastAPI probe on port 8000.
Offline correction checks passed: 402 tests, the 18 affected AWS cases after
the UI-probe change, Ruff, scoped Mypy, cfn-lint, actionlint and Bash syntax.

[Corrected run 41201695589](https://github.com/pankajshakya627/LLMOps/actions/runs/41201695589)
successfully created the `m7i-flex.large` session and built/pushed all three
images. The host deployment failed in SSM command
`0d10d3ed-e737-4555-9a33-4e91286490b6`; its error output is needed to diagnose
startup. Cleanup reported `Session stack deleted`. The application, ingestion,
model compatibility and memory capacity remain unverified. A subsequent tested
`capacity` workflow operation reads only host/container memory through SSM,
without deployment or model calls. Both correction commits passed GitHub CI.

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
- Repository Ruff checks and the expanded CI Mypy scope
  (`--explicit-package-bases app infra/aws/lab.py tests/test_aws_lab.py`) passed,
  checking 77 files. No quality thresholds, tests or constraint rules were removed or weakened.
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
