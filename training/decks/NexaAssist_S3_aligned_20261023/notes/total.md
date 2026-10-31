# 01_Distill II

Prompts, generation and evaluation gates Session 3 of 5 · 3 hours · source-aligned workshop Today uses controlled model drafts through the actual LCEL chain. The class will explain both deterministic validation and semantic judgment. This revised deck follows the course lesson sequence; exact lesson URLs appear in section notes and the coverage map.

---

# 02_What you will produce

A grounded answer replay and a failure diagnosis. Three proposed golden cases with a review memo. A documented quality gate decision. Carry retrieval evidence from Session 2. An answer-quality result needs the question, expected behavior, evidence references and actual response.

---

# 03_The three-hour plan

25 min prompts/evaluation + 20 min code walkthrough 90 min pair labs, including a 10 min break 25 min gate decisions + 20 min review Split the lab block across answer replay, failure classification and golden-case review. Use the detailed handout as the exercise sheet.

---

# 04_Showcase / reject a convincing bad answer

An attacker supplies closing tags and instructions. A generated draft cites an invented quote. A candidate has a lower faithfulness score. Distinguish escaped syntax, citation validation and semantic evaluation. A delimiter test does not prove injection resistance; valid quotes do not establish every claim.

---

# 05_Run prompt and evaluation demonstrations

python -m training.showcase --session 3 Tag escape retained; bad quote → abstention. Same cases: −0.25; changed dataset: refused. Allow 25 minutes. Also exercise the output PII rail. Inspect prompt version 1.1.0, the one-repair limit and dataset/judge identity checks. Scores and drafts are visibly synthetic.

