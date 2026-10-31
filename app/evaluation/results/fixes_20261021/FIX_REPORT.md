# NexaAssist fixes and verification

21 October 2026 · synthetic training policies · local development environment

The incorrect Home Loan processing-fee answer is fixed in the tested journeys,
including the default five-source request and the earlier failing twenty-source
request. Institution filtering, parent scope validation, reviewer authorization,
feedback retries and clarification responses now have regression coverage.

The table separates completed fixes from remaining gaps. This does **not**
establish production readiness. Reloading a previously open sidebar still produces a layout shift,
and authenticated Datadog cloud receipt was not checked in this pass.

## What changed

| Earlier finding | Change and verification | Status |
|---|---|---|
| Default fee answer used the older policy | Retrieval loads complete effective circulars linked to the retrieved policy IDs, with applicability and grandfathering clauses. Live five-source and twenty-source answers use 0.30%, ₹5,000 minimum and ₹10,000 maximum for sanctions from 1 July 2026, plus the supported GST rate. | Fixed in tested cases |
| Wider retrieval abstained on the fee | Complete amendments are supplied before ordinary parent context, without raising the source default. A complete amendment that cannot fit the token budget causes abstention before generation. | Fixed; budget regression tested |
| Later evaluated repeat failed citation checks | Allow one repair draft against the same evidence. Both attempts retain exact quote/marker checks; two invalid drafts still abstain. Retrieval is not repeated, and RAGAS scores only the final returned answer. | Bounded recovery added; success and exhaustion tested |
| Missing institution filter | Dense/hybrid searches and amendment queries share institution, date, product, jurisdiction and confidentiality scope. The Atlas vector index now includes `institution` and is READY/queryable. | Fixed; controlled tests and live index/retrieval checks |
| Review: chained or inconsistent circulars | Follow effective circular-to-circular links with a visited-ID set. Load all indexed parts of each discovered instrument and reject mixed dates/products/source scope with a service error. | Fixed; chained-link and inconsistent-metadata regressions |
| Parent expansion could cross scope | A parent must match the child's institution, jurisdiction, confidentiality, document/version, product and source validity metadata. A mismatch retains the scoped child. | Fixed; institution/product/future/expired-parent regressions |
| Feedback list/review had no authorization | Both review routes require a configured bearer secret. No configuration returns 503; missing/wrong credentials return 401. The UI requests the token and clears cached records when it changes. | Fixed for the local reviewer capability |
| A feedback retry could create duplicates | The UI retains a submission UUID. An atomic MongoDB upsert returns the existing record on an identical retry, including after review, without another Datadog SDK attempt. Changed contents with the same ID return 409. | Fixed; real API readback and an eight-retry controlled test |
| Product/date conflicts and vague rate questions gave generic abstentions | Added `needs_clarification` with a fixed scope question. Model-written clarification claims are never forwarded. Abstentions also give product/date recovery guidance. | Improved; date-intent classification remains variable |
| Caption contrast failed | Increased caption opacity using a scoped style. | Accessibility snapshot passed |
| Date segments were too small | Month/day segments now measure at least 24×24 pixels. | Accessibility snapshot passed |
| Product field had an empty autocomplete attribute | Set its native autocomplete option explicitly to `off`. | Chrome no longer reports that issue group |
| Fast form entry was uncertain | A real Chrome test filled a reference and immediately submitted a question, then filled a correction and immediately submitted feedback. API logs confirm `reference_source: provided`; database readback confirms the complete correction. | Passed; no application data-loss bug reproduced |
| Page-load CLS was 0.24 | A collapsed first load measured CLS 0.00, but reloading a previously open sidebar still measured 0.24. A render-order experiment did not improve it and was removed. | Partial; remains open |

The earlier reports remain unchanged historical evidence:
[system UAT](../system_uat_20261021/REPORT.md) and
[Chrome DevTools validation](../devtools_validation_20261021/REPORT.md).

## Source-grounded GST decision

The NexaFlex foreclosure clause states **4% of outstanding principal plus GST**
after six EMIs. It does not specify the GST percentage. The user confirmed that
the answer should retain that wording rather than borrow 18% from the separate
processing-fee clause.

Corrected the implemented foreclosure reference in
`evaluation/datasets/answer.jsonl` and its GQ-004 mirrors in the source QA JSON
and JSONL files. This corrects an unsupported reference expectation; it does not
change a policy document or relax the lock-in or fee requirements. The live
foreclosure answer already matches the source wording. Wider, unimplemented
customer/calculation fixtures were not rewritten or certified by this pass.

## Live answer checks

All responses below were validated against the actual response model. Verdicts
also reflect reading the answer and its conditions, rather than HTTP 200 alone.

