# Quality evaluation and release checks

Ragas evaluates generated answers against their exact supplied evidence and,
where available, a reference answer. Judge/metric embedding profiles are
independent of the candidate generation profile. Unknown, unavailable and error
states are preserved rather than assigned invented numeric scores.

## Owned configuration

- [gates.json](gates.json): quality/SLO limits; currently marked `placeholder`.
- [datasets/answer.jsonl](datasets/answer.jsonl): frozen answer/status/reference cases.
- [datasets/retrieval.jsonl](datasets/retrieval.jsonl): retrieval reference cases.

The relocation into this package does not change case contents or thresholds.
The live answer service uses this same answer dataset for exact-match references.

## Batch and retrieval evaluation

From the repository root, with private credentials and the selected compatible
corpus prepared:

```bash
uv run --no-sync --env-file .env --env-file app/gateway/ollama.env.example \
  python -m app.evaluation.run \
  --dataset app/evaluation/datasets/answer.jsonl \
  --gates app/evaluation/gates.json --output /tmp/nexaassist-evaluation.json

uv run --no-sync --env-file .env --env-file app/gateway/ollama.env.example \
  python -m app.evaluation.retrieval_eval --k 5 --min-recall 0.85 \
  --dataset app/evaluation/datasets/answer.jsonl --output /tmp/nexaassist-retrieval.json
```

These commands call actual model/Atlas services and can incur costs. Use the same
candidate/corpus profile for ingestion and retrieval. Keep evaluator settings fixed
when comparing candidates; do not describe fallback results as pure-model results.

```bash
uv run --no-sync python -m app.evaluation.compare /tmp/baseline.json /tmp/candidate.json \
  --gates app/evaluation/gates.json

uv run --no-sync python -m app.evaluation.slo_check \
  --base-url http://127.0.0.1:8001 --gates app/evaluation/gates.json
```

A failed check exits nonzero. A missing measurement is not a safety pass. Current
latency, rate-limit and cost counters are process-local; mixed-model pricing is
not inferred from one candidate's static rate.

## Live scores in Phoenix

Use `POST /answer/evaluated`, then publish the saved response and matching headers
with `python -m app.evaluation.phoenix_export`. The
[observability runbook](../observability/README.md) covers exact trace/span identity,
publication retries and metric annotations. Tracing does not compute scores,
create native online evaluators or approve a release.

## Test scope

```bash
RAGAS_DO_NOT_TRACK=true uv run --no-sync python -m pytest -q \
  tests/test_evaluation.py tests/test_live_evaluation.py tests/test_gates.py \
  tests/test_retrieval_eval.py tests/test_sampling.py tests/test_compare.py
```

Controlled providers and local stores verify the harness without live model or
Atlas calls. A real semantic quality release needs fresh measured evidence and
owner-confirmed thresholds.
