# Session_1_syllabus

- Source: `Session_1_syllabus.pptx`
- Total slides: 16

## Slide 1

NEXAASSIST / SESSION 01 / DISCOVER

Discover

Release decisions, ownership and evidence

Session 1 / lifecycle, evaluation and governance

16 slides / offline labs + release review

LLMOps_Syllabus.md / 01, 03, 09, 10, 11 / Platform agnostic controls; NexaAssist worked example

01/16

### Speaker Notes

Define the release contract and identify the evidence required to approve a change. The primary source is LLMOps_Syllabus.md; NexaAssist is the worked example, so the operating controls also apply with other frameworks, stores and vendors. Use 25 minutes for concepts, 20 for architecture, 90 for practicals including a 10-minute break, 25 for the exit review and 20 for recap. The practical block produces an inventory, a gate-validation transcript, a tamper transcript and a release decision; no credentials are needed. Primary syllabus: LLMOps_Syllabus.md sections 01, 03, 09, 10, 11.

## Slide 2

NEXAASSIST / SESSION 01 / DISCOVER

LLMOps controls behavior across releases

Quality and safety need baselines, owners and release gates.

Latency, failures and tokens need measured operating limits.

Every change needs evidence, an approver and a rollback path.

LLMOps_Syllabus.md / 01, 03, 08, 14 / Concept + inspected local implementation; sources in notes

02/16

### Speaker Notes

Use the Friday-to-Monday failure story to identify which artifact changed and who owns it. Evaluate a model candidate on the same task and evaluation scope as the baseline, considering task quality, safety, latency, cost and compatibility. A hosted model can change behavior without an application code change, so retain model/provider metadata and comparison evidence. Today establishes the control contract; endpoint tuning, gateway policies and detailed FinOps are developed in later sessions. Primary syllabus: LLMOps_Syllabus.md sections 01, 03, 08, 14. Supporting lesson: https://www.educative.io/courses/llmops/what-is-llmops-and-why-does-it-exist.

## Slide 3

NEXAASSIST / SESSION 01 / HOW WE REACHED LLMOPS

Lifecycle / inventory before promotion

Record model/provider ID, owner, purpose and approval state.

Benchmark candidates on one frozen dataset and configuration.

Check compatibility; retain a rollback bundle before retirement.

LLMOps_Syllabus.md / 01, 10, 11 / Concept + inspected local implementation; sources in notes

03/16

### Speaker Notes

Build a model inventory row with the configured model/provider identifier, owner, intended task, approval state and evaluation evidence. Read configured values from app/core/config.py rather than inventing a model name; in an offline exercise record unmeasured provider behavior explicitly. Compare baseline and candidate under the same dataset, task, prompt and retrieval scope, and check structured output, tool schema, token limits and embedding compatibility as applicable. A migration plan retains the previous prompt, configuration, corpus and compatible embedding/index/parent stores until rollback is validated; automated promotion and retirement are design work here. Primary syllabus: LLMOps_Syllabus.md sections 01, 10, 11. Supporting lesson: https://www.educative.io/courses/llmops/how-we-reached-llmops.

## Slide 4

NEXAASSIST / SESSION 01 / DISCOVER

Version the release bundle and name its owners

Corpus / data owner

Prompt / prompt owner

Source hashes + chunk/embedding version

Template + parameters + approval record

Evaluation / reviewer

Runtime / service owner

Dataset + rubric + baseline + run ID

Model/provider + configuration version

LLMOps_Syllabus.md / 01, 02, 03, 10, 11 / Concept + inspected local implementation; sources in notes

04/16

### Speaker Notes

Turn the four cells into a release inventory with an owner and immutable identifier for each artifact. The PromptOps record includes template, parameters, test cases, change history and rollback target; a file-backed prompt is not a deployed shared registry. Dataset and rubric versions travel with the evaluation results, and a reviewer records disputed labels rather than editing the set until the candidate passes. Prompt experiments, judge calibration and the full approval workflow are developed in Session 3. Primary syllabus: LLMOps_Syllabus.md sections 01, 02, 03, 10, 11. Supporting lesson: https://www.educative.io/courses/llmops/mlops-to-llmops-what-changes-and-what-stays.

## Slide 5

NEXAASSIST / SESSION 01 / DISCOVER

Four phases / explicit release decisions

Discover

Distill

scope

Permitted data + named owners

Baseline + candidate comparison

quality

Deliver

