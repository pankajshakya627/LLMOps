# AWS training deployment

One Mumbai EC2 host runs the Streamlit UI, FastAPI, PostgreSQL/pgvector, LiteLLM and Guardrails AI. The application uses a synthetic policy corpus. Only the UI accepts inbound connections, restricted to the trainer's saved public IPv4 /32. Use Systems Manager for administration. The UI uses HTTP.

## Configure AWS and GitHub

1. Use a dedicated AWS sandbox in `ap-south-1`. Apply [github-oidc.yaml](github-oidc.yaml) as the bootstrap administrator. Set `GitHubSubject` to the exact OIDC subject of this repository's `aws-lab` environment and `EnableBedrock=false`. Supply the existing GitHub OIDC provider ARN if the account already has one. For an existing bootstrap, preserve its subject and provider parameters by using previous values and update the template to install the stop/resume permissions.
2. Put the OpenAI API key in a same-region Secrets Manager plaintext secret named `nexa-lab-openai`. For direct Claude access, store `nexa-lab-anthropic` as plaintext or as a Secrets Manager key/value object containing exactly one direct Anthropic API key. Enter each value using the secret editor. Only the gateway container receives the provider keys. The host generates the database, reviewer and gateway credentials from a separate stack-owned secret.
3. In GitHub, restrict the `aws-lab` environment to branch `main`. Save the trainer's global IPv4 /32 as environment secret `AWS_UI_ALLOWED_CIDR`. Set these environment variables.

| GitHub environment variable | Value |
|---|---|
| `AWS_REGION` | `ap-south-1` |
| `AWS_GITHUB_ROLE_ARN` | Bootstrap output `GitHubRoleArn` |
| `AWS_CLOUDFORMATION_ROLE_ARN` | Bootstrap output `CloudFormationRoleArn` |
| `AWS_SESSION_BOUNDARY_ARN` | Bootstrap output `BoundaryArn` |
| `OPENAI_API_KEY_SECRET_ARN` | Full ARN of `nexa-lab-openai` |
| `ANTHROPIC_API_KEY_SECRET_ARN` | Optional full ARN of `nexa-lab-anthropic`, supplied when creating the stack |
| `ANTHROPIC_LITELLM_CHAT_MODEL` | Optional `anthropic/` prefix followed by the Claude model ID enabled for the key |
| `CHAT_MODEL` | Application answer alias. Defaults to `nexa-chat-openai`. Choose `nexa-chat-anthropic` to serve Claude answers |
| `OPENAI_LITELLM_CHAT_MODEL`, `OPENAI_LITELLM_JUDGE_MODEL` | Optional upstream OpenAI routes, both default to `openai/gpt-6-luna` |
| `DATADOG_API_KEY_SECRET_ARN`, `DD_SITE`, `DD_LLMOBS_ML_APP` | Needed only when selecting Datadog. Its optional plaintext key secret is named `nexa-lab-datadog` |

For a retained stack originally created without Claude access, update its CloudFormation parameter `AnthropicKeySecretArn` using the existing template and previous values for other parameters. Set the Claude model variable and run **deploy**. Use a change set and check that the EC2 host and volume stay in place.

For an existing bootstrap, run the update from the reviewed release checkout using your sandbox administrator profile. Keep the same repository subject and OIDC provider.

```bash
aws cloudformation update-stack --region ap-south-1 --stack-name nexa-ci-bootstrap \
  --template-body file://infra/aws/github-oidc.yaml --capabilities CAPABILITY_IAM \
  --parameters ParameterKey=GitHubSubject,UsePreviousValue=true \
    ParameterKey=ExistingOidcProviderArn,UsePreviousValue=true \
    ParameterKey=EnableBedrock,ParameterValue=false
aws cloudformation wait stack-update-complete --region ap-south-1 --stack-name nexa-ci-bootstrap
```

## Gateway routes

| Private API path | Model alias | Upstream |
|---|---|---|
| `/v1/chat/completions` | `nexa-chat-openai` | OpenAI chat |
| `/v1/chat/completions` or `/v1/messages` | `nexa-chat-anthropic` | Direct Anthropic Messages |
| `/v1/chat/completions` | `nexa-judge-openai` | Independent OpenAI evaluation judge |
| `/v1/embeddings` | `nexa-embed-openai` | OpenAI text-embedding-3-small, 1,536 dimensions |

The private AWS gateway allows up to 4,096 output tokens for Claude and 2,000 for OpenAI chat, the OpenAI judge and Bedrock chat or judging. Clients can request a smaller limit. Requests above the selected route's limit are rejected before a provider call.

The workflow packages the selected routes in `gateway.yaml`. Calls from FastAPI use the gateway master key on the private Compose network. Provider fallback is disabled. Changing the answer alias preserves the vector index. The AWS deployment always provisions the application-level guardrails sidecar. Local Ollama training uses its own Compose file.

## Running costs

The existing Linux `m7i-flex.large` in Mumbai costs $0.10075 per running hour, and its auto-assigned public IPv4 costs $0.005 per running hour at the November 2026 rates. The encrypted 40 GiB gp3 volume costs about $3.65 per month while retained. Secrets Manager, ECR, S3, log storage and requests have separate charges. OpenAI and Anthropic bill the selected models independently. Budget tags record a planning allowance. The first validation allowance is $9.

A normal start or resume gets 60 minutes. Choose 120 minutes for a longer session. Stop releases the dynamic public IP. Resume looks up its new address and verifies the saved release. Deploy uses the remaining window. CloudWatch collects container logs with one-day retention. Datadog is optional. [Mumbai price list](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/ap-south-1/index.csv) · [IPv4 pricing](https://aws.amazon.com/vpc/pricing/) · [EC2 stop/start](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Stop_Start.html)

## Optional Bedrock mode — disabled by default

Set `EnableBedrock=true` in the bootstrap, configure `BEDROCK_MODEL_ARNS` for the exact authorized model/profile and destination ARNs including Titan, and set `BEDROCK_CHAT_ROUTE` and `BEDROCK_JUDGE_ROUTE` to approved `bedrock/converse/...` routes. Check model entitlements and quotas in the deployment region. Choose a separate stack name and `model_provider=bedrock` at start. Bedrock uses its instance role, published guardrail and separate Titan 1,024-dimensional namespaces. OpenAI data stays in its original stack.

## Operation and evidence

Follow the [trainer guide](START_USE_DELETE_GUIDE.md) for daily use and the [CI/CD guide](CI_CD_GUIDE.md) for releases and evaluations. [Historical validation](VALIDATION.md) describes earlier disposable stacks. Their original timers still delete their data.
