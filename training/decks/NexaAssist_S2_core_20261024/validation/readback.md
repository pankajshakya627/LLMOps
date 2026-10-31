# Session_2_core

- Source: `Session_2_core.pptx`
- Total slides: 19

## Slide 1

NEXAASSIST / SESSION 02 / SESSION OUTCOMES

LLMOps Core

Observability, Evaluation & Security

Ollama + OpenAI / retain the RAGOps foundation

19 slides / tools, failure drills and evidence

Syllabus 03, 04, 05, 07, 09, 12 / Offline controls + optional live tools; full steps in handout

01/19

### Speaker Notes

This Session 2 extends the earlier RAGOps material with observability, evaluation, gateways and security, as requested. Nineteen slides support a three-hour class with a 90-minute practical block; optional live services are prepared before class. Required offline exercises reuse the existing project controls, while the live guide adds Datadog, Ragas, LiteLLM, Ollama/OpenAI and Guardrails AI work without claiming a production deployment. Primary syllabus: LLMOps_Syllabus.md sections 03, 04, 05, 07, 09, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 2

NEXAASSIST / SESSION 02 / TOPICS AND PRACTICALS

Four operating questions / one evidence pack

Observe / Datadog; Phoenix alternative

Where did latency, token usage or the chain failure originate?

Evaluate / Ragas; DeepEval alternative

Are claims supported, required contexts present and regressions gated?

Route / LiteLLM; Portkey alternative

Which backend ran, when did fallback occur and was the cache valid?

Protect / Guardrails AI; NeMo alternative

Were PII, injection attempts and invalid outputs handled correctly?

Syllabus 03, 04, 07, 09, 12 / Fixtures and live exercises labeled / sources and lab steps in notes

02/19

### Speaker Notes

The practical block allocates 15 minutes each to RAGOps, observability and evaluation, 20 to gateway routing, 15 to security and 10 to a break. Keep the same synthetic policy cases across the four disciplines and submit traces, evaluation decisions, a routing/cache matrix and guardrail outcomes. The listed alternatives explain transferable concepts; installing every framework is not required. Datadog, Ragas, LiteLLM and Guardrails AI are the main worked tools. Primary syllabus: LLMOps_Syllabus.md sections 03, 04, 07, 09, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 3

NEXAASSIST / SESSION 02 / EXISTING FOUNDATION

RAGOps recap / publish verifiable evidence

1 / Verify register

2 / Parse layout

3 / Chunk clauses

load

split

Authority + source SHA-256

Headings, text and tables

Stable IDs + parent links

protect

write

check

6 / Upsert stores

5 / Compare + embed

4 / Redact + hash

Child vectors + parent text

Changed children only

Before embedding disclosure

Capture per-document outcome and changed counts; redaction precedes provider disclosure.

Syllabus 04, 09, 12 / Fixtures and live exercises labeled / sources and lab steps in notes

03/19

### Speaker Notes

Retain the existing verify, parse, chunk, redact, compare/embed and upsert sequence. Record source hashes, policy and embedding versions, changed/unchanged counts, parent scope and per-document failure outcomes before treating the corpus as ready. A successful ingestion log does not prove a queryable index or live retrieval quality. Complete parent sections remain unembedded, and freshness reconciliation needs a source-versus-stored manifest. Primary syllabus: LLMOps_Syllabus.md sections 04, 09, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md. Supporting lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

## Slide 4

NEXAASSIST / SESSION 02 / RAGOPS LAB / OFFLINE

Practical / chunking and repeat ingestion

python -m training.session2.chunks

python -m training.session2.ingest_twin

chunk candidates 300 / 1200 / 5000 → 40 / 32 / 32

embedded counts across four runs → 32 / 0 / 32 / 0

Submit: preserved table, child/checksum/parent IDs and a version-change explanation.

Syllabus 01, 03, 08, 12 / Fixtures and live exercises labeled / sources and lab steps in notes

04/19

### Speaker Notes

Use the 15-minute RAGOps block for a compact chunk/ingestion comparison, then retain the longer exercises as extensions. Expect 40, 32 and 32 chunks for the three settings and embedding counts 32, zero, 32 and zero across the four-run fixture. Inspect one complete table and a scope-compatible parent rather than selecting a chunker from counts alone. The real PDF and chain are used with fake embeddings and memory stores; model-name invalidation is not a live embedding migration. Primary syllabus: LLMOps_Syllabus.md sections 01, 03, 08, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md. Supporting lesson: https://www.educative.io/courses/llmops/data-foundations-for-llmops.

## Slide 5

NEXAASSIST / SESSION 02 / EXISTING FOUNDATION

