# 01_Distill II

Prompts, generation and evaluation gates Session 3 of 5 · 3 hours · offline draft replay Today uses controlled model drafts through the actual LCEL chain. The class will explain both deterministic validation and semantic judgment.

---

# 02_What you will produce

A grounded answer replay and a failure diagnosis. Three proposed golden cases with a review memo. A documented quality gate decision. Carry retrieval evidence from Session 2. An answer-quality result needs the question, expected behavior, evidence references and actual response.

---

# 03_The three-hour plan

25 min prompts/evaluation + 20 min code walkthrough 90 min pair labs, including a 10 min break 25 min gate decisions + 20 min review Split the lab block across answer replay, failure classification and golden-case review. Use the detailed handout as the exercise sheet.

---

# 04_A prompt has three responsibilities

Role: what the assistant is authorized to do. Evidence boundary: which supplied text supports claims. Output contract: schema, status and citations. Prompts guide model behavior but cannot enforce every safety property. The application validates output and evidence after generation. The implementation or concept reference is app/chains/prompts/answer.py.

---

# 05_The prompt is a tracked artifact

Prompt ID, version and fingerprint travel with the answer provenance. Open app/chains/prompts/answer.py and locate ANSWER_PROMPT_ID. Read the displayed excerpt in context; it is taken directly from the application. Prompt ID, version and fingerprint travel with the answer provenance. The implementation or concept reference is app/chains/prompts/answer.py.

---

# 06_Make a prompt change reviewable

Run tests/test_prompts.py before changing wording. A wording change requires a version and pin update. Then replay cases; a new hash proves identity, not quality. The workshop does not alter the shared prompt. Delimiters and closing reminders remain a proposed future change that would need a version bump and live evaluation.

---

# 07_LCEL composes prompt and strict model output

The chain requests AnswerDraft with strict JSON-schema output. Open app/chains/answer.py and locate generation = ANSWER_PROMPT. Read the displayed excerpt in context; it is taken directly from the application. The chain requests AnswerDraft with strict JSON-schema output. The implementation or concept reference is app/chains/answer.py.

---

# 08_Status is part of the API contract

Distinguish answered, insufficient_evidence and needs_clarification. Open app/models/answer.py and locate class AnswerDraft. Read the displayed excerpt in context; it is taken directly from the application. Distinguish answered, insufficient_evidence and needs_clarification. The implementation or concept reference is app/models/answer.py.

---

# 09_The answer path fails closed

Retrieve and budget evidence → generate draft Check output PII → check IDs, markers and exact quotes Return supported response, repair once or abstain A clarification uses a fixed safe scope question. Citation failure allows one repair, while detected PII returns the existing safe abstention immediately. The implementation or concept reference is app/chains/answer.py.

---

# 10_What exact quotes do and do not establish

An exact quote proves those bytes were supplied. It does not prove the claim follows from the quote. Semantic evaluation must still check grounding and scope. Use an unrelated policy claim paired with a real source quote as the counterexample. This is why citation integrity and faithfulness remain separate measurements.

---

# 11_Practical 1 / replay three model drafts

Run: python -m training.session3.answers Valid → answered; invented quote → abstention. Output PII → abstention with no leaked citation. Expect one call for the valid draft, two for the fixed invalid quote, and one for the PII draft. All model calls are fakes; the chain validation is real.

---

# 12_Exercise / break evidence identity

In a lab copy, change the evidence ID to 99. Predict the marker/ID mismatch and repair count. Then explain a wrong answer with a valid quote. Do not edit shared production prompts during class. Review the valid and invalid branches and capture the prediction before running the modified copy.

---

# 13_Use metrics that match the failure

Context precision: relevance of retrieved material. Context recall: coverage of reference information. Faithfulness and answer relevance: grounding and fit. Judge scores are estimates influenced by context and rubric. We use the local evaluation implementation and human review rather than treating exact word overlap as truth.

---

# 14_Golden cases need human verification

Input includes question, date and product scope. Expected output/status and source references are explicit. Put verifier and review rationale in a companion memo. The schema forbids extra fields. A reviewer name added directly to the GoldenAnswer JSON would fail validation, so use the separate memo. The implementation or concept reference is app/evaluation/answer_evaluation.py.

---

# 15_Practical 2 / classify the fault

Run: python -m training.session3.gates Missing required context → retrieval_error. Complete context, unsupported response → generation_error. The scores are synthetic and deliberately chosen to trigger the production gate. Do not label the output a measured Ragas benchmark.

---

# 16_A gate names the metric that failed

Per-metric means and failed cases make the decision actionable. Open app/evaluation/gates.py and locate def gate_failures. Read the displayed excerpt in context; it is taken directly from the application. Per-metric means and failed cases make the decision actionable. The implementation or concept reference is app/evaluation/gates.py.

---

# 17_Practical 3 / propose three golden cases

Copy the JSONL dataset into /tmp. Add answer, abstention and clarification examples. Validate with load_golden; review the actual source clauses. Do not automatically translate refusal or prompt-injection categories. The correct expected status depends on the meaning of each input and must be reviewed. The implementation or concept reference is training/session3/handout.md.

---

# 18_Offline does not always mean no provider

Class labs use fakes and need no credentials. A pre-release golden evaluation can call real models. Live evaluation needs approved access, cost and data. Distinguish offline evaluation as a lifecycle concept from offline execution as a network constraint. The required class exercises satisfy both; optional Ragas runs use providers.

---

# 19_Compare like with like

Keep case set, retrieval configuration and judge aligned. Save the baseline before writing the next report. Inspect per-metric deltas and newly failing cases. The comparison helper does not enforce dataset identity. The operator must verify comparability before interpreting a delta as a regression. The implementation or concept reference is app/evaluation/compare.py.

---

# 20_Optional live / run and compare

Run app.evaluation.run --limit 3 with approved .env. Preserve old and new reports under distinct paths. Run app.evaluation.compare OLD.json NEW.json. Full commands are in the handout. Preserve provenance and investigate any newly failing case, even if aggregate metrics hide it.

---

# 21_Exit gate / quality with an explanation

Three valid cases and human review memo. A named failure type for every failing example. Thresholds met or a documented release hold. A classroom pass requires a defensible interpretation. A real release remains blocked by unmeasured quality or unapproved targets.

---

# 22_Next / make failure safe to serve

Keep generation behind the service layer. Bring one invalid input and one dependency outage. Session 4 will measure the API failure contract. The next class wraps the already-working intelligence in deterministic request validation, quotas, readiness checks and measurable operational constraints.
