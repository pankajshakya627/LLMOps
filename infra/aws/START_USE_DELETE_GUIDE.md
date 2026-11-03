# Start the AWS app, open it in a browser, and delete it

> Monitoring now uses the [Datadog AWS runbook](../../app/observability/README.md).
> The API sends traces, custom metrics and evaluations directly; CloudWatch logs use the Forwarder.
> The old Phoenix viewing instructions below are historical and no longer apply.
> Configure `DATADOG_API_KEY_SECRET_ARN`, `DD_SITE`, and `DD_LLMOBS_ML_APP` for GitHub AWS sessions.

Use this guide for each disposable NexaAssist training session. Commands marked
**Mac terminal** can run from any directory, including `~`; the GitHub commands
include the repository explicitly. Your local Python virtual environment and
local Docker services are not required for these cloud operations.

**Order:** sign in → check the secret and existing session → start once → wait
for green deployment → open the browser → destroy → verify deletion → disable
unused secret storage.

| Setting | Value |
| --- | --- |
| AWS account | `227237140175` |
| Region | Mumbai, `ap-south-1` |
| Local AWS profile | `nexa-lab` |
| GitHub repository | `pankajshakya627/LLMOps` |
| GitHub environment | `aws-lab` |
| Application stack | `nexa-lab-training` |
| Reusable permissions stack | `nexa-ci-bootstrap` |
| Model provider | OpenAI; Bedrock stays disabled |

## 1. Sign in and check your tools

**Mac terminal:**

```bash
aws --version
gh auth status
session-manager-plugin --version
aws login --profile nexa-lab
aws sts get-caller-identity --profile nexa-lab --region ap-south-1
```

Check that the returned account is `227237140175` and the identity is your
intended IAM user. If GitHub is not authenticated, run `gh auth login`.
If the Session Manager plugin is missing on this Mac, install it:

```bash
brew install --cask session-manager-plugin
```