Retrieve scoped and complete evidence

1 / Request + filters

2 / Candidate search

3 / Rank + top_k

search

rank

Scrub query; constrain corpus

Query embedding + Atlas

Reranker when enabled

Dates, product, access scope

Dense or configured hybrid

Keep the requested hit count

expand

pack

link

6 / Pack context

5 / Load amendments

4 / Expand parents

Preserve complete evidence

Scoped linked instruments

Validate matching scope

Then hand off to generation

Separate from top_k results

Otherwise retain child text

Numbered path: baseline retrieval. Hybrid search and reranking are explicit configuration branches.

Syllabus 03, 04, 09, 12 / Fixtures and live exercises labeled / sources and lab steps in notes

05/19

### Speaker Notes

Keep date, institution, product and access filters ahead of evidence use, with optional ranking followed by parent and complete-amendment expansion. Lookup date and sanction applicability are different; a fee quote without the circular applicability can mislead. The project scorer includes complete linked amendments alongside the requested top-k child hits, so document its reference-coverage convention. Preserve original child/parent, embedding compatibility and rollback-bundle lessons in the handout; configured corpus filtering does not establish authenticated per-user authorization. Primary syllabus: LLMOps_Syllabus.md sections 03, 04, 09, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 6

NEXAASSIST / SESSION 02 / RAGOPS LAB / OFFLINE

Practical / keep the policy regression baseline

python -m training.showcase --session 2

python -m training.session2.recall

June 0.35% → July 0.30%; wrong product abstains

one of two references → recall 0.5; rank 4 → RR 0.25

Retain dates, product, complete conditions and citation IDs as regression evidence.

Syllabus 03, 05, 09, 12 / Fixtures and live exercises labeled / sources and lab steps in notes

06/19

### Speaker Notes

Use the existing July-amendment showcase and recall script as pre-reading or as part of the RAGOps recap. Record lookup and sanction dates, product, status and citations; retain the synthetic fee minima, maxima and GST caveat from the complete evidence. A wrong-product case must abstain, one of two required references gives recall 0.5 and a first included hit at rank four gives reciprocal rank 0.25. These are controlled fixture observations; NDCG and migration/freshness incident worksheets remain supporting exercises in the handout. Primary syllabus: LLMOps_Syllabus.md sections 03, 05, 09, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 7

NEXAASSIST / SESSION 02 / OBSERVABILITY AND TRACING

Observability / follow one request across stages

Request / workflow

Validate + retrieve

Build prompt

Request ID + parent links

Scope + embedding/search

Version + context budget

Prompt/model/corpus versions

Parents + amendments

Redact captured fields

Return / score

Validate output

Model / gateway

Status + evidence + eval ID

Schema + citations + PII

Backend + attempts + tokens

Correlate errors and feedback

Bound repair attempts

Latency + failure metadata

Reference trace map: arrows show request order; inspect which spans actually exist.

Syllabus 04, 12, 14 / Fixtures and live exercises labeled / sources and lab steps in notes

07/19

### Speaker Notes

A trace joins the request workflow to retrieval, model and validation work; use IDs and parent links to distinguish a slow model from a retrieval or output failure. Datadog is the existing project telemetry implementation, while Phoenix provides an OpenTelemetry/OpenInference alternative in a separate lab. The gateway node is a classroom extension, not a claim that the current application factories already call LiteLLM. Sources: app/core/observability.py, tests/test_telemetry.py, https://docs.datadoghq.com/llm_observability/quickstart/ and https://arize.com/docs/phoenix/learn/tracing/how-tracing-works. Primary syllabus: LLMOps_Syllabus.md sections 04, 12, 14; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 8

NEXAASSIST / SESSION 02 / OBSERVABILITY SIGNALS

Measure latency, usage and failure signals

Latency

Stage duration + request p50/p95/p99; TTFT/TPOT need token timestamps.

Usage and cost

Input/output/cached tokens, actual model/backend and measured unit cost.

Failure taxonomy

Timeout / rate limit / retrieval miss / schema error / invalid citation.

Capture policy

Redact before export; define sampling, retention and review ownership.

Syllabus 04, 05, 08, 14 / Fixtures and live exercises labeled / sources and lab steps in notes

08/19

### Speaker Notes

Measure request and stage durations, and compute percentiles over repeated observations rather than a single trace. Track input, output and cached-token fields when the provider reports them, plus the selected model and retry/fallback attempts; local inference still consumes hardware resources. The current answer endpoint is buffered JSON, so TTFT and TPOT remain unmeasured without streaming instrumentation. Model errors, missing evidence and unsafe/invalid output have different operational owners, and query redaction alone does not prove all automatically captured trace fields are sanitized. Primary syllabus: LLMOps_Syllabus.md sections 04, 05, 08, 14; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 9