Deploy

SLO

Monitor + rollback + retirement

Compatibility + SLO evidence

LLMOps_Syllabus.md / 01, 03, 11, 14 / Concept + inspected local implementation; sources in notes

05/16

### Speaker Notes

Use Discover, Distill, Deploy and Deliver as checkpoints for the syllabus lifecycle rather than as an application-building tutorial. Discover records permitted data and owners; Distill compares a candidate with a frozen baseline; Deploy checks compatibility and measured service limits; Deliver watches production and exercises rollback. A valid thresholds file is only configuration validation, and offline fixtures do not approve production quality or capacity. A release reviewer holds a candidate when required evidence or an accountable approver is missing. Primary syllabus: LLMOps_Syllabus.md sections 01, 03, 11, 14. Supporting lesson: https://www.educative.io/courses/llmops/the-4d-framework-discover-distill-deploy-deliver.

## Slide 6

NEXAASSIST / SESSION 01 / C4 LEVEL 1

C4 / system context

[Person] Staff member

[External system]

asks

Calls APIs

Ask policy questions

Model provider

HTTPS

Browser / JSON HTTP

Embeddings + generation

[Software system]

[Person] Reviewer

[External managed store]

Reads/writes

reviews

NexaAssist

Review feedback

MongoDB Atlas

MongoDB

Cited policy explanations

Bearer / JSON HTTP

Knowledge + feedback

[Person] Operator

[External system]

Maintain sources

Datadog

Exports

ingests

Registered-file CLI

Optional APM / LLMObs

ddtrace

White: people · Navy: system in scope · Gray: external systems · Arrows name the initiating call.

LLMOps_Syllabus.md / 10, 15 / Concept + inspected local implementation; sources in notes

06/16

### Speaker Notes

Read the context diagram as a worked example of operational ownership. Staff ask questions, reviewers assess feedback and operators maintain registered sources; assign actual owner names in the worksheet without treating these example roles as confirmed appointments. The provider, database and optional telemetry service are separate dependencies whose access, provenance, retention and failure behavior need review. Translate those responsibilities to any platform while preserving the boundary between end-user authorization and configured corpus filtering. Primary syllabus: LLMOps_Syllabus.md sections 10, 15. Supporting lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

## Slide 7

NEXAASSIST / SESSION 01 / C4 LEVEL 2

C4 / containers and ownership

NexaAssist / application boundary

[External system]

Embeds changed text / HTTPS

[Container] Python CLI

Model provider

Registered ingestion

Embedding / chat APIs

Query/chat

LangChain runs inside

HTTPS

Upserts chunks + parents

Navy: application process

MongoDB

Gray: managed dependency

[Data store] Atlas collections

Vectors + parents

[Container] FastAPI / Python

Plus plain feedback storage

[Container] Streamlit

Requests

Policy API

Staff + reviewer UI

Read/write

Services + LangChain inside

MongoDB

[External system]

JSON HTTP

Render and call the API

Datadog / optional

Traces

LLMOps_Syllabus.md / 04, 10, 12 / Concept + inspected local implementation; sources in notes

07/16

### Speaker Notes

Use this container view to assign a service owner, a data owner and a telemetry owner. LangChain runs inside the Python API and ingestion CLI; the UI calls FastAPI and the database stores child vectors, parent sections and feedback in logical collections. Trace correlation must preserve request and artifact identities across the relevant operations, and telemetry export is conditional on configuration. This is the inspected working copy and does not establish a production deployment, authenticated user-level permissions or live traces. Primary syllabus: LLMOps_Syllabus.md sections 04, 10, 12. Supporting lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

## Slide 8

NEXAASSIST / SESSION 01 / DATA AND REQUEST PATHS

Two paths share one knowledge contract

OFFLINE / INGESTION CLI

Registered sources

Parse → chunk → redact

Atlas knowledge

verify

upsert

Identity, dates and hash

Compare; embed changed text

Child vectors + parent text

ONLINE / API + CHAIN

load evidence

Question + scope

Retrieve → expand

Generate → validate

filter

context

Validate and scrub query

Parents + linked amendments

Cite, clarify or abstain

Shared contract: source hash, policy date, embedding version and recoverable release identity.

LLMOps_Syllabus.md / 01, 04, 12 / Concept + inspected local implementation; sources in notes

08/16

### Speaker Notes