| Scenario | Observed answer |
|---|---|
| Current fee, five sources | Revised 0.30%, ₹5,000–₹10,000, plus supported GST; explains the sanction cutoff and earlier terms |
| Sanction on 30 June 2026 | Earlier 0.35%, ₹5,000–₹15,000, plus 18% GST |
| Sanction on 1 July 2026 | Revised 0.30%, ₹5,000–₹10,000, plus 18% GST |
| Policy lookup on 30 June 2026 | Earlier fee; the future circular is excluded |
| Home question with Auto filter | Asks which product to use |
| “What is the rate?” | Asks which product's rate |
| Question date conflicts with date filter | Asks which policy date to use |
| Earlier sanction; ₹12,000 prepayment | Revised minimum requires opt-in; otherwise ₹25,000 remains. Does not assume the borrower opted in. |
| NexaFlex foreclosure | Six-EMI lock-in, then 4% plus GST |
| NexaHome maximum | ₹7.5 crore |
| Current fee, twenty sources | Correct revised fee and sanction-date condition |
| Unsupported current NRLR | `insufficient_evidence`; no invented current rate |

One post-review date-conflict attempt returned `insufficient_evidence` instead
of `needs_clarification`. Its status assertion stopped the provisional harness
before saving that response body; the API event and this limitation are recorded
in `live_date_classification_variability.json`. The six completed responses were
retained, and the remaining six cases were run separately with responses saved
before assessment. After the scope-first prompt change, the date question returned
the fixed clarification. This does not erase the earlier false negative:
classification still relies on the model. The fixed abstention now tells the
user to check the selected product/date and specify the term.

The final twelve targeted cases after the second-opinion fixes are in
`latest_live_answers.json`. The preceding ten-case batch is in `live_answers.json`;
two additional earlier API checks are in `final_api_checks.json`. Intermediate outputs are kept
with an `initial_` prefix and do not supersede the final results. The original
nineteen-case UAT was not rerun wholesale or counted again.

After the final parent-scope change, `/retrieve` returned five scoped hits,
one complete linked circular and valid expanded parents (`final_retrieval.json`).
API health/metrics and Streamlit health returned 200. The Docker Datadog Agent
was healthy; it was not replaced with the native macOS Agent.

## Evaluation and browser evidence

An earlier live current-fee evaluation scored all four metrics:

| Metric | Measured value |
|---|---:|
| Faithfulness | 1.000 |
| Answer relevancy | 0.522 |
| Context precision | approximately 1.000 |
| Context recall | 1.000 |

The relevancy score is retained as measured. Correct fee facts and a high
faithfulness score do not make every quality dimension a pass. RAGAS is an
LLM-assisted measurement, not independent human approval.

A subsequent evaluated fee sample (`ragas_fee_final.json`, before the citation
repair change) failed citation validation and abstained. Faithfulness/relevancy
were unavailable; context precision/recall were scored. Context-only scores are
not proof of an answered question. The log event confirmed citation validation
as the rejection path. Two failing regression cases then reproduced the lack
of repair/exhaustion handling. The application now permits exactly one repair
draft, records the attempt in its warning, and reports cumulative generation
time. This may add a model call and latency; it does not bypass validation.
The subsequent live sample is in `ragas_fee_after_repair.json`.
That final-code sample returned the correct conditional fee and scored all four
metrics: faithfulness **1.000**, relevancy **0.859**, precision approximately
**1.000**, recall **1.000**, with Datadog delivery **queued**. Both successful
samples and the intervening abstention remain saved. A successful last sample
does not establish that every future model draft will pass citation checks.

The response reported `datadog_status: queued`. Streamlit displayed the answer,
citations and Datadog link without metric cards. The quick-entry browser test
also scored all four metrics using the supplied reference. No authenticated
cloud page was inspected, so SDK queuing is not claimed as cloud visibility.

The desktop Lighthouse snapshot with the sidebar open scored **100 for
accessibility**, compared with 92 before these changes. This is an automated
snapshot score, not a compliance percentage or a screen-reader study. The
latest inspected Chrome state still has two framework markup issue groups:
unassociated labels and fields without an ID/name. Read-only DOM inspection
identified native date/chat/toggle/group markup; the application controls remain
named in the accessibility tree. These framework issues are not claimed fixed.

The local reload measurements were unthrottled. A collapsed first start measured
LCP 249 ms / CLS 0.00. A previously open sidebar reload measured LCP 282 ms /
CLS 0.24. The raw trace shows the main container moving 300 pixels as the sidebar
appears, followed by smaller control/font changes. This supports the remaining
bootstrap-layout diagnosis; it is not a real-user performance measurement.

Evidence includes `fast_input_browser.json`, `reference_entry_observation.json`,
`fast_browser_feedback.json`, `ragas_fee.json`, `lighthouse_sidebar.json`,
`devtools_roundtrips.json`, the compressed traces, and the screenshots. The chat
screenshot predates the small caption change that now explains linked amendments
can exceed the selected similarity-source count.

