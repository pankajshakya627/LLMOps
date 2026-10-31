# Brooks-Lint Review

**Mode:** Test Quality Review
**Scope:** All 37 default-suite test files, the synthetic banking API suite, and
the explicitly invoked Phoenix SDK checks. No `.brooks-lint.yaml` was present.
**Health Score:** 95/100
**Trend:** First run — no trend data.

The suite provides fast, useful behavior coverage; a passing result does not
establish a hard active-client memory bound or complete live-service quality.

## Test Suite Map

```text
Unit/contract emphasis:                 29 files, 157 test functions
Offline integration/CLI/UI emphasis:     8 files,  46 test functions
Synthetic banking API:                  1 file,   22 collected cases
Phoenix SDK integration (opt-in):        1 file,    4 collected cases
Real-browser E2E:                        0 executed; driver preflight blocked
```

File categories are approximate: some contract files also use FastAPI TestClient.
They are not measured test-pyramid percentages. Parametrization expands default
test functions to 306 cases; the banking suite adds 22. See `suite_map.json`.

The final application/offline run completed 328 cases in 35.85 seconds. The
separate pinned Phoenix SDK run completed four cases in 2.61 seconds. Longer
setup blocks are mostly at provider/storage boundaries. No runtime-only
production helpers were added to support these tests.

## Findings

### Warning

**T5 — Coverage Illusion: idle eviction does not establish a hard client bound**

**Symptom:** `tests/test_rate_limit.py:49` verifies removal of expired clients and
names the behavior as keeping memory bounded. In `app/core/rate_limit.py:35`,
reaching `max_clients` triggers a purge, but `:37` then adds another identity even
when every existing identity remains active. A fixed-clock probe with
`max_clients=3` retained 100 distinct active identities.

**Source:** Roy Osherove, *The Art of Unit Testing* — test completeness; Google,
*How Google Tests Software* — change coverage versus line coverage.

**Consequence:** a burst of distinct clients can grow memory beyond the apparent
threshold, and each subsequent request can rescan the active map. Passing the
idle-client test does not protect this resource boundary.

**Remedy:** agree on a full-capacity policy, such as rejecting new identities
until capacity expires, then add an active-client-capacity regression and
implement that policy without allowing established clients to bypass limits.
Production code was not changed in this test-writing task. The deterministic
reproduction is included in `VALIDATION.md`.

## Diagnosis by risk

| Risk | Observed assessment |
|---|---|
| T1, obscurity | Shared settings previously inherited process variables despite `_env_file=None`. The fixture now clears setting-related variables. A hostile-environment check passed 40 cases. |
| T2, brittleness | Some training transcript assertions intentionally pin curriculum output. No refactor history exists to establish systemic refactor failures. Multiple assertions in the UI workflow describe its coherent review/export journey. |
| T3, duplication | No finding established. Similar unit and integration scenarios test different boundaries; small local setup remains clearer than a general fixture framework. |
| T4, mock abuse | Existing isolated service tests remain useful. New pipeline tests keep real routing, services, retrieval/context chains, SDK structured parsing, citations, usage accounting and feedback logic; only external boundaries are isolated. |
| T5, coverage illusion | One unresolved finding above. Real Atlas search, provider semantics and browser rendering remain distinct from fake-boundary results. |
| T6, architecture mismatch | No inverted/slow pyramid established: the offline run is under one minute. Optional SDK/tool environments remain separate from the Python 3.14 base suite. |

These conclusions follow the reviewed principles of Meszaros (*xUnit Test
Patterns*: Mystery Guest, Eager Test and Slow Tests), Osherove (isolation and mock
completeness), and Feathers (*Working Effectively with Legacy Code*: sensing and
separation). A mock at an external boundary is not itself a defect. No fixed
70:20:10 ratio or coverage percentage was treated as a release requirement.

## Summary

The most useful follow-up is the active-client-capacity policy and its regression
test. The added transport/parser and Phoenix SDK checks improve confidence in
real boundaries while preserving fast offline feedback. Human-reviewed model
quality and browser evidence are still required for release decisions.
