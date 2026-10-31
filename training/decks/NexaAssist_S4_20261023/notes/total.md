# 01_Deploy

Secure serving, reliability and cost Session 4 of 5 · 3 hours · real routes, fake dependencies Today exercises the existing FastAPI app without network access. Production-grade claims still require live staging traffic and a reviewed deployment environment.

---

# 02_Outcomes you can demonstrate

Predict 422, 429 and 503 responses. Trace input, output and resource controls. Explain why an empty metrics window cannot pass an SLO. The deliverables are an API failure matrix, a security limitation note and an operational test plan.

---

# 03_Three hours to harden the boundary

25 min serving/security + 20 min walkthrough 90 min labs, including a 10 min break 25 min SLO review + 20 min recap Use the API lab first so every learner sees failure responses before reading the relevant implementation.

---

# 04_The API owns a strict contract

Pydantic rejects invalid or extra request fields. Depends injects settings and request controls. Routers delegate; provider failures become safe 503s. Thin routers keep domain behavior reusable by both API and evaluation paths. Never expose provider exception strings in public responses. The implementation or concept reference is app/api/answer.py; app/models/retrieval.py.

---

# 05_Layer the controls around generation

Before: validate, quota and redact the query. During: bound context and output tokens. After: detect PII and verify cited quotes. These controls reduce distinct risks. None demonstrates complete injection resistance, data-loss prevention or semantic correctness.

---

# 06_Practical 1 / exercise the real API

Run: python -m training.session4.serving Observe health 200, readiness 503 and invalid input 422. Two provider failures then quota: [503, 503, 429]. ASGI transport keeps this offline. Settings and dependency behavior are injected, while routing, validation and rate-limit code remain real.

---

# 07_A failure should reveal enough to act

422 → repair the request. 429 + Retry-After → respect the quota. 503 → dependency unavailable; preserve private details. Ask learners what the UI should show for each status. The existing interface already handles rate-limit feedback separately from unavailable service errors.

---

# 08_Reuse the query PII rail

scrub_request runs before embeddings and generation. The same pattern engine masks corpus identifiers. Regex misses names and addresses and can misclassify digits. These are known limits, not a promise of complete compliance. Real data needs an approved privacy policy and evidence appropriate to its risk. The implementation or concept reference is app/services/retrieval.py; app/chains/redaction.py.

---

# 09_New / block detected PII before returning

Check answer text and evidence quotes; return the existing safe abstention. Open app/chains/answer.py and locate if any(redact(text). Read the displayed excerpt in context; it is taken directly from the application. Check answer text and evidence quotes; return the existing safe abstention. The implementation or concept reference is app/chains/answer.py.

---

# 10_Preserve citation integrity when blocking

Never rewrite a quote and still call it exact. On a detected identifier, discard the draft and citations. Log only the event; never log the sensitive text. The new rail is always applied to generated answer and quote text. Source identities and arbitrary free-form private data are not comprehensively inspected by this pattern detector.

---

# 11_Practical 2 / inspect security tests

Run input_rail, output_cap and rate_limit tests. Run test_readiness_timeout.py and the answer replay. Explain both protected cases and known detector limits. Use the complete pytest command in the handout. Extend a copy of the rate-limit exercise to three allowed requests and a fourth blocked one. The implementation or concept reference is training/session4/handout.md.

---

# 12_Resource governance has explicit bounds

Request query length is capped. CHAT_MAX_OUTPUT_TOKENS bounds answer generation. RATE_LIMIT_PER_MINUTE is a per-process quota. The shipped token cap and quota are placeholders. Multiple workers and reverse proxies change their operational meaning; a fleet limit needs a shared gateway or store. The implementation or concept reference is app/core/config.py.

---

# 13_Health and readiness answer different questions

/health: this process can respond. /ready: the configured database ping succeeds. Neither endpoint proves retrieval or answer quality. The readiness endpoint is intentionally narrower than a live RAG test. A healthy database can still have a missing or stale vector index.

---

# 14_New / put a deadline on the driver ping

The two-second driver deadline applies to readiness, not ordinary retrieval. Open app/database/mongo.py and locate def ping_database. Read the displayed excerpt in context; it is taken directly from the application. The two-second driver deadline applies to readiness, not ordinary retrieval. The implementation or concept reference is app/database/mongo.py.

---

# 15_Package the existing application

Read app/Dockerfile and Dockerfile.dockerignore. Inspect locked dependencies, non-root user and probe. Keep API secrets outside the image build context. This delivery does not claim a fresh container build. The handoff describes an earlier dummy-settings smoke test; learners should rerun their deployment checks in their environment.

---

# 16_Practical 3 / inspect operational tests

Run tests/test_slo.py and tests/test_telemetry.py. Map a request through FastAPI and workflow spans. Explain why transport-only API tests omit lifespan. The standalone serving lab does not execute startup. Separate tests cover telemetry initialization, and a live Datadog demo remains optional.

---

# 17_Measure latency, errors and priced tokens

Use /metrics/answers and app.evaluation.slo_check. Missing traffic or prices → not_measured. Process metrics do not establish a fleet-wide SLO. Latency uses a rolling window, while request/token counters are cumulative. The teaching checker makes required inputs visible but is not a full production observability backend. The implementation or concept reference is app/api/operations.py; app/evaluation/slo_check.py.

---

# 18_Cost follows measured tokens

Cost = (input tokens × input price + output tokens × output price) / 1M. Monthly estimate = priced query cost × expected query volume. Verify current provider prices before the live exercise. Use approved prices and a representative request mix. No current model availability or price is asserted by these slides; historical saved prices may be stale.

---

# 19_Streaming needs a separate contract

Current answers are buffered and validated as a whole. Total generation time does not measure TTFT or TPS. Streaming requires deciding when validated content may leave. TTFT means time to first token; TPS means tokens per second. They are discussed as future metrics rather than inferred from the current generation_ms field.

---

# 20_Conversation state changes the problem

Session history changes privacy and retrieval scope. Query rewriting needs its own failure behavior and evals. LangGraph and action tools remain future layers. The course discusses orchestration; this project deliberately remains stateless per question. The architecture is extended only when a concrete requirement justifies that cost.

---

# 21_Exit gate / can we serve it responsibly?

Submit API failure matrix and limitation note. Define representative staging traffic and approved budgets. Hold a live release when required SLOs are unmeasured. A fake returning 503 proves error handling. It does not prove readiness recovery, production capacity or model quality under load.

---

# 22_Next / detect, investigate and recover

Carry the quality and operational evidence forward. Bring one regression and one misleading feedback item. Session 5 rehearses the operating loop. The operating loop connects traces, reviewed feedback, golden cases and reversible configuration. It begins after deployment rather than ending there.