Code walkthrough: app/evaluation/run.py
def case_fingerprint(case: GoldenCase) -> str:
    canonical = json.dumps(case.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


Align reviewed cases and the judge contract. Inspect case flips alongside aggregate deltas. Regenerate reports that lack identity evidence. The application model or prompt may change deliberately. Dataset, judge model/prompt and metric versions must align. CLI exits 2 for incomparable evidence, 1 for regressions or newly failing cases. Live golden evaluation is still required before release.

---

# 06_Prompt Engineering and Prompt Life Cycle Management

Educative lesson 09 Concept → worked example → NexaAssist application This section follows the lesson Prompt Engineering and Prompt Life Cycle Management. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 07_A prompt has three responsibilities

Role: what the assistant is authorized to do. Evidence boundary: which supplied text supports claims. Output contract: schema, status and citations. Prompts guide model behavior but cannot enforce every safety property. The application validates output and evidence after generation. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management. The implementation or concept reference is app/chains/prompts/answer.py.

---

# 08_A production prompt separates three concerns

Instructions: Role, scope and abstention Untrusted data: Question + retrieved documents Output contract: Typed status + exact citations The relationship is constraint and validation, not a claim that delimiters confer authority. System-role rules remain separate from untrusted user/context content. The source uses Jinja templates and XML; NexaAssist uses ChatPromptTemplate and JSON-serialized evidence. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 09_Delimiters mark structure; they do not stop every attack

Wrap untrusted content with explicit boundaries. Escape delimiter-like content before rendering examples. Keep privileged instructions outside the data field. The shared answer chain now escapes every human-message variable, wraps request/evidence fields in XML boundaries and ends with a reminder. Prompt 1.1.0 is versioned and fingerprint-pinned. These controls preserve structure; live injection resistance and policy semantics require model evaluation. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 10_The sandwich pattern repeats a narrow rule

Give scope and grounding instructions before the data. Place the question inside its declared data boundary. End with a reminder to follow the output contract. The source motivates this pattern with recency sensitivity. It is a prompt-design technique to evaluate, not a hard security boundary. Changing the actual answer prompt still requires versioning, pin updates and behavioral evaluation. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 11_JSON mode and strict schema solve different problems

Valid JSON only guarantees a parseable representation. A schema checks fields, types and allowed status values. Source support and policy meaning need further checks. The course demonstrates JSON-object output. NexaAssist uses integration strict JSON-schema output and validates AnswerDraft. Neither mechanism makes the contents automatically correct or safe. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 12_The prompt is a tracked artifact

Prompt ID, version and fingerprint travel with the answer provenance. Open app/chains/prompts/answer.py and locate ANSWER_PROMPT_ID. Read the displayed excerpt in context; it is taken directly from the application. Prompt ID, version and fingerprint travel with the answer provenance. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management. The implementation or concept reference is app/chains/prompts/answer.py.

---

# 13_Make a prompt change reviewable

Run tests/test_prompts.py before changing wording. A wording change requires a version and pin update. Then replay cases; a new hash proves identity, not quality. The workshop does not alter the shared prompt. Delimiters and closing reminders remain a proposed future change that would need a version bump and live evaluation. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 14_LCEL composes prompt and strict model output

The chain requests AnswerDraft with strict JSON-schema output. Open app/chains/answer.py and locate generation = ANSWER_PROMPT. Read the displayed excerpt in context; it is taken directly from the application. The chain requests AnswerDraft with strict JSON-schema output. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management. The implementation or concept reference is app/chains/answer.py.

---

# 15_Status is part of the API contract

Distinguish answered, insufficient_evidence and needs_clarification. Open app/models/answer.py and locate class AnswerDraft. Read the displayed excerpt in context; it is taken directly from the application. Distinguish answered, insufficient_evidence and needs_clarification. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management. The implementation or concept reference is app/models/answer.py.

---

# 16_A registry supports comparison and rollback

Track prompt text, version, owner and evaluation evidence. Compare candidates with the same cases and configuration. Hot-swapping and A/B routing need their own controls. The existing code stores prompts as versioned Python artifacts and returns fingerprints. It is not a hot-swapping prompt registry. Teach the registry responsibility without claiming a new service exists. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 17_Practical / render a boundary attack safely

Run: python -m training.session3.prompt_boundaries Inspect escaped closing tags and retained question text. Check template variables and compare the production rendering. The lab runs the actual answer chain with a fake model and parses the prompt it receives. Closing tags remain data and the system role survives. The fixture abstention does not prove that a live model ignores every injected instruction. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 18_The answer path fails closed

Retrieve and budget evidence → generate draft Check output PII → check IDs, markers and exact quotes Return supported response, repair once or abstain A clarification uses a fixed safe scope question. Citation failure allows one repair, while detected PII returns the existing safe abstention immediately. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management. The implementation or concept reference is app/chains/answer.py.

---

# 19_What exact quotes do and do not establish

An exact quote proves those bytes were supplied. It does not prove the claim follows from the quote. Semantic evaluation must still check grounding and scope. Use an unrelated policy claim paired with a real source quote as the counterexample. This is why citation integrity and faithfulness remain separate measurements. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 20_Practical 1 / replay three model drafts

Run: python -m training.session3.answers Valid → answered; invented quote → abstention. Output PII → abstention with no leaked citation. Expect one call for the valid draft, two for the fixed invalid quote, and one for the PII draft. All model calls are fakes; the chain validation is real. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 21_Exercise / break evidence identity

In a lab copy, change the evidence ID to 99. Predict the marker/ID mismatch and repair count. Then explain a wrong answer with a valid quote. Do not edit shared production prompts during class. Review the valid and invalid branches and capture the prediction before running the modified copy. Source lesson: https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management.

---

# 22_Evaluation of LLM Outputs: Metrics, Tests, and Human Feedback

Educative lesson 10 Concept → worked example → NexaAssist application This section follows the lesson Evaluation of LLM Outputs: Metrics, Tests, and Human Feedback. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback.

---

# 23_Meaning defeats exact string comparison

Paraphrases can be correct despite little word overlap. A tiny negation can reverse an otherwise similar answer. Use semantic criteria plus deterministic contract checks. BLEU and ROUGE can remain useful for some tasks, but overlap alone is a poor release gate for policy answers. Use an original example: “eligible after twelve months” versus “ineligible after twelve months” to show why shared words are insufficient. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback.

---

# 24_The RAG triad assigns different questions

Question: What was asked? Retrieved context: Was useful evidence found? Generated answer: Is it supported and responsive? The triad localizes faults. Specific Ragas metrics have their own implementation definitions and reference requirements; do not replace them with a vague all-purpose accuracy score. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback.

---

# 25_Use metrics that match the failure

Context precision: relevance of retrieved material. Context recall: coverage of reference information. Faithfulness and answer relevance: grounding and fit. Judge scores are estimates influenced by context and rubric. We use the local evaluation implementation and human review rather than treating exact word overlap as truth. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback.

---

# 26_Golden cases need human verification

Input includes question, date and product scope. Expected output/status and source references are explicit. Put verifier and review rationale in a companion memo. The schema forbids extra fields. A reviewer name added directly to the GoldenAnswer JSON would fail validation, so use the separate memo. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback. The implementation or concept reference is app/evaluation/answer_evaluation.py.

---

# 27_A judge needs a rubric and calibration

Provide query, context, response and explicit criteria. Score claims against evidence and record reasons. Compare a sample against human judgments. Low temperature can reduce variability but does not make a judge deterministic. Watch for preference, ordering and correlated model errors. Human agreement checking is an outstanding project improvement; it is taught here as a required design consideration. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback.

---

# 28_Practical 2 / classify the fault

Run: python -m training.session3.gates Missing required context → retrieval_error. Complete context, unsupported response → generation_error. The scores are synthetic and deliberately chosen to trigger the production gate. Do not label the output a measured Ragas benchmark. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback.

---

# 29_A gate names the metric that failed

Per-metric means and failed cases make the decision actionable. Open app/evaluation/gates.py and locate def gate_failures. Read the displayed excerpt in context; it is taken directly from the application. Per-metric means and failed cases make the decision actionable. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback. The implementation or concept reference is app/evaluation/gates.py.

---

# 30_Practical 3 / propose three golden cases

Copy the JSONL dataset into /tmp. Add answer, abstention and clarification examples. Validate with load_golden; review the actual source clauses. Do not automatically translate refusal or prompt-injection categories. The correct expected status depends on the meaning of each input and must be reviewed. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback. The implementation or concept reference is training/session3/handout.md.

---

# 31_Offline does not always mean no provider

Class labs use fakes and need no credentials. A pre-release golden evaluation can call real models. Live evaluation needs approved access, cost and data. Distinguish offline evaluation as a lifecycle concept from offline execution as a network constraint. The required class exercises satisfy both; optional Ragas runs use providers. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback.

---

# 32_Compare like with like

Keep case set, retrieval configuration and judge aligned. Save the baseline before writing the next report. Inspect per-metric deltas and newly failing cases. The comparison helper does not enforce dataset identity. The operator must verify comparability before interpreting a delta as a regression. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback. The implementation or concept reference is app/evaluation/compare.py.

---

# 33_Spend evaluation budget where it catches regressions

A representative subset can gate frequent changes. Broader release or scheduled evaluations cover more cases. Keep judge, dataset and prompt identities in reports. The source distinguishes a small CI set from larger scheduled evaluation. This project has evaluation CLIs and local tests, but no CI pipeline is added in this revision. A subset passing does not validate unseen categories. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback.

---

# 34_Optional live / run and compare

Run app.evaluation.run --limit 3 with approved .env. Preserve old and new reports under distinct paths. Run app.evaluation.compare OLD.json NEW.json. Full commands are in the handout. Preserve provenance and investigate any newly failing case, even if aggregate metrics hide it. Source lesson: https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback.

---

# 35_Exit gate / quality with an explanation

Three valid cases and human review memo. A named failure type for every failing example. Thresholds met or a documented release hold. A classroom pass requires a defensible interpretation. A real release remains blocked by unmeasured quality or unapproved targets.

---

# 36_Next / make failure safe to serve

Keep generation behind the service layer. Bring one invalid input and one dependency outage. Session 4 will measure the API failure contract. The next class wraps the already-working intelligence in deterministic request validation, quotas, readiness checks and measurable operational constraints.
