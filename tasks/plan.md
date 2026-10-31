# Session 2 implementation plan

The user approved the capability map and model-access specification, then explicitly
requested code implementation on 24 October 2026. That instruction authorizes this
plan and its execution without another planning-only approval turn.

## Sequence

1. Model access: explicit endpoint/API mode/credentials, independent judge and metric
   embedding profiles; offline HTTP contract tests before factory changes.
2. Embedding integrity: validate vectors and reject incompatible corpus/parent
   identities in the database boundary before embedding or mutations. Preserve the
   matching legacy OpenAI corpus; document separate local index JSON.
3. Gateway: use LiteLLM through the shared model client; bounded fallback and
   balancing configuration, isolated opt-in cache, observed-model provenance and
   conservative costs. No second Python router.
4. Security: preserve existing rails, scrub batch evaluation, connect an optional
   Guardrails AI validation process that fails closed when configured. Guardrails AI
   currently requires Python <3.14, so it runs separately from the Python 3.14 app.
5. Evals and delivery: hold judge/metric embeddings fixed across candidates, retain
   exact contexts and Phoenix evaluation links, run focused/full offline checks,
   document commands and create the requested immutable handoff.

Each step starts with failing tests and remains within the existing layers. Pure
simplification follows covered behavior and does not change unrelated code.

## Verification

Use `.venv/bin/python -m pytest` with HTTP mock transports and fake Mongo stores.
Run the new tests, affected existing tests, `.venv/bin/ruff check .`,
`.venv/bin/mypy .`, then `.venv/bin/python -m pytest -q tests`. Report the known
missing architecture HTML failure separately. Keep CONSTRAINTS.md and evaluation
thresholds unchanged. Model downloads, Atlas writes and cloud calls are excluded
from offline verification; report any live evidence separately.

## Risks

- Reusing embedding stores can replace incompatible vectors: reject before use.
- Candidate credentials can leak to a custom endpoint: require explicit keys.
- Gateway aliases obscure responding models and costs: preserve unknown values.
- Sidecar outage must not bypass configured output validation.
- Local cache is a classroom single-worker capability, not a production shared cache.