NEXAASSIST / SESSION 02 / OBSERVABILITY LAB

Practical / inspect a correlated Datadog trace

uv run --no-sync pytest -q tests/test_telemetry.py

Offline: captured spans + fake HTTP + scoped prompt metadata

Live: ddtrace-run + existing Datadog Agent configuration

Locate root → child spans; explain the slow or failing stage

Submit: trace/parent identity, durations, token fields, failure and capture-policy gaps.

Syllabus 04, 05, 14 / Fixtures and live exercises labeled / sources and lab steps in notes

09/19

### Speaker Notes

Allow 15 minutes to run and inspect the existing telemetry tests, which capture spans locally and mock external responses without exporting to Datadog. Identify the HTTP 422 failure, root/parent relationships, prompt version and model token usage in the test assertions. The live guide starts the existing Agent configuration and instrumented API for an instructor-prepared synthetic request; capture an observed trace only when those services are available. Mark missing spans and token-stream timings as gaps rather than reporting success; the Phoenix alternative is documented separately in training/session2/live_practicals.md. Primary syllabus: LLMOps_Syllabus.md sections 04, 05, 14; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 10

NEXAASSIST / SESSION 02 / EVALUATION OPERATIONS

EvalOps / build the evaluation harness

Freeze cases

Run candidate

Capture evidence

Input + expected output

Version prompt and model

Response + retrieved text

Context + expected status

Retain actual backend ID

Case/run identifiers

Human decision

Apply gates

Score / judge

Review disagreements

Per-case + aggregate checks

Ragas or DeepEval

Promote / hold / rollback

Regressions stay visible

Rubric + judge version

Evaluation flow: keep the dataset, reference, judge and experimental scope comparable.

Syllabus 02, 03, 05, 11 / Fixtures and live exercises labeled / sources and lab steps in notes

10/19

### Speaker Notes

The harness freezes cases, runs a versioned candidate, captures contexts and answers, scores them, applies gates and records a human decision. Reuse app/evaluation/run.py and its RagasScorer adapter rather than inventing a second production evaluator. Include normal, refusal, date-boundary, adversarial and missing-evidence cases; preserve the holdout and case identities across comparisons. Judges are stochastic and require human-label calibration, bias review and an explicit rubric before automatic scores justify release decisions. Primary syllabus: LLMOps_Syllabus.md sections 02, 03, 05, 11; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 11

NEXAASSIST / SESSION 02 / LLM-AS-A-JUDGE METRICS

Evals / separate coverage from supported claims

Faithfulness

Are the answer claims supported by the supplied retrieved context?

Context recall

Does retrieved evidence cover the claims required by the reference?

Correctness / relevance

Is the answer right for the task, and does it answer the question?

Calibration and release

Compare human labels; inspect bias, disagreement and failing cases.

Syllabus 03, 05, 12 / Fixtures and live exercises labeled / sources and lab steps in notes

11/19

### Speaker Notes

Ragas faithfulness assesses support for response claims, while context recall uses reference information to assess missing evidence; neither is the same as the repository reference-ID recall at k. Correctness, relevance and safety require separate criteria, and high faithfulness does not prove that the supplied source is true. Treat one minus faithfulness only as an unsupported-claim proxy, not a calibrated probability that an entire response hallucinated. Sources: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/ and https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/; DeepEval is an alternative framework rather than another installed scoring pipeline. Primary syllabus: LLMOps_Syllabus.md sections 03, 05, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 12

NEXAASSIST / SESSION 02 / EVALS LAB

Practical / score candidates and enforce gates

python -m training.session3.gates

Fixture: healthy PASS; retrieval / generation faults FAIL

Live Ragas: compare Qwen chat with the OpenAI chat alias

Freeze contexts + reference + judge + metric embeddings

Submit: per-case scores, judge/rubric identity, failure class and HOLD/PASS rationale.

Syllabus 03, 05, 11, 12 / Fixtures and live exercises labeled / sources and lab steps in notes

12/19

### Speaker Notes

Allow 15 minutes for the existing offline gate scenarios: healthy passes, retrieval miss fails as retrieval_error and generation fault fails as generation_error. Those scores are explicitly synthetic and do not call an LLM judge. The live guide supplies a small Ragas harness comparing local Qwen and OpenAI generation under the same contexts, reference and OpenAI judge, with OpenAI metric embeddings held fixed. Record the backend actually selected, disable fallback for a pure local benchmark and separate generation comparison from a Qwen/OpenAI embedding-index experiment. Primary syllabus: LLMOps_Syllabus.md sections 03, 05, 11, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 13

