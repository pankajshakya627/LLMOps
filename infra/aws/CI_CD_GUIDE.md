# CI/CD for the training application

Pull requests and pushes to main run [Application checks](../../.github/workflows/ci.yaml). Require the **Application CI** check on main. It covers locked Python dependencies, lint, types, tests, evaluation adapters, shell syntax, CloudFormation, Compose configurations, and image builds. The image tests run with external networking disabled. A loopback HTTP fixture exercises OpenAI, direct Claude through Chat Completions and Messages, and embeddings through the pinned LiteLLM server.

A manually dispatched [AWS workflow](../../.github/workflows/aws-lab.yaml) calls the same CI before start or deploy. CI exports its tested Linux/amd64 images as short-lived artifacts. The deployment job assumes a temporary AWS role through GitHub OIDC, pushes those images to ECR and records the immutable digests in the release manifest. SSM installs the checksummed release. Session operations serialize by stack name.

The deploy smoke test checks readiness, monitoring and a real cited answer before promoting the release directory. Failed updates restore the previous Compose release. Failed initial starts use an ownership receipt for cleanup. Stop and resume use the existing release and Docker volume. EventBridge Scheduler delivers a stop request carrying the active deadline. The Lambda checks it against the current schedule and ignores stale deliveries. Explicit destroy uses a separate operation.

## Model comparison

Run paid trials only on demand. For a direct-provider comparison, enable the Claude route, leave the OpenAI judge and embedding settings fixed, and use the same running release and corpus for both providers. From the current release directory on EC2 via Systems Manager:

```bash
cd /opt/nexaassist/current
for trial in 1 2 3; do
  for model in nexa-chat-openai nexa-chat-anthropic; do
    docker compose run --rm --no-deps api python -m app.evaluation.provider_trial \
      --model "$model" --trial "$trial" --output "/reports/$model-$trial.jsonl"
  done
done
```

Each process starts a fresh trial over the golden cases. Record the release digest and the configured upstream model IDs. Copy the JSONL files out of the retained release reports directory. Group results by model and case ID. Review failed critical abstentions and cases that pass only some trials. Use a paired per-case regression gate on the two result sets and report the sample size. The dataset and course thresholds are small enough that a weak difference can remain inconclusive.

Use [the operator guide](START_USE_DELETE_GUIDE.md) to resume a stopped host and [the AWS runbook](README.md) for setup, costs, and optional provider permissions.