This uses the existing bootstrap and GitHub variables. If configuring a different
AWS account, follow the [one-time setup](README.md#one-time-aws-and-github-setup)
first; ARNs from the old account will not configure the new account.

For automatic browser access, complete the [one-time bootstrap update and saved
trainer IP setup](README.md#enable-automatic-browser-access-once). After that,
port 8501 is configured automatically on every fresh session. Refresh the
`AWS_UI_ALLOWED_CIDR` environment secret only when your public IPv4 changes,
before starting a new session.

## 2. Check or restore the OpenAI secret

Full cost cleanup can leave the reusable secret marked for deletion. Check its
metadata without printing the API key:

```bash
aws secretsmanager describe-secret \
  --profile nexa-lab --region ap-south-1 \
  --secret-id nexa-lab-openai \
  --query '{Name:Name,MarkedForDeletion:DeletedDate}' --output json
```

If `MarkedForDeletion` is `null`, the secret is active; continue. If it contains
a date and is still recoverable, restore it before deployment:

```bash
aws secretsmanager restore-secret \
  --profile nexa-lab --region ap-south-1 \
  --secret-id nexa-lab-openai
```

If the secret no longer exists, recreate `nexa-lab-openai` in Secrets Manager in
Mumbai, with only the OpenAI key in the **Plaintext** field. Choose the default
`aws/secretsmanager` encryption key. Store its new ARN in the GitHub `aws-lab`
environment variable `OPENAI_API_KEY_SECRET_ARN`. The secret value must not be a
JSON object or an `OPENAI_API_KEY=...` assignment. Never paste the key into GitHub
variables or terminal commands.

Restoring or recreating an active secret resumes its storage billing.

## 3. Check whether an application session already exists

```bash
aws cloudformation describe-stacks \
  --profile nexa-lab --region ap-south-1 \
  --stack-name nexa-lab-training \
  --query 'Stacks[0].StackStatus' --output text
```

| Result | Next action |
| --- | --- |
| Error saying the stack does not exist | Expected after cleanup; start a new session in step 4 |
| `CREATE_IN_PROGRESS` | Wait for the existing deployment; do not start a second session with this name |
| `CREATE_COMPLETE` | Check its GitHub deployment result; if successful, continue to step 5 |
| `DELETE_IN_PROGRESS` | Wait for deletion before reusing the name |
| Failure or rollback status | Inspect the failed workflow/stack events, fix the cause and destroy the failed session |

`nexa-ci-bootstrap` contains deployment permissions. Its existence does not mean
the application is running. In the CloudFormation console, choose the correct
account and Mumbai Region. **Filter status → Deleted** shows past lab sessions;
clear old search filters if stacks appear missing.

## 4. Start once and wait for deployment

**Mac terminal:**

```bash
gh workflow run aws-lab.yaml \
  --repo pankajshakya627/LLMOps --ref main \
  -f operation=start -f session=nexa-lab-training \
  -f model_provider=openai -f minutes=60 -f budget=5
```

Open the run URL printed by that command, or visit
[Actions → Disposable AWS lab](https://github.com/pankajshakya627/LLMOps/actions/workflows/aws-lab.yaml).
Wait until **both `checks / check` and `session` succeed**. Creation of a
`workflow_dispatch` event only confirms the request was accepted.

For a single operator, the following finds and watches the newest manual run on
`main` without a typed `RUN_ID` placeholder. Check its timestamp against the run
URL printed above, particularly if someone else can also start workflows:

```bash
gh run list --repo pankajshakya627/LLMOps --workflow aws-lab.yaml --limit 5

LAB_RUN_ID=$(gh run list \
  --repo pankajshakya627/LLMOps --workflow aws-lab.yaml \
  --branch main --event workflow_dispatch --limit 1 \
  --json databaseId --jq '.[0].databaseId')

gh run watch "$LAB_RUN_ID" --repo pankajshakya627/LLMOps --exit-status
```

Previous successful deployments took around 14 minutes; this is not a guarantee.
The 60-minute lifetime starts at infrastructure creation, so provisioning and
build time use part of it. Choose `minutes=120` instead for a two-hour session
when needed; this consumes more usage. The `$5` budget input is a planning tag,
not a hard spending cutoff. AWS and OpenAI billing are separate.

If a live session needs a code update, use `operation=deploy` instead of `start`.
Deployment does not extend its original expiry. If the workflow fails, read the
failed step; a failed new session is automatically cleaned up.

## 5. Fetch the current host details

Run this only after successful deployment. It avoids copying an expired instance
ID or yesterday's browser URL:

```bash
LAB_INSTANCE_ID=$(aws cloudformation describe-stacks \
  --profile nexa-lab --region ap-south-1 \
  --stack-name nexa-lab-training \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue | [0]" \
  --output text)

LAB_APP_URL=$(aws cloudformation describe-stacks \
  --profile nexa-lab --region ap-south-1 \
  --stack-name nexa-lab-training \
  --query "Stacks[0].Outputs[?OutputKey=='ApplicationUrl'].OutputValue | [0]" \
  --output text)

printf 'Current instance: %s\nBrowser URL: %s\n' "$LAB_INSTANCE_ID" "$LAB_APP_URL"

aws cloudformation describe-stacks \
  --profile nexa-lab --region ap-south-1 --stack-name nexa-lab-training \
  --query "Stacks[0].Outputs[?OutputKey=='ExpiresAt'].OutputValue | [0]" \
  --output text
```

The final value is the expiry time in **UTC**; add 5 hours 30 minutes for IST.
Keep using the same Mac terminal so its variables remain set. If you open a new
terminal, repeat this step before using `$LAB_INSTANCE_ID` or `$LAB_APP_URL`.

## 6A. Direct AWS IP in your browser, restricted to your IP

Open **GitHub Actions → your successful run → Summary → Open the application**,
or open `$LAB_APP_URL` from step 5. Every fresh session configures port **8501**
automatically from the saved `AWS_UI_ALLOWED_CIDR` environment secret. No Docker
override, SSH connection or manual inbound rule is needed.

From your **Mac terminal**, you can verify the UI health endpoint:

```bash
curl --fail --connect-timeout 10 --max-time 15 "${LAB_APP_URL}/_stcore/health"
```

The response should be `ok`. Use **http://CURRENT_PUBLIC_IP:8501**, including
`:8501`; ports 80 and 443 are not configured. Use synthetic data only: direct
access has no application login or TLS. Anyone sharing your allowed public IP
can reach the UI. API, Phoenix and database ports remain private.

If your public IP changes, use the SSM tunnel below for the current session.
Refresh the saved secret using the one-time setup command before your next
fresh session. Updating the secret or redeploying code does not edit a running
session's allowlist. Never broaden the source to `0.0.0.0/0`.

Older sessions without `ApplicationUrl` used a private template. Finish/destroy
them and start a fresh session with the updated code; do not deploy the new
public UI mapping into an old stack. The workflow rejects those redeployments
before image builds. Existing sessions are not automatically migrated.

## 6B. Private browser access through an SSM tunnel

This alternative uses authenticated SSM forwarding and works even when your
browser network no longer matches the saved allowlist. From the **Mac terminal**
where you fetched the instance ID:

```bash
aws ssm start-session \
  --profile nexa-lab --region ap-south-1 \
  --target "$LAB_INSTANCE_ID" \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["8501"],"localPortNumber":["18501"]}'
```

Keep that terminal open and visit **http://localhost:18501**. The application
runs on AWS; your laptop forwards browser traffic to it. Closing the terminal
closes this access path, not the AWS session.

## 7. View complete synthetic traces and API monitoring

The current AWS Compose profile enables content capture for the synthetic course
corpus. Deploy the updated code with the existing workflow's `operation=deploy`
and the current session name. This replaces the release without extending expiry.
Previously redacted traces cannot be recovered: send a new request after deployment.

After fetching `LAB_INSTANCE_ID` in step 5, open Phoenix from your Mac:

```bash
aws ssm start-session \
  --profile nexa-lab --region ap-south-1 --target "$LAB_INSTANCE_ID" \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["6006"],"localPortNumber":["16006"]}'
```

Keep that terminal open and visit <http://localhost:16006>. In project
`nexaassist-training`, open a NEW HTTP request, then inspect Input, Output, and
its child spans: retrieval, prompt/model generation and `validate_output` where
those steps ran. The root Output is the final API response, including citations
and quality fields when available. Early refusals/empty retrieval do not invoke
every downstream step. In project `nexaassist-gateway`, inspect actual provider,
model, latency and reported tokens. Gateway raw messages stay disabled;
application model spans contain the captured messages. The two projects do not
guarantee a shared trace ID. Embedding vectors remain hidden.

In another Mac terminal, fetch the instance ID again if necessary and forward
remote port `8000` to local `18000` using the same command pattern. Then open:

| View | Browser URL |
| --- | --- |
| Try all API routes | <http://localhost:18000/docs> |
| All API route counts, statuses, errors and p50/p95/p99 latency | <http://localhost:18000/metrics/http> |
| Answer usage, token totals, error rate and sampled quality | <http://localhost:18000/metrics/answers> |
| Retrieval counts, errors and empty results | <http://localhost:18000/metrics> |
| Readiness of the selected database | <http://localhost:18000/ready> |

Use Swagger `POST /answer/evaluated` for quality scores and Phoenix annotations;
this makes paid judge/embedding calls. A synthetic example request is:

```json
{"query":"What is the maximum loan amount for a NexaHome Loan?","as_of":"2026-10-01","product_id":"NEXA-HL","top_k":5}
```

Regular `/answer` does not run Ragas by default. Scores can be unavailable or
error rather than zero. Cost through the gateway remains null in app metrics;
inspect provider billing separately. HTTP route counters reset on restart and
latency percentiles use the last 1000 requests per route in that process.

For AWS monitoring, open **CloudWatch → Logs Insights**, select
`/nexaassist/nexa-lab-training` (substitute your session stack name), choose the
session time range and run:

```text
filter event = "http_request_completed"
| stats count(*) as requests, sum(server_error) as server_errors,
        pct(duration_ms, 95) as p95_ms by route, method
| sort requests desc
```

To find a particular API trace's logs, use:

```text
fields @timestamp, route, method, status_code, duration_ms, trace_id, span_id
| filter event = "http_request_completed" and trace_id = "PASTE_PHOENIX_TRACE_ID"
| sort @timestamp desc
```

[CloudWatch documents these aggregation/visualization functions](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax-Stats.html).
EC2's Monitoring tab provides basic instance metrics; `operation=capacity` prints
host/container memory. No new custom metrics, alarms or polling judge loop is
provisioned by this change. Log queries and retained telemetry can incur charges.
Session teardown deletes the logs and Phoenix volume as before.

Content capture covers JSON bodies up to 64 KiB per direction. Larger, incomplete
or invalid JSON is omitted with a reason. Headers are not captured, and request
URL query strings are excluded from application span URLs. Supported personal
identifiers and common credential fields are masked; this does not detect all
secrets or PII. Exception events retain the exception type but omit message,
stacktrace and status-description text. Raw model drafts may appear before
application output validation.
Set `PHOENIX_CAPTURE_CONTENT` to `"false"` in `app/compose.aws.yaml` and redeploy
before using real/confidential content. Authentication and security checks still
run normally; non-JSON/binary payload bodies are not captured.

| Component | AWS port | Browser address |
| --- | --- | --- |
| Streamlit, direct access after 6A | `8501` | `http://CURRENT_PUBLIC_IP:8501` |
| Streamlit, SSM tunnel after 6B | `8501` → local `18501` | `http://localhost:18501` |
| FastAPI docs, optional separate SSM tunnel | `8000` → local `18000` | `http://localhost:18000/docs` |
| Phoenix, optional separate SSM tunnel | `6006` → local `16006` | `http://localhost:16006` |
| SSH | `22` | Not enabled for inbound access; use Session Manager for a terminal |
| Default HTTP / HTTPS | `80` / `443` | Not configured for this lab |

For an optional API or Phoenix tunnel, repeat the 6B command in another Mac
terminal with the matching remote/local port pair from the table. Keep backend
services private.

In Streamlit, ask a synthetic policy question, for example:
**What is the maximum loan amount for a NexaHome Loan?** Inspect the answer and
its citations. Each question uses OpenAI; avoid automated question loops.

## 8. Finish: destroy the session and verify deletion

Close browser/tunnel/server-terminal sessions when done, then run from your Mac:

```bash
gh workflow run aws-lab.yaml \
  --repo pankajshakya627/LLMOps --ref main \
  -f operation=destroy -f session=nexa-lab-training
```

Watch the **new destroy run** using its printed URL, or repeat the `LAB_RUN_ID`
lookup/watch commands from step 4 after checking the newest run's timestamp.
Wait for successful completion. This deletes the session's database, feedback,
traces, reports, images and infrastructure, including any temporary UI rule.
Download reports you need before destruction.

Verify that the named active stack no longer exists:

```bash
aws cloudformation describe-stacks \
  --profile nexa-lab --region ap-south-1 \
  --stack-name nexa-lab-training \
  --query 'Stacks[0].StackStatus' --output text
```

The expected result after deletion is an error saying the stack does not exist.
To see the deletion history rather than that error:

```bash
aws cloudformation list-stacks \
  --profile nexa-lab --region ap-south-1 \
  --stack-status-filter DELETE_COMPLETE \
  --query "reverse(sort_by(StackSummaries[?StackName=='nexa-lab-training'], &DeletionTime))[0].{Status:StackStatus,Deleted:DeletionTime}" \
  --output table
```

Expected: `DELETE_COMPLETE` for the session you just destroyed. In the console,
use **CloudFormation → Mumbai → Stacks → Filter status → Deleted**. If deletion
fails, inspect Events and fix the reported resource; do not assume shutdown
removed storage. Automatic expiry is a fallback, and deletion can take time.
GitHub's completed run rows are history and do not mean the app is still running.

## 9. Stop retained secret storage charges

The session destroy operation retains the reusable OpenAI secret. After all
OpenAI lab sessions are gone, mark it for deletion if it is no longer needed:

```bash
aws secretsmanager delete-secret \
  --profile nexa-lab --region ap-south-1 \
  --secret-id nexa-lab-openai --recovery-window-in-days 7
```

AWS does not charge for a secret marked for deletion. It is inaccessible until
restored and recoverable during its recovery window; return to step 2 before the
next lab start. After permanent deletion, recreate the secret and update its
ARN in GitHub. Deleting this AWS copy does not revoke the OpenAI key itself.

Keep `nexa-ci-bootstrap` for repeat deployments: its IAM roles/policy/OIDC setup
has no hourly compute or storage. If bootstrap was uploaded through the AWS
console, an S3 `cf-templates-...` bucket may retain an uploaded template. Check
its contents and remove only unused lab template copies backed up in the repo;
do not delete unrelated buckets or objects. See the [full cleanup runbook](README.md#delete-everything-belonging-to-the-session)
for removing the bootstrap itself if desired.

Past usage can appear in billing after cleanup. AWS and OpenAI bills are
separate, and the budget tag does not enforce a spending cap.

## 10. Common errors

| Message / symptom | What to do |
| --- | --- |
| `not a git repository` from `gh` | Include `--repo pankajshakya627/LLMOps`, as every command above does |
| HTTP 404 for `runs/RUN_ID` | `RUN_ID` was a placeholder; use the automatic numeric lookup in step 4 |
| `AlreadyExistsException` | A session with that name exists; wait or use `deploy`, not another `start` |
| No application stack in the console | Check the run outcome, account, Mumbai Region and Active/Deleted filters; the session may have expired |
| `Your session has expired` | Run `aws login --profile nexa-lab` |
| Secret is scheduled for deletion | Restore it in step 2 before deployment |
| OpenAI secret must contain only the API key | Fix the secret's plaintext format; do not print the key in logs or chat |
| `TargetNotConnected` | Use the new instance ID and verify EC2 is running and SSM is Online; a terminated ID cannot reconnect |
| Browser cannot reach the public IP | Use the new session's `ApplicationUrl` with `:8501`; verify your browser network matches the saved `/32`, or use SSM in 6B |
| Browser cannot reach localhost | Keep the 6B tunnel open and verify its target is the current instance |
| Failed SSH connection | Use SSM for the server terminal; SSH is not needed to open the app |
| `DELETE_FAILED` | Inspect CloudFormation Events and resolve the named resource before considering cleanup complete |

References: [AWS Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html),
[AWS secret deletion](https://docs.aws.amazon.com/secretsmanager/latest/userguide/manage_delete-secret.html),
[Docker Compose overrides](https://docs.docker.com/reference/compose-file/merge/),
[GitHub run lookup](https://cli.github.com/manual/gh_run_list).

For infrastructure setup and design, use the [full AWS runbook](README.md) and
the [CI/CD explanation](CI_CD_GUIDE.md).