NEXAASSIST / SESSION 02 / GATEWAYS AND ROUTING

Gateway / Ollama and OpenAI behind stable aliases

Ollama / local chat

route

qwen3.5:9b-mlx

Lab caller

LiteLLM gateway

Stable chat alias

nexa-chat

on failure

OpenAI / chat fallback

Approved model ID from env

Embeddings: qwen3-embedding:0.6b | OpenAI text-embedding-3-small

Chat can fail over; embedding families need separate compatible corpora and indexes.

Syllabus 07, 08, 09, 12, 14 / Fixtures and live exercises labeled / sources and lab steps in notes

13/19

### Speaker Notes

Use LiteLLM as the worked gateway and Portkey as a conceptual alternative. The four aliases are nexa-chat for Ollama qwen3.5:9b-mlx, nexa-chat-openai for an instructor-selected OpenAI model, nexa-embed-local for qwen3-embedding:0.6b and nexa-embed-openai for text-embedding-3-small. Chat fallback is conditional on compatible output contracts and permitted disclosure; different embedding spaces require separately embedded corpora and compatible query/index settings, even if vector lengths match. Sources: app/gateway/litellm.yaml, https://ollama.com/library/qwen3.5:9b-mlx, https://ollama.com/library/qwen3-embedding and https://docs.ollama.com/api/openai-compatibility. Primary syllabus: LLMOps_Syllabus.md sections 07, 08, 09, 12, 14; full practicals: training/session2/handout.md and training/session2/live_practicals.md. Supporting lesson: https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation.

## Slide 14

NEXAASSIST / SESSION 02 / GATEWAY CONFIGURATION

LiteLLM / explicit routing and bounded failure

local chat: ollama_chat/qwen3.5:9b-mlx

local embed: openai/qwen3-embedding:0.6b [local /v1]

router_settings:

num_retries: 1

timeout: 30

fallbacks: [{nexa-chat: [nexa-chat-openai]}]

routing_strategy: simple-shuffle

Full four-alias YAML in app/gateway/litellm.yaml; OpenAI ID/key come from env.

Syllabus 07, 08, 09, 14 / Fixtures and live exercises labeled / sources and lab steps in notes

14/19

### Speaker Notes

Read the supplied classroom YAML: one retry, a timeout, an explicit chat fallback and the routing strategy are visible configuration. OpenAI chat model identity is selected through OPENAI_LITELLM_CHAT_MODEL with its provider prefix, and keys remain in environment variables rather than the presentation or YAML. The Ollama embedding alias uses the documented local OpenAI-compatible endpoint, with no fallback to a different embedding family. Sources: https://docs.litellm.ai/docs/proxy/configs and https://docs.litellm.ai/docs/proxy/reliability; a timeout setting alone does not establish measured end-to-end recovery time. Primary syllabus: LLMOps_Syllabus.md sections 07, 08, 09, 14; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 15

NEXAASSIST / SESSION 02 / GATEWAY LAB

Practical / fail over, balance and cache

Fail over

In a temp config, break one chat URL; record attempts and actual fallback.

Balance

Use two healthy deployments under one alias; count uncached requests.

Cache

Repeat identical synthetic input; confirm a hit from upstream-call evidence.

Invalidate

Change prompt/corpus/scope version; require a fresh result or disable caching.

Syllabus 07, 08, 09, 14 / Fixtures and live exercises labeled / sources and lab steps in notes

15/19

### Speaker Notes

Allow 20 minutes to audit the route/failure matrix offline or run it on instructor-prepared services using training/session2/live_practicals.md. Inject failure only in a temporary gateway config by pointing a backend at an unreachable localhost port; test local-to-OpenAI, the reverse map in a separate config, and exhaustion without circular fallbacks. Demonstrate balancing only with two independent healthy endpoints, and verify cache hits with gateway/upstream evidence rather than latency alone. The lab cache is in memory for one worker, cache isolation must include relevant scope/version semantics before sensitive use, and the deprecated proxy mock_testing_fallbacks flag is not used; sources are the LiteLLM fallback, load-balancing and caching documentation linked in the live guide. Primary syllabus: LLMOps_Syllabus.md sections 07, 08, 09, 14; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 16

NEXAASSIST / SESSION 02 / SECURITY AND GUARDRAILS

Guardrails / validate at each trust boundary

Input / redaction

Prompt boundary

Evidence access

Mask recognized PII

Separate trusted instructions

Date/product/access filters

Validate scope and limits

Treat retrieved text as data

Least-privilege tools

