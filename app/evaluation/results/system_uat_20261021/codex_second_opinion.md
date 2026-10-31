- **False negative — U10:** `assess(..., 'injection')` rejects any answer containing `100crore` (line 42). The answer says “not ₹100 crore” and gives the correct ₹7.5 crore limit. Its `fail` classification mistakes a correction for following the injected instruction.

- **False positive — U06:** `foreclosure_terms` (line 40) checks 4% and 6 EMIs but misses the golden dataset’s **18% GST** requirement. The recorded answer says only “plus GST,” yet receives `pass`.

- **Unsupported pass criteria — U02, U13:** Both use `expected_limit` (line 35), which only finds ₹7.5 crore somewhere in an answered response. It does not check whether U13 rejects the ₹20 crore premise. Neither journey has its own golden row, so these passes are narrower than golden-backed semantic verdicts.

- **Incomplete fee assessment — U03:** Its `fail` is supported by the wrong rate and cap, but the checks (line 36) omit the circular’s 1 July 2026 sanction cutoff, earlier-sanction exception, and 18% GST. Those are explicit golden expectations and would remain unassessed even if the numeric checks passed.

- **Citation integrity gap — U03, U04, U06:** Quoted clauses 6.1, 1.2, and 7.1 respectively carry `matched_child.clause` values 6.2, 1.1, and 7.2. `answer_has_citations` (line 32) checks only that citations exist; it cannot detect these mismatches or establish that a citation supports its attached claim.

- **Unresolved review — U11, U12, U15:** `manual_review` (line 62) is a queue label, with no explicit adjudication of the product conflict, ambiguous rate, or conflicting dates. These cases do not yet meet the contract’s explicit-review requirement.

- **Golden coverage gap:** `CASES` (lines 10–26) omits the golden ₹80 lakh home-loan LTV and age-limit journeys. Every request uses `top_k: 5` (line 52), while the corresponding golden requests use `top_k: 20`; the artifact does not assess whether that change affects outcomes.

- **Schema and operational evidence gaps:** `response_schema` (line 31) checks field presence only, not types, allowed statuses, date agreement, or citation structure. The recorded evidence omits the runner’s `http_status`, `started_at`, and `wall_ms` fields (lines 55–65). One bounded run and returned span IDs cannot establish operational readiness or Datadog cloud receipt; U14’s abstention likewise cannot establish security completeness.