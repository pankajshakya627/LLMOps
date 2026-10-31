# 01_Deploy

Secure serving, reliability and cost Session 4 of 5 · 3 hours · source-aligned workshop Today exercises the existing FastAPI app without network access. Production-grade claims still require live staging traffic and a reviewed deployment environment. This revised deck follows the course lesson sequence; exact lesson URLs appear in section notes and the coverage map.

---

# 02_Outcomes you can demonstrate

Predict 422, 429 and 503 responses. Trace input, output and resource controls. Explain why an empty metrics window cannot pass an SLO. The deliverables are an API failure matrix, a security limitation note and an operational test plan.

---

# 03_Three hours to harden the boundary

25 min serving/security + 20 min walkthrough 90 min labs, including a 10 min break 25 min SLO review + 20 min recap Use the API lab first so every learner sees failure responses before reading the relevant implementation.

---

# 04_Showcase / the service fails safely

Provider failure → private details stay private. Repeated calls → the configured quota applies. Database failure → readiness reports unavailable. Use actual FastAPI routing, dependency injection, limiter and schemas with fake dependencies. Readiness tests a database ping, not vector-index availability.

---

# 05_Run the serving-failure demonstration

python -m training.showcase --session 4 Provider failures then quota: [503, 503, 429]. Invalid input: 422; failed readiness: 503. Allow 20 minutes. Predict which requests consume quota. The driver deadline is covered separately and is not a hard wall-clock guarantee. Limits are per process/client; this is not a distributed quota.

Code walkthrough: app/database/mongo.py
def ping_database(settings: Settings) -> None:
    """Bound the readiness probe without shortening normal query deadlines."""
    with timeout(2):
        _database(settings).command("ping")

Status, retry behavior and response privacy. Measure latency and cost under representative traffic. Offline failures establish no capacity target. Retain an HTTP transcript. Explain health versus readiness and unknown versus passing measurements. Prices and SLO targets remain placeholders pending owner confirmation.

---

# 06_Security, Compliance, and Responsible Operation in LLMOps

Educative lesson 11 Concept → worked example → NexaAssist application This section follows the lesson Security, Compliance, and Responsible Operation in LLMOps. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops.

---

# 07_Grounded output can still be unsafe

A source may contain private information. A user may request an unauthorized disclosure. A safe-looking request can consume excessive resources. Correctness and safety are different dimensions. A faithful reproduction of restricted information is still a privacy problem. The source organizes its security discussion around input, output and resource controls. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops.

---

# 08_Recognize direct and indirect injection

Direct: the user tries to override the assistant’s rules. Indirect: retrieved material contains hostile instructions. Defend at data, prompt, authorization and output boundaries. Do not teach a list of forbidden words as complete injection protection. Text can be phrased or encoded many ways. Retrieved documents are untrusted data even when their surrounding system is useful. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops.

---

# 09_Risk names are stable; numbering is versioned

The lesson uses older OWASP LLM01 / LLM04 / LLM06 labels. OWASP 2025 maps disclosure to LLM02 and consumption to LLM10. Record the list version when naming a risk. Verified against https://genai.owasp.org/llm-top-10/ on 2026-10-23. Prompt injection remains LLM01:2025. Explain the source’s historical numbering without presenting it as the current taxonomy. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops.

---

# 10_Layer the controls around generation

Before: validate, quota and redact the query. During: bound context and output tokens. After: detect PII and verify cited quotes. These controls reduce distinct risks. None demonstrates complete injection resistance, data-loss prevention or semantic correctness. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops.

---

# 11_Reuse the query PII rail

scrub_request runs before embeddings and generation. The same pattern engine masks corpus identifiers. Regex misses names and addresses and can misclassify digits. These are known limits, not a promise of complete compliance. Real data needs an approved privacy policy and evidence appropriate to its risk. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops. The implementation or concept reference is app/services/retrieval.py; app/chains/redaction.py.

---

# 12_New / block detected PII before returning