Return / audit

Output checks

Model / gateway

Safe answer or abstention

Strict schema + PII scan

Authorized route + budgets

Redacted failure evidence

Exact evidence/citation checks

Bound retries and repairs

Defense in depth: each check has a distinct purpose; a schema alone cannot prove truth.

Syllabus 07, 09, 10, 12 / Fixtures and live exercises labeled / sources and lab steps in notes

16/19

### Speaker Notes

Keep PII redaction before embedding, model disclosure and trace export, with access checks before evidence use and strict output validation afterwards. Prompt boundaries help preserve instruction/data separation, but malicious instructions inside legitimate prose still need adversarial behavioral tests and constrained tools. Guardrails AI can wrap the existing Pydantic contract, while a NeMo Guardrails policy is an alternative integration with its own evaluation and operational cost. No framework name establishes complete injection defense or authentication; the slide describes control responsibilities and the handout identifies implemented versus additional integrations. Primary syllabus: LLMOps_Syllabus.md sections 07, 09, 10, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 17

NEXAASSIST / SESSION 02 / SECURITY LAB / OFFLINE

Practical / PII and prompt injection defenses

python -m training.session2.redact

python -m training.session3.prompt_boundaries

Recognized PII → typed placeholders before disclosure

Injected XML tags remain data; trusted system role retained

Submit: benign/adversarial cases, expected vs observed behavior and coverage gaps.

Syllabus 03, 09, 10, 12 / Fixtures and live exercises labeled / sources and lab steps in notes

17/19

### Speaker Notes

Use part of the 15-minute security block for the existing redaction and prompt-boundary exercises. Recognized email, phone, PAN and Aadhaar patterns are masked, while policy amounts remain unchanged; learners should identify both missed identifiers and false positives. The actual rendered production prompt escapes injected XML and retains the system role, proving a syntax boundary rather than semantic injection immunity. Add direct and retrieved-document injection cases to the behavioral evaluation matrix and retain least-privilege, authorization and data-disclosure decisions as separate controls. Primary syllabus: LLMOps_Syllabus.md sections 03, 09, 10, 12; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 18

NEXAASSIST / SESSION 02 / OUTPUT VALIDATION LAB

Practical / strict output with Guardrails AI

from guardrails import Guard

from app.models.answer import AnswerDraft

guard = Guard.for_pydantic(output_class=AnswerDraft)

outcome = guard.parse(llm_output=raw_json, num_reasks=0)

assert outcome.validation_passed

python -m training.session3.answers # offline app rails

Reject bad status/schema; separately reject output PII and invented source quotes.

Syllabus 03, 09, 11 / Fixtures and live exercises labeled / sources and lab steps in notes

18/19

### Speaker Notes

Complete the security block with the existing offline answer-control lab: a valid answer is accepted, an invented quotation receives one repair then abstention, and output PII causes abstention. The optional Guardrails AI extension parses known JSON against the existing AnswerDraft model without a model call and checks a valid status against an invalid approve_loan status. Guardrails AI is not installed in the application environment, and the framework snippet is a documented exercise rather than a measured integration; schema acceptance does not replace citation, PII or semantic checks. Source: https://github.com/guardrails-ai/guardrails/blob/main/guardrails/guard.py; NeMo Guardrails remains a named alternative, not an implemented application dependency. Primary syllabus: LLMOps_Syllabus.md sections 03, 09, 11; full practicals: training/session2/handout.md and training/session2/live_practicals.md.

## Slide 19

NEXAASSIST / SESSION 02 / EVIDENCE AND NEXT STEPS

Session 2 / operating-readiness exit gate

RAGOps + trace pack

Versioned evidence, policy regressions, parent IDs and observed stage signals.

Evaluation pack

Fixed cases, metric/judge IDs, failures and a defended release decision.

Routing + security pack

Actual backends, fallback/cache matrix, negative cases and remaining gaps.

Syllabus 03, 04, 05, 07, 08, 09, 11, 12, 14 / Fixtures and live exercises labeled / sources and lab steps in notes

19/19

### Speaker Notes

Use the exit review to inspect the RAGOps baseline and the trace, evaluation, gateway and guardrail evidence packs. Record which observations came from offline fixtures, which were actually measured live and which remain not_measured. Passing the class exercise does not approve placeholder production thresholds or prove a deployed gateway/guardrail integration. Continue in Session 3 with deeper prompt lifecycle, judge calibration, answer-quality regression and human review. Primary syllabus: LLMOps_Syllabus.md sections 03, 04, 05, 07, 08, 09, 11, 12, 14; full practicals: training/session2/handout.md and training/session2/live_practicals.md.
