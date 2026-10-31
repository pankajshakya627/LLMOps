# Session 1 - Discover: why LLMOps, the architecture, and "are we allowed to build?"

_Student handout. Lab scripts are in `training/session1/`. No credentials are needed._

## Syllabus delivery — required practical block (90 minutes)

Use this block with the revised 16-slide PPT. It follows [LLMOps_Syllabus.md](../../LLMOps_Syllabus.md) sections 01–03 and 09–11, with reliability/rollback introduced. The older exercises below are supplementary; the service-start and live-readiness exercise is outside this required offline block. Run commands from the project root in the existing environment.

| Time | Practical | Expected evidence |
|---:|---|---|
| 20 min | Inventory and baseline | Four owned artifact records and four proposed evaluation cases |
| 15 min | Gate configuration validation | Valid-placeholder output and a rejected out-of-range field |
| 20 min | Source tamper | Registered document ID, exact error and HOLD decision |
| 10 min | Break | |
| 25 min | Provider-change release review | Missing checks, approver, rollback target and retirement condition |

**1. Inventory and baseline.** Read `app/core/config.py`, `app/chains/prompts/answer.py`, `nexa_synthetic_data/document_register.json`, `app/evaluation/datasets/answer.jsonl` and `app/evaluation/gates.json`. Record existing identifiers rather than inventing a model or provider. Use this worksheet in your own notes:

| Artifact | Identifier/version or hash | Owner to confirm | Approval state | Evidence / rollback target |
|---|---|---|---|---|
| Model/provider and runtime configuration | | | | |
| Prompt template and parameters | | | | |
| Corpus, chunks, embeddings, child/parent stores | | | | |
| Dataset, rubric and evaluation run | | | | |

Select one ordinary answer case, one refusal case and one policy-date case from the golden dataset. Propose one adversarial case separately, with expected behavior, required evidence and a human reviewer. Keep a frozen holdout apart from candidate tuning. Explain which checks compare to a reference answer and which assess evidence-grounded claims without a reference answer; judge calibration remains a human-label comparison design exercise here.

**2. Validate the gate file.** The following commands preserve the class thresholds:

```bash
uv run --no-sync python -m training.session1.check_gates app/evaluation/gates.json
```

Expected: `valid: status=placeholder p95_total_ms_max=2000.0`, exit code 0. A valid file is not production approval.

```bash
uv run --no-sync python - <<'PY'
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

gates = json.loads(Path("app/evaluation/gates.json").read_text())
gates["faithfulness_min"] = 1.5
with TemporaryDirectory() as directory:
    candidate = Path(directory) / "invalid_gates.json"
    candidate.write_text(json.dumps(gates))
    result = subprocess.run(
        [sys.executable, "-m", "training.session1.check_gates", str(candidate)],
        check=False,
    )
    assert result.returncode == 1, "The invalid threshold must be rejected"
PY
```

Expected child-process output: `INVALID: faithfulness_min - Input should be less than or equal to 1`; the assertion requires its exit code to be 1. Record why `status=placeholder`, absent model-quality measurements or missing approvals means **HOLD**.

**3. Reject a tampered source.** Predict the result, then run:

```bash
uv run --no-sync python -m training.showcase --session 1
```

Eight unchanged documents verify; a temporary changed copy is refused because its SHA-256 differs from the register. Submit the ID, exact error, responsible owner and next investigation. Explain why a valid hash does not prove data permission or policy correctness.

**4. Review a provider change.** Tabletop scenario: a model/provider candidate passes schema validation, but has no comparable golden-set report, compatibility evidence or owner approval. Decide **HOLD**, then list the evidence that could support promotion: frozen baseline/candidate runs; structured-output/tool/context compatibility as applicable; task quality, safety, latency and cost; data/provider approval; and a named approver. A proposed rollback retains the previous model/configuration, prompt and compatible corpus, embedding, index and parent stores. State a trigger, how to validate restored behavior, and when the previous version can be retired. No provider switch, automated CI, canary or rollback is executed in this exercise.

**Exit submission:** completed inventory, four-case baseline worksheet, gate-validation and source-tamper transcripts, and the signed-role release decision. Passing the class exercise leaves production thresholds and unmeasured behavior open. See the [slide-to-syllabus map](../decks/SYLLABUS_ALIGNMENT.md).

## A1. What you will be able to do by the end
1. Explain why an LLM app that works on Friday can fail on Monday (three production constraints).
2. Draw the NexaAssist architecture and say what runs offline and what runs online.
3. Say what the four quality gates of the 4D framework are and why each exists.
4. Show that the project refuses a tampered source document.
5. Write a measurable spec: success numbers, a "must refuse" list, and a data-access decision.