Check answer text and evidence quotes; return the existing safe abstention. Open app/chains/answer.py and locate if any(redact(text). Read the displayed excerpt in context; it is taken directly from the application. Check answer text and evidence quotes; return the existing safe abstention. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops. The implementation or concept reference is app/chains/answer.py.

---

# 13_Preserve citation integrity when blocking

Never rewrite a quote and still call it exact. On a detected identifier, discard the draft and citations. Log only the event; never log the sensitive text. The new rail is always applied to generated answer and quote text. Source identities and arbitrary free-form private data are not comprehensively inspected by this pattern detector. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops.

---

# 14_Practical 2 / inspect security tests

Run input_rail, output_cap and rate_limit tests. Run test_readiness_timeout.py and the answer replay. Explain both protected cases and known detector limits. Use the complete pytest command in the handout. Extend a copy of the rate-limit exercise to three allowed requests and a fourth blocked one. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops. The implementation or concept reference is training/session4/handout.md.

---

# 15_Resource governance has explicit bounds

Request query length is capped. CHAT_MAX_OUTPUT_TOKENS bounds answer generation. RATE_LIMIT_PER_MINUTE is a per-process quota. The shipped token cap and quota are placeholders. Multiple workers and reverse proxies change their operational meaning; a fleet limit needs a shared gateway or store. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops. The implementation or concept reference is app/core/config.py.

---

# 16_Treat residual risk as part of the result

Patterns cover selected identifiers, not all personal data. Quotas are per process; proxy behavior affects client identity. Authorization and retention still need deployment decisions. Keep the source’s defense-in-depth lesson, while avoiding a claim that these controls alone make the service suitable for public internet exposure. NexaAssist remains a training app with explicit live and organizational gaps. Source lesson: https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops.

---

# 17_Inference Infrastructure: Hardware, Economics, and Latency

Educative lesson 12 Concept → worked example → NexaAssist application This section follows the lesson Inference Infrastructure: Hardware, Economics, and Latency. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 18_Split response time into useful measurements

TTFT: request start until the first output token. TPS: generation rate after output begins. End-to-end latency also includes queues and retrieval. A buffered API cannot expose user-visible TTFT from generation_ms. Streaming can improve perceived progress, but does not remove prompt processing or queueing delays. Targets should follow the product’s usage rather than universal numbers. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 19_Weight memory is only the starting estimate

Approximate decimal GB = parameter billions × bytes/parameter. Scenario: 8B × 2 bytes = 16 GB for FP16 weights. Reserve additional memory for cache, runtime and concurrency. This is a weight-size lower-bound estimate, not a complete GPU purchase recommendation. Runtimes can shard or offload models; memory layout, kernels and architecture influence feasibility. No hardware performance measurement is supplied. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 20_Quantization changes the weight budget

FP16 uses roughly 2 bytes per parameter. INT8 uses roughly 1; packed INT4 roughly 0.5. Quality, kernel support and metadata overhead still matter. Scenario: idealized 8B INT4 weights use about 4 decimal GB before overhead. Quantization is not a guarantee of identical behavior or usable throughput. Re-evaluate the actual model and task after changing precision. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 21_The KV cache grows with workload shape

Longer context requires more cached attention state. Concurrent sequences increase the live memory footprint. A model loading successfully does not prove capacity. KV memory depends on layer count, attention layout, sequence length, precision and batch size. Avoid treating a fixed “GB per 4000 tokens” number as universal. Capacity must be measured with the intended context and concurrency. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 22_API versus self-hosting is a utilization decision

API: variable token cost plus provider limits and governance. Self-hosting: fixed capacity cost plus operating effort. Compare representative traffic, privacy and reliability needs. Provider quotas, availability and network behavior limit effective scalability; API scale is not unlimited. A steady high-volume workload may justify owned capacity, while a bursty one may not. Use total cost, not token price alone. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 23_Separate input and output prices in the estimate

Scenario: 1,000 queries/day, 500 input + 200 output tokens. At $0.10/$0.50 per 1M: $0.15/day, $4.50/30 days. These are scenario prices, not a current provider quote. Compute input and output cost independently: 500,000 input tokens cost $0.05 and 200,000 output tokens cost $0.10. Multiply by 30 for this illustrative month. Include failed calls, retries, judges and embeddings in a complete estimate. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 24_Parallelism and batching solve different constraints

Replicas distribute requests when a model fits per worker. Sharding distributes a model that needs multiple devices. Batching trades queue delay for better resource utilization. The source covers data parallelism, model parallelism and asynchronous batching. None guarantees linear throughput in practice. Observe provider rate limits, memory pressure and per-request latency when tuning concurrency. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 25_Practical / calculate capacity and spend

Run: python -m training.session4.capacity Verify weight-only estimates and scenario token costs. Write down the missing cache, runtime and concurrency inputs. The calculation is deterministic and offline. It demonstrates arithmetic and assumptions, not a live hardware sizing or pricing recommendation. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 26_Measure latency, errors and priced tokens

Use /metrics/answers and app.evaluation.slo_check. Missing traffic or prices → not_measured. Process metrics do not establish a fleet-wide SLO. Latency uses a rolling window, while request/token counters are cumulative. The teaching checker makes required inputs visible but is not a full production observability backend. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency. The implementation or concept reference is app/api/operations.py; app/evaluation/slo_check.py.

---

# 27_Streaming needs a separate contract

Current answers are buffered and validated as a whole. Total generation time does not measure TTFT or TPS. Streaming requires deciding when validated content may leave. TTFT means time to first token; TPS means tokens per second. They are discussed as future metrics rather than inferred from the current generation_ms field. Source lesson: https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency.

---

# 28_Hosting, Serving, and Scaling LLMs in Production

Educative lesson 13 Concept → worked example → NexaAssist application This section follows the lesson Hosting, Serving, and Scaling LLMs in Production. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 29_Async endpoints still need non-blocking internals

Await asynchronous provider and HTTP clients. Offload synchronous database/file work explicitly. FastAPI does not offload every utility called inside async def. The source text overstates automatic threadpool handling. Official FastAPI documentation distinguishes synchronous path operations/dependencies from ordinary utility calls. NexaAssist explicitly uses asyncio.to_thread for synchronous PyMongo work. Reference: https://fastapi.tiangolo.com/async/. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 30_The API owns a strict contract

Pydantic rejects invalid or extra request fields. Depends injects settings and request controls. Routers delegate; provider failures become safe 503s. Thin routers keep domain behavior reusable by both API and evaluation paths. Never expose provider exception strings in public responses. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production. The implementation or concept reference is app/api/answer.py; app/models/retrieval.py.

---

# 31_Practical 1 / exercise the real API

Run: python -m training.session4.serving Observe health 200, readiness 503 and invalid input 422. Two provider failures then quota: [503, 503, 429]. ASGI transport keeps this offline. Settings and dependency behavior are injected, while routing, validation and rate-limit code remain real. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 32_A failure should reveal enough to act

422 → repair the request. 429 + Retry-After → respect the quota. 503 → dependency unavailable; preserve private details. Ask learners what the UI should show for each status. The existing interface already handles rate-limit feedback separately from unavailable service errors. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 33_Dependency injection defines resource ownership

Create or cache shared clients with clear lifecycle. Inject application settings and replace services in tests. Keep domain logic callable outside HTTP routes. Depends is a wiring mechanism, not a blanket singleton or startup guarantee. Resource ownership must be explicit in lifespan, caches or dependencies. The current service/chain split lets evaluation replay the same logic. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 34_Health and readiness answer different questions

/health: this process can respond. /ready: the configured database ping succeeds. Neither endpoint proves retrieval or answer quality. The readiness endpoint is intentionally narrower than a live RAG test. A healthy database can still have a missing or stale vector index. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 35_New / put a deadline on the driver ping

The two-second driver deadline applies to readiness, not ordinary retrieval. Open app/database/mongo.py and locate def ping_database. Read the displayed excerpt in context; it is taken directly from the application. The two-second driver deadline applies to readiness, not ordinary retrieval. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production. The implementation or concept reference is app/database/mongo.py.

---

# 36_Package the existing application

Read app/Dockerfile and Dockerfile.dockerignore. Inspect locked dependencies, non-root user and probe. Keep API secrets outside the image build context. This delivery does not claim a fresh container build. The handoff describes an earlier dummy-settings smoke test; learners should rerun their deployment checks in their environment. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 37_Practical 3 / inspect operational tests

Run tests/test_slo.py and tests/test_telemetry.py. Map a request through FastAPI and workflow spans. Explain why transport-only API tests omit lifespan. The standalone serving lab does not execute startup. Separate tests cover telemetry initialization, and a live Datadog demo remains optional. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 38_A reproducible image still needs safe deployment

Freeze dependencies and build with an excluded-secret context. Inject secrets at runtime; do not COPY .env into images. Review networking, readiness and rollout in the target platform. The source Docker example includes COPY .env while later advising runtime secrets. The revised training follows the runtime-secret practice and existing dockerignore. No cloud provider deployment is assumed or performed. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 39_Cost follows measured tokens

Cost = (input tokens × input price + output tokens × output price) / 1M. Monthly estimate = priced query cost × expected query volume. Verify current provider prices before the live exercise. Use approved prices and a representative request mix. No current model availability or price is asserted by these slides; historical saved prices may be stale. Source lesson: https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production.

---

# 40_Exit gate / can we serve it responsibly?

Submit API failure matrix and limitation note. Define representative staging traffic and approved budgets. Hold a live release when required SLOs are unmeasured. A fake returning 503 proves error handling. It does not prove readiness recovery, production capacity or model quality under load.

---

# 41_Next / detect, investigate and recover

Carry the quality and operational evidence forward. Bring one regression and one misleading feedback item. Session 5 rehearses the operating loop. The operating loop connects traces, reviewed feedback, golden cases and reversible configuration. It begins after deployment rather than ending there.