## Code and contract mapping

| Responsibility | Files |
|---|---|
| Scoped search and parent checks | `app/chains/retrieval.py` |
| Complete linked-circular lookup | `app/database/retrieval.py`, `app/services/retrieval.py` |
| Supplemental evidence contract | `app/models/retrieval.py` |
| Context budget, citations, clarification | `app/chains/answer.py`, `app/chains/prompts/answer.py`, `app/models/answer.py` |
| Same evidence in live/offline evaluation | `app/services/evaluation.py`, `app/evaluation/run.py`, `app/evaluation/answer_evaluation.py` |
| Reviewer capability | `app/api/auth.py`, `app/api/feedback.py`, `app/core/config.py` |
| Atomic feedback retries | `app/models/feedback.py`, `app/database/feedback.py`, `app/services/feedback.py` |
| UI inputs, review credential and accessibility | `app/ui/app.py` |
| Setup and compatibility notes | `.env.example`, `README.md`, `DATADOG_README.md`, `app/database/indexes.md` |

API consumers must accept the new `needs_clarification` status and the additive
retrieval `amendments` field. Complete instruments have a null clause and a
document-level citation; that does not mean the instrument lacks supporting
clauses. The existing child-ID coverage diagnostic remains a mechanical check,
not semantic recall for a whole-instrument citation.

The local ignored `.env` now contains a generated `FEEDBACK_REVIEWER_TOKEN`.
Enter that value in Streamlit's **Review feedback** workspace. The value was
not printed, included in the review artifact, or committed. For a new checkout,
generate a separate random secret of at least 32 characters and restart FastAPI.
The shared token does not provide individual users, role management or an
authenticated submitter identity. Use proper identity/roles and TLS before
shared remote deployment.

## Checks run

| Check | Result |
|---|---|
| Application pytest | **121 passed**, 10.90 seconds |
| Separate synthetic mock API pytest | **22 passed**, 0.46 seconds |
| Ruff lint | Passed |
| Ruff formatting | Passed |
| Mypy | Passed; 56 application source files |
| Golden loaders and mirrors | Both loaders accepted ten implemented cases; source JSON and JSONL agree |
| Feedback authorization/retry | Live 401/200/409 paths passed; controlled unconfigured-token 503 passed |
| Fast-input Chrome regression | Supplied reference and correction preserved; metrics hidden |

Commands and full results are represented by `pytest.xml`, `mock_pytest.xml`,
`auth_retry_results.json`, and the companion JSON evidence. Line coverage was
not measured. Live Atlas/model checks used synthetic training policy data;
controlled tests do not substitute for real shared-corpus or load testing.

The independent reviewer found the missing parent product/date checks. Those
were classified as actionable, reproduced as three failing regressions, fixed,
and included in the passing suite. The user-approved Codex CLI second opinion
is tracked separately by its saved command and immutable patch hash. Its
result is saved in `codex_second_opinion.md`. All four findings were classified
as actionable. Eight failing regression cases reproduced chained/mixed circular
problems and unsafe clarification text. The fixes pass the suite;
`codex_review_reconciliation.json` maps each finding to its test. The CLI was not
run again after these follow-up changes.

## Cleanup and remaining limits

Three feedback records created by these fix tests were backed up and removed.
Cleanup required their exact IDs, institution, correction text, rejected status
and synthetic reviewer; no other feedback or source policy document was deleted.
See `cleanup_backup.json` and `cleanup_result.json`.

The Atlas index definition was updated to add the institution filter while
preserving its vector and other fields. Before/after and READY status evidence
are saved separately. No policy PDF, embedding model or corpus re-ingestion
was changed.

Still open: probabilistic date-intent classification, the restored-sidebar reload shift, the two framework markup issue
groups, and the Datadog integration's “Dropping prompt on non-LLM span kind”
warning. The installed ddtrace LangChain adapter attaches template metadata;
its serializer drops that metadata from a non-LLM span. Application workflow
annotations use input/output data rather than the prompt argument. The warning
was not hidden by disabling tracing or patching installed dependencies; complete
cloud prompt capture still needs a separate verification.

The shared citation checks guarantee marker/quote membership, not semantic
entailment or a successful answer on every model call. A valid-looking draft can
still need semantic review, and two invalid citation drafts still abstain.

Not checked: sustained load, recruited-user usability, full accessibility,
authenticated Datadog/LangSmith receipt, multi-institution write isolation,
customer-tool integrations, live hybrid/reranked quality, disaster recovery or
in-flight provider/Atlas outage recovery. Datadog feedback delivery remains best
effort, with no durable outbox. API and UI are left running locally. No commit,
push or deployment was made.