## A2. Key ideas (read before the labs)
| Term | One-line meaning |
|---|---|
| LLMOps | Engineering practices to design, deploy, run and improve LLM systems under real limits on correctness, latency, cost and safety |
| The three constraints | **Stochasticity** (same input, different outputs: a trust problem), **latency** (slow replies: a UX problem), **cost** (tokens are billed: a business problem) |
| Artifacts | Things that change behaviour without a code change: prompts, embeddings, the knowledge base |
| 4D | **Discover** (define) - **Distill** (prove quality) - **Deploy** (make it run safely) - **Deliver** (operate and improve). A loop, not a line |
| Quality gate | A written pass/fail check you must clear before the next phase |
| SLO | Service level objective: a measurable target, e.g. 95 percent of answers in under 2 seconds |
| RAG | Retrieval-augmented generation: look up relevant text first, then let the model answer from it |
| Offline vs online | Offline = data preparation (ingestion). Online = answering a user's question. Kept apart so a question never waits for ingestion |
| Data divergence | The gap between what users expect and what the search index really contains (stale, missing, wrong permissions) |

The four gates:
| Phase | Gate | Question it answers |
|---|---|---|
| Discover | Data availability and governance | Are we allowed (and able) to build this? |
| Distill | Offline evaluation on a golden set | Is the quality good enough to ship? |
| Deploy | SLO check | Does it stay within latency, cost and error budgets? |
| Deliver | Rollback trigger | Has it got worse in production, and do we roll back? |

## A3. Setup check (10 minutes, do before the labs)
Open a terminal in the project folder (the one containing `pyproject.toml`).

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/nexaassist
uv sync --python 3.14 --locked --extra ui --extra evaluation
```
The first run downloads many packages and can take a few minutes. Keep the `export` line: you need it in every new terminal.
(It keeps the virtual environment out of the project folder, which matters if the folder is synced by Google Drive.)

## A4. Lab 1 - Get a green baseline (20 min) [offline]
Goal: know what "healthy" looks like before you change anything.

```bash
RAGAS_DO_NOT_TRACK=true uv run --no-sync pytest -q
```
Expected at the end: `1 failed, 168 passed` (numbers may differ by a few). The one failure is
`tests/test_architecture_document.py::test_architecture_paths_and_walkthroughs_resolve`: it looks for a documentation folder that is not in
this copy of the project. Everything else passes. **A known failure is written down, not ignored.**

List the test files and fill in the table below with one sentence each (guess from the name, then open the file and check the first test):
```bash
ls tests/test_*.py
uv run --no-sync pytest tests/test_gates.py -v
```

| Test file | What it protects (your words) |
|---|---|
| test_ingestion.py | |
| test_answer.py | |
| test_retrieval.py | |
| test_prompts.py | |
| test_gates.py | |
| test_rate_limit.py | |

Answer in your notebook: *Which three files protect against "a model answers confidently from the wrong source"?*

## A5. Lab 2 - Start the service and read its vital signs (30 min) [offline]
Goal: see the online half of the system running, and learn what each health route promises.
Use **two terminals**, both in the project folder with the `export UV_PROJECT_ENVIRONMENT=...` line.

**Terminal A - start the API with placeholder settings (no real database or model key):**
```bash
export MONGODB_URI=mongodb://unused MONGODB_DB=d MONGODB_COLLECTION=c OPENAI_API_KEY=unused
export INSTITUTION=NexaBank JURISDICTION=IN CONFIDENTIALITY_LEVEL=internal
uv run --no-sync python -m uvicorn app.main:app --port 8000
```
Wait for `Application startup complete`.

**Terminal B - call it:**
```bash
curl -s localhost:8000/health ; echo
curl -s localhost:8000/metrics/answers ; echo
curl -s localhost:8000/openapi.json | python3 -c "import json,sys; print(*sorted(json.load(sys.stdin)['paths']), sep='\n')"
```
You should see `{"status":"ok"}`, a block of zeros with `cost_per_query_usd` and `sampled_hallucination_rate` set to `null`, and ten routes.

Now the readiness check. It is slow when the database cannot be reached, so be patient: it takes about 30 seconds.
```bash
time curl -s -w " http=%{http_code}\n" localhost:8000/ready
```
Expected: `{"detail":"Not ready"} http=503`.

Answer in your notebook:
1. Why does `/health` say ok while `/ready` says not ready? Which one should a load balancer use to decide whether to send traffic?
2. Why are `cost_per_query_usd` and `sampled_hallucination_rate` `null` and not `0`? (Hint: what is the difference between "measured as zero" and "not measured"?)
3. `/ready` took about 30 seconds to fail. Who waits during those 30 seconds, and what would you change?

Stop the server with Ctrl-C in Terminal A when done.

## A6. Lab 3 - Source of truth and tampering (40 min) [offline]
Goal: see the Discover gate ("do we have programmatic access to a trusted source of truth?") enforced in code.

Step 1. Read the register: it lists every document the system is allowed to index.
```bash
uv run --no-sync python -c "
import json
for e in json.load(open('nexa_synthetic_data/document_register.json')):
    print(e['doc_id'], e['version'], e['status'], e['effective_from'], '->', e['effective_to'], 'authoritative=', e['authoritative'], e['sha256'][:10])"