Use the offline and online paths to explain why a corpus or embedding change is also a release change. Record the document register hash, chunking settings, embedding model and dimensions, retrieval settings and prompt version together. A correlated diagnostic record should connect a request to evidence identities and relevant retrieval/model operations without retaining sensitive prompt data by default. These responsibilities are platform agnostic; Atlas and LangChain are the concrete implementation inspected in this example. Primary syllabus: LLMOps_Syllabus.md sections 01, 04, 12. Supporting lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

## Slide 9

NEXAASSIST / SESSION 01 / REQUEST FLOW

One answer / request and failure flow

1 / Validate + quota

2 / Scrub + retrieve

3 / Pack evidence

invoke

supply

Thin FastAPI route

Scope, parents, amendments

No complete evidence? Stop.

Invalid citation: one repair, then abstain.

prompt

6 / Return result

5 / Validate output

4 / Structured draft

return

check

Answer, clarify or abstain

PII + IDs + exact quotes

Model call / strict schema

Numbered boxes show the main path. Early abstention and the bounded repair are explained in notes.

LLMOps_Syllabus.md / 03, 04, 05, 09 / Concept + inspected local implementation; sources in notes

09/16

### Speaker Notes

Ask learners to mark the validation, retrieval, generation and output checks on one request. Missing complete evidence causes abstention, and a bad citation permits one repair before abstention; the app returns buffered JSON, so this diagram does not demonstrate token streaming or TTFT/TPOT measurement. Use the same request identity to relate errors and timing with the prompt/model/retrieval versions, and propose trace sampling, redaction and retention controls as an operations worksheet. Distinguish an empty retrieval result, a schema failure, an unsupported claim and a provider timeout; full production monitoring is developed later. Primary syllabus: LLMOps_Syllabus.md sections 03, 04, 05, 09. Supporting lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

## Slide 10

NEXAASSIST / SESSION 01 / DISCOVER

Governance / three independent checks

Freshness: does indexed evidence match the approved source?

Permission: may this scope access and disclose the content?

Audit: can a reviewer recover versions and the decision?

LLMOps_Syllabus.md / 09, 10, 12 / Concept + inspected local implementation; sources in notes

10/16

### Speaker Notes

Treat freshness, authorization and auditability as independent controls. The source register and checksums establish byte identity, while effective dates, access policies and provider data rules answer different questions. Record the data owner, provider disclosure decision, retention and residency requirements, access-review owner and the evidence required for retirement. Configured metadata filters and redaction help enforce boundaries but are not proof of authenticated per-user authorization or complete sensitive-data detection. Primary syllabus: LLMOps_Syllabus.md sections 09, 10, 12. Supporting lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

## Slide 11

NEXAASSIST / SESSION 01 / EVALUATION OPERATIONS

EvalOps / freeze a trustworthy baseline

Dataset: input + expected_output + context + expected_status

Cases: normal, refusal, date boundary, adversarial

Compare: same dataset, rubric and release identities

Reference checks + a calibrated judge + human review.

Record disagreements; keep candidate tuning apart from the holdout.

LLMOps_Syllabus.md / 03, 05, 11 / Concept + inspected local implementation; sources in notes

11/16

### Speaker Notes

Inspect app/evaluation/datasets/answer.jsonl and identify input, expected_output, context and expected_status. For the worksheet, select a normal case, a refusal case and a date-boundary case and propose one adversarial case; keep the scored holdout fixed rather than adding candidate-specific answers to it. Reference-based correctness uses an expected answer, while reference-free groundedness assesses claims against supplied evidence and still needs a defined rubric. Calibrate an LLM judge against human labels, inspect disagreement and bias, and version the rubric; no judge calls or measured model-quality claims are part of this offline lab. Primary syllabus: LLMOps_Syllabus.md sections 03, 05, 11. Supporting lesson: https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application.

## Slide 12

NEXAASSIST / SESSION 01 / USE-CASE MANIFEST

Practical / validate gates, then decide

Run: python -m training.session1.check_gates app/evaluation/gates.json

In a temporary copy: set faithfulness_min=1.5; expect INVALID.

Valid + status=placeholder means HOLD for production approval.

LLMOps_Syllabus.md / 01, 03, 10, 11 / Offline exercise; observed fixture results

12/16

### Speaker Notes

