# Start, use and stop the training application

Complete [AWS and GitHub setup](README.md#configure-aws-and-github) first. In GitHub Actions select **AWS training application**, choose `main`, and enter the same stack name for all operations. The default is `nexa-lab-training`.

| Operation | What happens |
|---|---|
| `start` | Tests a revision, creates a new stack, publishes the tested images, ingests the synthetic register and verifies a live cited answer. An existing stack name is rejected |
| `stop` | Stops EC2, waits for the stopped state, and retains the encrypted volume, feedback, images and reports |
| `resume` | Starts the saved release, checks API and UI readiness, and publishes its current browser link. Each actual restart gets a new 60- or 120-minute window |
| `deploy` | Tests and deploys updated images to a running session; a failed roll-out restores the previous Compose release when available |
| `evaluate` | Runs one paid golden evaluation on a running host and writes its report to the session S3 bucket |
| `capacity` | Reads memory and container statistics on the running host |
| `destroy` | Permanently deletes the session host, database, reports, images, logs and runtime secret. The reusable provider secrets and bootstrap are separate |

For the first live validation, choose `model_provider=openai`, `observability=cloudwatch`, `minutes=60` and `budget=9`. Open the browser link in the run summary from the saved trainer IP. Ask “What is the maximum loan amount for a NexaHome Loan?” with product `NEXA-HL` and an as-of date of 2026-10-01. Check the citation and submit synthetic feedback.

To resume a stopped application from the CLI:

```bash
gh workflow run aws-lab.yaml --ref main -f operation=resume -f session=nexa-lab-training -f minutes=60
```

Read the new run summary for the current URL. Verify an existing feedback ID, the saved release digest, and the corpus counts across a stop/resume test. The private API's `/ready` checks database readiness.

```bash
gh workflow run aws-lab.yaml --ref main -f operation=stop -f session=nexa-lab-training
```

Finish by verifying **stopped** in EC2. Storage charges continue until you destroy the stack. Export any evidence you need before running destroy. Older stacks without a `StopSchedule` output retain their scheduled deletion behavior.
