# Application validation with Chrome DevTools

21 October 2026 · NexaAssist · synthetic training data

**The application’s main flows work, but the current-fee answer still fails.** This pass also found accessibility and layout issues in the rendered UI. Passing the automated suite does not make the application ready for unsupervised policy advice.

This is a fresh automated and browser validation pass. The earlier 19-case live test remains supporting evidence and was not counted as newly rerun. No production code, dependencies, project MCP configuration, or environment settings were changed.

## Fresh results

| Area | Observed result |
|---|---|
| Application pytest suite | **98 passed**, 8.73 seconds; no failures or errors in the saved JUnit report |
| Separate synthetic banking mock API suite | **22 passed**, 0.31 seconds |
| Ruff lint / formatting | Passed; 69 files checked for formatting |
| Mypy | Passed; 55 application source files |
| Live API boundaries | **17 passed**, including malformed requests, invalid feedback/review inputs, limits, missing resources, and wrong methods |
| Live operational endpoints | `/health`, `/metrics`, `/metrics/latency`, and Streamlit health returned 200 |
| Docker Datadog Agent | Healthy; not restarted or reconfigured |
| Browser evidence flow | Five sources rendered; expanding a source showed the actual policy section and metadata |
| Browser evaluated answer | Correct ₹7.5 crore maximum; Datadog evaluation link rendered; all four metric statuses were `scored` and delivery was `queued` in the API event |
| Browser plain answer | All five age limits correctly mapped to applicant category and application/maturity stage |
| Browser feedback and review | Feedback persisted with exported span targets; a keyboard-entered correction persisted; explicit rejected review persisted; overwrite attempt returned 409 |
| Separate browser context | No first-context chat history; independent blank product filter |
| Mobile evidence view | Five results and an expanded source worked at 390×844; document width stayed 390 pixels |
| Browser offline/recovery | Offline reload reached Chrome’s error page; restoring connectivity and navigating to localhost restored the app |
| Browser requests after recovery | 122 listed requests: 121 returned 200 and one returned 304 |

Two synthetic feedback records were backed up and removed after testing. Existing feedback and policy documents were left unchanged. API and Streamlit were left running. The isolated test tabs and MCP client were closed.

## Findings

### High: the fee answer is still outdated

The fresh request to `/answer`, with `top_k: 5`, product `NEXA-HL`, and policy date `2026-10-01`, returned **0.35%, minimum ₹5,000, maximum ₹15,000, plus 18% GST**.

The repository’s reference requires **0.30%, minimum ₹5,000, maximum ₹10,000, plus 18% GST** for sanctions on or after 1 July 2026, while earlier sanctions retain their original fee. The fresh answer also omitted that applicability condition.

This reproduces the earlier failure. Earlier ranked retrieval evidence showed the circular outside the top five. Earlier wider retrieval also abstained, so raising the source count remains an unverified remedy.

Evidence: `fee_retest.json`; earlier `system_uat_20261021/fee_retrieval_top5.json` and `fee_retrieval_top20.json`. Code: `app/chains/retrieval.py`, `app/chains/context.py`, `app/chains/prompts/answer.py`, and `app/chains/answer.py`. Reference: `evaluation/datasets/answer.jsonl`.

### Medium: caption contrast is insufficient

The Lighthouse snapshot audit measured **3.67:1** contrast for three main-area captions against its **4.5:1** criterion. The rendered foreground was `#788590`, background `#fbfcfd`, with 14-pixel normal text. Affected captions include the policy-topic hints, the suggestion-scope note, and the independent-question warning.

The automated accessibility score was **92/100**. This is an audit score, not a compliance percentage. Changing styles was outside this testing request.

Evidence: the `color-contrast` audit in `lighthouse.json`; rendered captions originate in `app/ui/app.py`. The exact source of the resolved theme colors was not isolated.

### Medium: date segments have small touch targets

The same audit flagged the month and day segments at roughly **18×20 pixels**, with insufficient spacing against its 24-pixel target criterion. These are the rendered date widget’s internal controls. Keyboard date editing worked, but that does not resolve touch usability.

