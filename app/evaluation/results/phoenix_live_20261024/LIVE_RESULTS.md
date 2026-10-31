# Live FastAPI / Phoenix run — 24 October 2026

All policy data in this run is synthetic. These are observed live results, not
fixture scores. The candidate was rejected; the run does not establish release
readiness or a reliable local answer for the baseline question.

## Services available

- Verified API with the retained baseline and Guardrails enabled:
  `http://127.0.0.1:8001/docs`.
- Phoenix: `http://127.0.0.1:6006`, project `nexaassist-training`.
- Live Guardrails validator: `http://127.0.0.1:8101/docs`.
- The user's original API on port 8000 was not restarted. It needs a restart
  with the updated local profile to load the no-thinking configuration.

## Retrieval and bounded generation

The manually created `policy_qwen3_v1` index is READY and queryable on
`nexaassist.policy_chunks_qwen3_v1`. The corpus contains 177 stored 1024-dimensional
vectors. The maximum-loan question returned 20 ranked hits and one complete
amendment. The top hit is POL-HL-V3 clause 4.1.

The initial answer failed with `LengthFinishReasonError`: thinking consumed the
2,000-token completion budget before structured output was available. Phoenix
recorded the error in trace `29643d148dbc8dbdd7e4505684512632`.

Ollama 0.40.10 reported thinking values `[false, true]`, default `true`.
A short live `reasoning_effort: none` probe returned READY with one completion
token and no reasoning output. The local profile now disables thinking while
retaining the 2,000-token cap. Independent judge settings clear that candidate
control. Gateway configs apply it only to local chat deployments.

## Baseline and candidate evaluation

Same question, date, product, top_k=20, Qwen corpus, no-thinking mode and judge
settings were used. The candidate additionally changed citation-format wording.
Each candidate was evaluated once; scores are stochastic and not calibrated.

| Measurement | Baseline 1.1.0 | Citation candidate 1.1.1 |
|---|---|---|
| Answer status | insufficient_evidence | answered |
| Faithfulness | unavailable: abstained | **0.0** |
| Answer relevancy | unavailable: abstained | 0.9958213525224018 |
| Context precision | 0.09999999999 | 0.09999999999 |
| Context recall | 1.0 | 1.0 |
| Evaluated request elapsed | 39.74 s | 47.87 s |
| Trace ID | b0f853dd11adc99fb21110d323255908 | 9f6bc0bcd31a56f8258efa4078a3c12a |
| HTTP server span ID | 577d64549bb16e08 | 27c80de8f1eddab8 |

Baseline Qwen drafts used invalid marker syntax and/or unsupported quotes. The
application preserved exact-citation checks, allowed its bounded repair and
abstained. No thresholds or validators were relaxed.

Candidate 1.1.1 added explicit numeric-marker examples and instructed verbatim
short/table-cell quotes. It passed structural and citation validation but wrote
`₹7,50,00,00` in its answer while quoting `₹7,50,00,000` correctly. Ragas detected
that unsupported numerical claim and returned faithfulness 0.0. High answer
relevancy did not establish factual faithfulness.

**Decision:** candidate rejected. The local prompt source and version/hash pins
were restored to baseline 1.1.0 / dca0041f402b, and the isolated API was restarted
with that baseline. Candidate 1.1.1 remains a Phoenix snapshot, not the active
application default.

## Phoenix evidence

The four Ragas annotations were published and read back from Phoenix for both
HTTP server spans. The candidate also has:

- `app_prompt_version`: 1.1.1, with its SHA and registry-version ID in metadata.
- `guardrails_output_schema`: passed.
- `quality_decision`: rejected, with the numerical-error explanation.

Inspect the HTTP server span, rather than only its child model span. These are
imported span annotations; no native Phoenix dataset evaluator was created.

Phoenix Prompts contains `nexaassist-policy-answer` with:

| Registry version ID | Snapshot | Tag / status |
|---|---|---|
| UHJvbXB0VmVyc2lvbjox | Actual baseline source 1.1.0 | code-1-1-0-dca0041f402b |
| UHJvbXB0VmVyc2lvbjoy | Wording-only classroom variation | candidate-1-1-0-dca0041f402b; not evaluated/deployed |
| UHJvbXB0VmVyc2lvbjoz | Actual citation candidate source 1.1.1 | code-1-1-1-894fb2a14591; rejected-20261024 |

Prompt tags use hyphens rather than periods because the live server rejected the
initial dotted tag name. The application still consumes its local LangChain
prompt; registry snapshots do not automatically deploy a prompt version.

## Guardrails

Six direct endpoint checks produced the expected decisions:

- Valid draft accepted.
- Invalid status, unknown field, negative evidence ID and malformed JSON rejected.
- Invalid outer request shape returned HTTP 422.

A seventh check submitted the actual numerically incorrect candidate draft to
`POST /validate`: its schema was valid and validation passed. This is expected
schema-validator behavior, not a factual-quality pass. The same draft's Ragas
faithfulness score was 0.0. The API on port 8001 was configured to invoke this
live validator during generation.

## Code and checks

The retained fix adds `CHAT_REASONING_EFFORT=none` to the direct local profile,
clears it for independently configured judges and gateway clients, and applies
the local deployment policy inside LiteLLM. Cache identity includes the setting.
New offline tests cover payload propagation, the retained cap, judge isolation,
empty override clearing and deployment-specific routing policy.

- Full offline suite: 269 passed.
- Ruff and mypy passed; mypy checked 138 source files.
- After candidate rollback, focused prompt/answer/evaluation/telemetry checks
  were rerun. The existing prompt pins retain their baseline values.
- CONSTRAINTS.md and evaluation thresholds were not weakened.
- No merge, production promotion or full ten-case release evaluation was done.

Machine-readable details: [SUMMARY.json](SUMMARY.json),
[candidate response](candidate_evaluated.json), [baseline response](evaluated.json),
[Guardrails outcomes](guardrails.json), [index state](indexes.json).

## OpenAI comparison using `.env`

The separate API on port 8002 loaded the configured `gpt-6-luna` candidate and
`gpt-6.1-sol` evaluator from `.env`. The fallback overlay preserved Qwen
1024-dimension embeddings, the existing Qwen corpus, the 2000-token generation
cap and baseline prompt 1.1.0. Ollama remains the primary profile on port 8001.
The Guardrails service on port 8101 remained enabled.

The same maximum-loan question returned HTTP 200 with status `answered`:
“The maximum NexaHome Loan amount is ₹7,50,00,000. [2]” The exact citation was
“Maximum loan amount is ₹7,50,00,000.” from POL-HL-V3 clause 4.1.

| Metric | Observed score |
|---|---|
| Faithfulness | 1.0 |
| Answer relevancy | 0.9583873236833522 |
| Context precision | 0.09999999999 |
| Context recall | 1.0 |

End-to-end evaluation took 33.45 seconds; generation took 3116.3 ms. The
exporter published all four scores to span `3357d048e66b4b4a`, trace
`756fdfb478fbd0dad1fe9915c7987133`. See
[response](openai_evaluated.json) and [headers](openai_evaluated.headers).

This was an explicit cloud comparison, not automatic quality-triggered routing.
The low context precision remains unresolved. Safari inspection was unavailable:
the Computer runtime returned `Trusted RPC service is not configured: sky`.
The HTTP API and Phoenix were checked directly instead. Configuration assertions
verified credential resolution and identical retrieval/evaluator settings; no
application logic changed and the full offline suite was not rerun for this
configuration/documentation change.
