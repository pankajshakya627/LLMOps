# Start, inspect and delete an AWS + Datadog session

Use **GitHub Actions → Disposable AWS lab** for the whole session. Your Mac does
not need local application containers. The application runs in AWS Mumbai
(`ap-south-1`); traces, logs, metrics and Ragas evaluations are viewed in Datadog.

## Reusable account setup

Keep these between sessions so the next Start works without creating credentials:

- `nexa-ci-bootstrap`: GitHub OIDC, deployment role and permission boundary.
- `nexaassist-datadog-integration` / `DatadogIntegrationRole`: the existing Datadog AWS account connection.
- Secrets Manager `nexa-lab-openai` and `nexa-lab-datadog`.
- The GitHub `aws-lab` environment and its role/secret ARN variables.
- Datadog's account, API key and already exported history, under its configured retention.

GitHub variables include `AWS_REGION`, `AWS_GITHUB_ROLE_ARN`,
`AWS_CLOUDFORMATION_ROLE_ARN`, `AWS_SESSION_BOUNDARY_ARN`,
`OPENAI_API_KEY_SECRET_ARN`, `DATADOG_API_KEY_SECRET_ARN`, `DD_SITE` and
`DD_LLMOBS_ML_APP`. They contain configuration and references; API keys stay in
Secrets Manager. The environment secret `AWS_UI_ALLOWED_CIDR` contains the
trainer's public IPv4 `/32`. Refresh it before Start when your public IP changes.
The environment remains restricted to `main`.

For another AWS account, follow [one-time setup](README.md#one-time-aws-and-github-setup).
The bootstrap must include the session Forwarder/code/subscription permissions.
A bootstrap stack alone does not mean the application has been deployed.

## 1. Start

Open [Actions → Disposable AWS lab](https://github.com/pankajshakya627/LLMOps/actions/workflows/aws-lab.yaml)
and choose **Run workflow**:

| Input | Selection |
|---|---|
| Branch | `main` |
| operation | `start` |
| session | `nexa-lab-training`, or another unused `nexa-lab-*` name |
| model_provider | `openai` |
| minutes | `60` or `120` |
| budget | Existing USD planning allowance; this tag is not a hard spending cap |

Wait until **checks / check** and **session** both succeed. Start creates the
application host, its services, the session Forwarder and log subscription, and
all session storage. It verifies the official Forwarder ZIP checksum, builds
immutable images, ingests the registered synthetic corpus and tests a cited answer.
Failed new starts run cleanup. Starting the same name while it is live fails;
it does not delete or replace that live session.

The lifetime starts at infrastructure creation. Builds and deployment use part
of that time. `deploy` replaces application images without extending expiry.
Bedrock remains a separate explicit option in the [AWS runbook](README.md).

## 2. Open the application and Datadog

Open **the successful run → Summary**. It provides:

- **Open the application**: the current AWS UI URL, restricted to the trainer IP.
- **Datadog traces and evaluations**: filtered to this particular session.
- **Datadog logs**: the same session's forwarded application logs.
- **Metrics Explorer** and a `lab_session_id:...` filter to paste there.
- Scheduled expiry in IST.

Use the new run's URL rather than an old bookmark: the host IP changes after
recreation. Each creation gets a new session ID even when the stack name is reused,
so the Datadog links distinguish old history from the new run.

Try the synthetic maximum-home-loan, current processing-fee and unsupported-policy
queries. The app displays a Datadog trace ID. In Datadog inspect its workflow,
model/retrieval spans, duration, errors, tokens and correlated logs. Evaluated
answers attach the four Ragas scores to the matching workflow. The gateway has a
separate `nexaassist-gateway` application with the same session tag.

The `aws-lab` environment variable `DD_CAPTURE_CONTENT=true` enables masked query
and answer text for this synthetic training lab. The default is `false` when the
variable is absent. Change it through GitHub Settings → Environments → `aws-lab`,
then run **Deploy**; subsequent **Start** runs keep the same choice. Existing
traces cannot gain text retroactively. Use the summary's **Datadog answer queries**
link to omit health-check rows. See the [Datadog runbook](../../app/observability/README.md)
for the 64 KiB limit, masking and evaluation recovery.

Direct UI access uses HTTP and synthetic data. API, database, gateway and validator
ports remain private. An optional authenticated SSM tunnel can expose UI port 8501
or API port 8000 locally; Datadog itself needs no tunnel or local telemetry server.

## 3. Destroy

Run the same workflow with **operation=destroy** and the **exact session name**.
Wait for a green run; deletion is not complete merely because it was requested.
Destroy terminates the host before emptying object versions and deleting the stack.

| Deleted with the session | Retained for reuse |
|---|---|
| EC2, encrypted EBS, pgvector data and session feedback | GitHub/AWS bootstrap and account integration role |
| App/gateway/validator images and ECR repositories | OpenAI and Datadog API-key secrets |
| Release files, reports and Forwarder ZIP versions in the session bucket | GitHub environment configuration |
| Forwarder Lambda, its role and invocation permission/subscription | Already exported Datadog history |
| Application, Forwarder and lifecycle CloudWatch log groups | Existing AWS/organization audit trails |
| Runtime secret, expiry schedule, lifecycle function and session network | Datadog account and settings |

Download reports or export feedback before Destroy if you want to keep them.
CloudWatch deletion does not erase data already exported to Datadog. Buffered
telemetry is not guaranteed to finish exporting at teardown.

Expiry invokes the same cleanup path. The host's shutdown timer is an additional
compute fallback; it does not prove every resource was removed. Investigate
`DELETE_FAILED` and retry Destroy after fixing its cause. The failed historical
`DatadogIntegration` stack is not part of a lab session.

## 4. Recreate

After the Destroy workflow succeeds and the old stack is gone, run **Start** again.
The same name can be reused. The new stack owns fresh collectors, logs, database,
images and storage; the reusable credentials and Datadog account link are reused.
No manual Forwarder installation or Docker Agent is required.

## Optional terminal commands

```bash
gh workflow run aws-lab.yaml --repo pankajshakya627/LLMOps --ref main \
  -f operation=start -f session=nexa-lab-training \
  -f model_provider=openai -f minutes=60 -f budget=5

gh run list --repo pankajshakya627/LLMOps --workflow aws-lab.yaml --limit 5

gh workflow run aws-lab.yaml --repo pankajshakya627/LLMOps --ref main \
  -f operation=destroy -f session=nexa-lab-training
```

Verify the AWS account/Region and exact stack when troubleshooting. Use the
current workflow's failed step and CloudFormation events; do not start a second
session with a name that is still creating, running or deleting.