```
Answer: which documents are superseded? Which one amends part of another?

Step 2. Prove a changed file is refused. Run `uv run --no-sync python -m training.session1.tamper` (source: `training/session1/tamper.py`; read it first, it works on a temporary copy and changes nothing).
Expected:
```
1. untouched copy: 8 documents verified
2. tampered copy refused: POL-HL-V3: file sha256 does not match the document register
```
Run the two real tests that guard this: `uv run --no-sync pytest tests/test_ingestion.py -k hash -v`.

Answer: (a) You changed one bit. Why is a one-bit change enough to be refused? (b) Name a real-world event this protects against.

Step 3. Governance memo (write 5 lines): *The policies are fictional, but suppose they were real, and some PDFs contained customer names.*
May we send them to a third-party model provider? Under what conditions would you instead host a model yourself? Who has to approve?

## A7. Lab 4 - Write the spec (50 min) [offline]
Goal: turn "make a good bot" into numbers a test can check. This is the main deliverable of the session.

Step 1. Copy the shared thresholds file so you do not edit the class copy:
```bash
cp app/evaluation/gates.json evaluation/gates.mine.json
```
Step 2. Open `evaluation/gates.mine.json` and, for each line, write in your notebook one sentence justifying your number (who is hurt if it is
too loose? what does it cost if too strict?). The shipped values are *placeholders taken from the course's examples*, not decisions.
Keep `"status": "placeholder"` unless your team has truly confirmed the numbers.

| Field | Meaning | Shipped | Yours | Why |
|---|---|---|---|---|
| faithfulness_min | answer claims are supported by the retrieved text | 0.85 | | |
| answer_relevancy_min | answer addresses the question | 0.85 | | |
| context_precision_min / context_recall_min | retrieval brought the right passages | 0.85 / 0.85 | | |
| judge_correctness_min / judge_groundedness_min | LLM judge scores | 0.85 / 0.85 | | |
| status_match_rate_min | share of cases with the right answer/abstain/clarify behaviour | 0.85 | | |
| p95_total_ms_max | slowest 5 percent of answers | 2000 | | |
| cost_per_query_usd_max | average cost per question | 0.01 | | |
| error_rate_max | share of requests failing (5xx) | 0.001 | | |
| hallucination_rate_rollback | above this, roll back | 0.05 | | |

Step 3. Check your file is valid (the loader rejects unknown fields and out-of-range numbers):
```bash
uv run --no-sync python -m training.session1.check_gates evaluation/gates.mine.json
```
Expected: `valid: status=placeholder p95_total_ms_max=2000.0` (your values may differ).
Break it on purpose: change `faithfulness_min` to `1.5` and run again. Read the error (it names the field; the exit code is 1). Put it back.

Step 4. Fill in the manifest below (a one-page contract; save it as `use_case_manifest.md` in your own folder, not in the repo).

```markdown
# Use-case manifest: NexaAssist (your team's version)
## 1. Problem statement
Who struggles with what today, and what does it cost?
## 2. Product definition
What it accepts, what it returns (always with sources), and what it must never do.
## 3. Success KPIs (the gates)
Point to your gates.mine.json values: faithfulness, relevancy, latency, cost, error rate.
## 4. Must-refuse list (at least 5)
e.g. approve or decline a loan; advice about a named customer; questions outside the policy corpus; ...
## 5. Data inventory
Source of truth (document_register.json), versions, freshness rule ("re-ingest when the register changes"), restrictions.
## 6. Risks and mitigations
Hallucination, outdated policy (wrong date), data leakage, prompt injection, cost spikes: each with one mitigation.
```

## A8. Gate checklist (hand in at the end)
- [ ] Baseline test run recorded, known failure explained
- [ ] Answers to Lab 2 questions
- [ ] Tamper lab output pasted and Lab 3 answers written
- [ ] `gates.mine.json` valid, with a justification for every threshold
- [ ] Manifest with a must-refuse list and a data-access decision
**Discover gate passed when:** a stranger could read your manifest and tell, in numbers, what "good enough" means, and which data you may use.

## A9. Homework (30 min)
1. Read `app/chains/chunking.py` (95 lines). In your own words: what is a "clause chunk" and why not split every 500 characters?
2. Bring one question the bot must refuse and one it must answer *with a date caveat*.
3. Optional: skim README section 5 ("the chunk record") and list the metadata fields.

## A10. Self-check quiz (answers in Part B)
1. Name the three production constraints. 2. What does "gate" mean in 4D? 3. Why are ingestion and answering separate? 4. Why is a prompt an
"artifact"? 5. What does the sha256 in the register protect against?

## Course alignment for this session

See [the complete lesson-to-slide map](../decks/COURSE_ALIGNMENT.md). Source-course technologies are translated to the existing MongoDB/LangChain architecture; design extensions are not live implementation claims.