Evidence: the `target-size` audit in `lighthouse.json`; `st.date_input` in `app/ui/app.py`.

### Medium: page-load layout shift is repeatable locally

Two unthrottled local reload traces measured:

| Trace | LCP | CLS |
|---|---:|---:|
| First | 304 ms | 0.24 |
| Second | 243 ms | 0.24 |

The first trace’s largest cluster scored 0.2356. The main shift had no identified cause; a much smaller shift was associated with a material-symbol font loading. The evidence does not justify attributing the whole shift to fonts.

These are local lab measurements, with warm resources on a fast machine. They do not measure real-user performance, model latency, or INP. The raw second trace is saved as `welcome_trace.json.gz`; both summaries are in `devtools_roundtrips.json`.

### Investigation candidate: quick form filling needs a regression check

One DevTools `fill` → submit attempt created feedback with an empty correction, despite an attempted marker entry. An attempted supplied reference also fell back to the matching golden reference. The initial attempt did not independently establish the text’s committed state immediately before submission, so this is **not a proven application data-loss bug**.

A separate test using native keyboard typing and Tab preserved the complete correction in MongoDB. Native keyboard entry also preserved the reviewer name, review note, and explicitly selected rejected decision. Those successful paths were verified by API readback.

Keep the fast-fill/paste path as a test candidate rather than silently passing it or assigning its cause to the application. Evidence: `feedback_initial_observation.json`, `feedback_native_keyboard.json`, `feedback_reviewed.json`, and the relevant MCP round trips.

### Shared-deployment gaps remain

The current retrieval filter still omits an institution constraint. Feedback listing and review still lack user/reviewer authorization. The earlier report explains the institution-filter probe and the single-institution corpus observed then. This pass inspected those paths and reviewed only its own synthetic records; it did not establish cross-institution exposure or perform a full security assessment.

Treat these as blockers before introducing a shared multi-institution collection or exposing reviewer functions to real users. Code: `app/chains/retrieval.py` and `app/api/feedback.py`.

## What the tests cover

| Component | Existing controlled-test evidence | Live evidence in this pass |
|---|---|---|
| Ingestion | Registered documents, parsing, clause/table boundaries, metadata, parent upserts, idempotence, stale chunks, embedding failure preservation | No corpus writes or re-ingestion performed |
| Retrieval | Date/product/confidentiality filters, parent expansion/fallback, empty results, hybrid fusion, reranking | Desktop/mobile Atlas evidence retrieval and fee reproduction |
| Answer generation | Quote membership, marker validation, abstention, context budgets, provider error handling | Fee failure, correct maximum and age answers |
| FastAPI | Validation, safe dependency failures, health/metrics behavior | All nine documented operations exercised across successes, boundary tests, and diagnostics |
| Streamlit | Chat state, retries with original scope, suggestions, reference/evaluation handling, feedback and both review decisions | Real Chrome evidence/answer modes, keyboard date input, blank input, feedback, rejected review, separate contexts, mobile source expansion |
| Evaluation | Missing references, evaluator errors, invalid/non-finite scores, one-answer/context reuse | All four scored statuses and queuing confirmed on the evaluated UI request |
| Feedback | Persistence, optional telemetry failures, institution-scoped listing, review conflict | Real MongoDB save/readback, native correction text, rejected review, overwrite protection, cleanup |
| Telemetry | Early instrumentation and correlated JSON logs | Healthy Agent, real span targets and API evaluation event; cloud pages not inspected |

Coverage here means observed behaviors and inspected tests. **Line coverage was not measured**; a coverage package was not installed. The separate banking mock API tests do not establish that customer banking tools are connected to the current policy UI. LangGraph and application MCP layers remain future work.

## Browser-method notes

Testing used the installed **Chrome DevTools MCP 1.10.1** through a temporary local stdio client. Chrome ran headlessly with `--isolated`; personal profiles were not attached. Usage statistics and CrUX integration were disabled. No permanent `.mcp.json` change was necessary.