Allow 15 minutes to run the gate loader against the shipped file and then against a temporary copy containing faithfulness_min set to 1.5. The shipped file is valid with status=placeholder and p95_total_ms_max=2000.0, while the edited copy reports INVALID for faithfulness_min and exits with code 1. Save both transcripts and restore or delete the temporary copy without weakening the class thresholds. Passing schema validation establishes neither achieved metrics nor approved targets, so the worksheet records a production hold pending owner-confirmed gates and measurement. Primary syllabus: LLMOps_Syllabus.md sections 01, 03, 10, 11. Supporting lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

## Slide 13

NEXAASSIST / SESSION 01 / SOURCE INTEGRITY

Code / reject changed source bytes

def _verify_source(path: Path, entry: dict[str, Any]) -> str:

"""Refuse a file whose bytes differ from the register's recorded sha256."""

digest = hashlib.sha256(path.read_bytes()).hexdigest()

if digest != entry["sha256"]:

raise ValueError(f"{entry['doc_id']}: file sha256 does not match the document register")

return str(path)

A source must match the register before parsing or embedding.

LLMOps_Syllabus.md / 09, 10, 12 / Concept + inspected local implementation; sources in notes

13/16

### Speaker Notes

Read the exact _verify_source excerpt and identify the validation boundary before parsing or embedding. The SHA-256 comparison rejects changed bytes against the registered source identity and supports an audit trail. A matching hash does not establish permission, freshness, policy correctness or approval to send text to an external provider. Keep those decisions as separate evidence in the inventory and governance worksheet. Primary syllabus: LLMOps_Syllabus.md sections 09, 10, 12. Supporting lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

## Slide 14

NEXAASSIST / SESSION 01 / OFFLINE PRACTICAL

Practical / prove the source boundary

uv run --no-sync python -m training.showcase --session 1

Predict → run: 8 originals verify; a changed copy is refused.

Submit: document ID, hash error, owner and HOLD decision.

LLMOps_Syllabus.md / 09, 10, 11 / Offline exercise; observed fixture results

14/16

### Speaker Notes

Allow 20 minutes for the tamper lab and ask for a prediction before running the command. The showcase uses a temporary copy: eight original documents verify and a changed file is refused with a document-register hash mismatch. Capture the failing document ID, error and operational response, then explain why the release reviewer holds ingestion rather than changing the expected hash to hide the discrepancy. The expected result tests source integrity only; it is not a live model, database or security-coverage benchmark. Primary syllabus: LLMOps_Syllabus.md sections 09, 10, 11. Supporting lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

## Slide 15

NEXAASSIST / SESSION 01 / RELEASE EVIDENCE

Practical / review a provider change

Complete inventory: prompt/model/config/data versions + owners.

Candidate lacks quality and compatibility evidence → HOLD.

Name approver, rollback bundle, trigger and retirement condition.

LLMOps_Syllabus.md / 01, 02, 03, 10, 11, 14 / Release-review tabletop; no provider switch

15/16

### Speaker Notes

Allow 25 minutes for a release-review tabletop and 20 minutes to finish the inventory and baseline worksheet, with a 10-minute break completing the 90-minute practical block. Scenario: a provider/model change has passed schema validation but has no comparable golden-set results, compatibility report or owner approval. The expected decision is HOLD; list the missing checks, decide who can approve, and retain the old prompt, model/configuration and compatible corpus, embeddings, index and parent collections. Describe a rollback validation and retirement condition without claiming that CI, canary deployment, automatic promotion or a real provider switch was executed. Primary syllabus: LLMOps_Syllabus.md sections 01, 02, 03, 10, 11, 14. Supporting lesson: https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application.

## Slide 16

NEXAASSIST / SESSION 01 / EXIT GATE

Session 1 / release-readiness exit gate

Hand in: inventory, baseline cases and two failure transcripts.

Defend: owner, evidence, HOLD or promote, rollback target.

Pass the exercise; keep unmeasured production gates open.

LLMOps_Syllabus.md / 01, 03, 10, 11, 14 / Learning gate; production evidence remains open

16/16

### Speaker Notes

Use the 25-minute gate review to assess the submitted inventory, baseline worksheet, gate-validation transcript and source-tamper transcript. Ask each pair to defend its HOLD decision for the provider-change case and identify the owner and missing evidence that could change it. Require a recoverable rollback bundle rather than only a source-code revision. Distinguish passing this learning exercise from production approval, then use the recap to connect release controls to Session 2 RAGOps. Primary syllabus: LLMOps_Syllabus.md sections 01, 03, 10, 11, 14.