Actions used native MCP click, keyboard, fill, navigation, and emulation tools. Page JavaScript was limited to read-only inspection. No cookies or credential storage were read, and no externally linked Datadog page was opened. A rendered Datadog link is not proof of cloud visibility.

The initial keyboard Tab reached “Skip to main content”; Enter focused the main region. Keyboard date editing selected 1 October. Blank input generated an assertive validation alert, and feedback success exposed a polite status region. These observations do not replace a screen-reader study.

No runtime console errors or warnings were listed in the inspected online states. Chrome did report three issue groups: missing form labels, missing field IDs/names, and autocomplete usage. The page accessibility tree named the main application controls; the exact elements behind those Chrome issue groups were not isolated. They remain findings, not a clean-console claim.

The offline test affected only the isolated browser page. It was not an Atlas/model/API outage injection and did not test recovery of an in-flight answer. Switching to mobile emulation reloaded the page and reset its browser session; the mobile evidence question was therefore submitted afterward, rather than treating an empty reloaded page as a populated-view pass.

Automation errors were kept separate from application failures. One output path was outside the MCP server’s default workspace, a styled radio required clicking its label, and one broad text wait returned before the new answer completed. Later snapshots and database checks established the actual outcomes. Tool success messages alone were not counted as functional passes.

## Recommended next tests

These are recommendations; no new permanent pytest cases or production fixes were added.

| Priority | Suggested test | Behavior and reason |
|---|---|---|
| High | `test_default_retrieval_includes_applicable_fee_amendment` | Use the actual UI default and check the circular plus sanction-date applicability, not just a base-policy quote |
| High | `test_fee_answer_across_sanction_cutoff` | Verify both sides of 1 July 2026 and earlier-sanction grandfathering; this is a core financial-policy rule |
| Critical before shared corpus | `test_dense_and_hybrid_retrieval_enforce_institution` | Ensure another institution’s matching chunks and parents cannot enter context |
| Critical before shared access | `test_feedback_review_requires_reviewer_role` | Keep ordinary users from listing or reviewing other users’ feedback |
| Medium | `test_pasted_feedback_and_reference_survive_immediate_submit` | Distinguish native paste/commit timing from tool behavior and detect dropped text |
| Medium | `test_mobile_captions_and_date_targets_meet_audit_criteria` | Catch the measured contrast/target-size regressions |
| Medium | `test_page_reload_layout_stays_stable` | Recheck measured CLS after a targeted layout change, using a controlled environment |

## Reproduction and saved evidence

Commands run for application checks:

```bash
.venv/bin/python -m pytest -q --junitxml=/private/tmp/nexaassist-system-tests.xml
.venv/bin/ruff check app tests
.venv/bin/ruff format --check app tests
.venv/bin/mypy app
```

The mock API suite was run through `pytest.main` with its directory added to `sys.path` and the existing temporary `openapi_spec_validator` dependency directory appended. It is not part of the default application `pytest` discovery, which points to `tests/`.

`SUMMARY.json`, `pytest.xml`, `mock_pytest.xml`, `api_boundaries.json`, and `devtools_roundtrips.json` provide the current evidence. `api_checks.py.txt` preserves the executed API probe. `desktop_evidence.png` and `mobile_evidence.png` show inspected views; the mobile image captures the expanded source at its current scroll position. Cleanup backups contain only this run’s synthetic feedback records.

The earlier broader live journey report is `../system_uat_20261021/REPORT.md`. Its 19 outcomes were not rerun wholesale or added to the fresh test count.

## Completion limits

The requested validation is complete within the recorded scope; **product correctness is not fully satisfied** because the fee defect remains. No fixes, commits, pushes, or deployments were performed.

Unverified: recruited-user usability, sustained concurrency/load, actual customer integrations, full accessibility compliance, authenticated Datadog/LangSmith cloud receipt, live infrastructure failure injection, and real re-ingestion/retirement. Passing mocked failure tests and a browser offline reload does not establish those properties.
