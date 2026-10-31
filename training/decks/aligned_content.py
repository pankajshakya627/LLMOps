"""Lesson-aligned courseware, based on all sixteen Safari lesson reads."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from training.decks.compact_content import compact_sessions
from training.decks.course_content import SESSIONS as ORIGINAL
from training.decks.course_content import page
from training.decks.showcase_content import SHOWCASES

BASE_URL = "https://www.educative.io/courses/llmops/"
LESSONS = [
    ("What Is LLMOps, and Why Does It Exist?", "what-is-llmops-and-why-does-it-exist"),
    ("How We Reached LLMOps", "how-we-reached-llmops"),
    ("MLOps to LLMOps: What Changes and What Stays", "mlops-to-llmops-what-changes-and-what-stays"),
    (
        "The 4D Framework (Discover, Distill, Deploy, Deliver)",
        "the-4d-framework-discover-distill-deploy-deliver",
    ),
    (
        "Architecture of a Retrieval-Augmented Generation Application",
        "architecture-of-a-retrieval-augmented-generation-application",
    ),
    (
        "Scoping and Planning a Production RAG Application",
        "scoping-and-planning-a-production-rag-application",
    ),
    ("Data Foundations for LLMOps", "data-foundations-for-llmops"),
    ("Embeddings, Vector Storage, and Evaluation", "embeddings-vector-storage-and-evaluation"),
    (
        "Prompt Engineering and Prompt Life Cycle Management",
        "prompt-engineering-and-prompt-life-cycle-management",
    ),
    (
        "Evaluation of LLM Outputs: Metrics, Tests, and Human Feedback",
        "evaluation-of-llm-outputs-metrics-tests-and-human-feedback",
    ),
    (
        "Security, Compliance, and Responsible Operation in LLMOps",
        "security-compliance-and-responsible-operation-in-llmops",
    ),
    (
        "Inference Infrastructure: Hardware, Economics, and Latency",
        "inference-infrastructure-hardware-economics-and-latency",
    ),
    (
        "Hosting, Serving, and Scaling LLMs in Production",
        "hosting-serving-and-scaling-llms-in-production",
    ),
    ("Orchestration and Application Logic", "orchestration-and-application-logic"),
    (
        "Quality, Human-in-the-Loop, and Governance Systems",
        "quality-human-in-the-loop-and-governance-systems",
    ),
    ("Future Directions in LLMOps", "future-directions-in-llmops"),
]


def old(session: int, *numbers: int) -> list[dict[str, Any]]:
    return [deepcopy(ORIGINAL[session - 1]["slides"][n - 1]) for n in numbers]


def lesson(number: int, *slides: dict[str, Any]) -> list[dict[str, Any]]:
    title, slug = LESSONS[number - 1]
    result = [
        page(
            title,
            f"Educative lesson {number:02d}",
            "Concept → worked example → NexaAssist application",
            kind="section",
            note=f"This section follows the lesson {title}. Teach the concept first, then distinguish the existing NexaAssist implementation from proposed extensions. The slides paraphrase the source rather than reproduce its text.",
        )
    ] + list(slides)
    for slide in result:
        slide["lesson"] = number
        slide["lesson_title"] = title
        slide["lesson_url"] = BASE_URL + slug
        slide["note"] += f" Source lesson: {BASE_URL + slug}."
    return result


def diagram(
    title: str, nodes: list[tuple[str, str]], edges: list[tuple[int, int, str]], note: str
) -> dict[str, Any]:
    slide = page(
        title, *[label + ": " + detail for label, detail in nodes], kind="diagram", note=note
    )
    slide["nodes"] = nodes
    slide["edges"] = edges
    return slide


s1 = old(1, 1, 3, 4)
s1 += lesson(
    1,
    page(
        "LLMOps manages behavior under real constraints",
        "Correctness and safety are part of the product.",
        "Latency shapes whether people can use the service.",
        "Token consumption determines variable cost.",
        note="Start with a staff policy assistant that gives fluent but unsupported advice. Ask which operational signal reveals each problem. A fast HTTP response, cheap model or well-written prompt does not establish all three dimensions at once.",
    ),
    page(
        "From a convincing demo to an operated service",
        "A demo tests a few questions in a controlled setting.",
        "Production introduces changing data, users and traffic.",
        "The remedy is a repeatable evaluation and release loop.",
        note="Use a new original example: a policy amendment changes a fee while the old corpus remains indexed. The application code is unchanged, yet the answer becomes stale. Grounding, data refresh, traceability and reviewed release evidence belong in the system design.",
    ),
    *old(1, 5),
)
s1 += lesson(
    2,
    diagram(
        "AI, ML, GenAI and LLMs describe different scopes",
        [
            ("AI", "Goal-directed systems"),
            ("ML", "Learns patterns from data"),
            ("GenAI", "Creates new artifacts"),
            ("LLMs", "Language-generating models"),
        ],
        [(0, 1, "includes"), (1, 2, "includes"), (2, 3, "includes")],
        "Read these as a conceptual subset chain, not a deployment pipeline. AI also includes approaches that do not learn. LLMs are one kind of generative model, while RAG is an application pattern around a model.",
    ),
    page(
        "The operational burden moved toward integration",
        "Research focused on building and training models.",
        "Interactive interfaces broadened access to generation.",
        "Applications now coordinate data, APIs and model behavior.",
        note="The source illustrates a research period, a major interface shift in 2022, and a subsequent integration era. These are historical teaching phases, not a claim that training disappeared. In an API-backed app the team owns orchestration and data even when it does not own weights.",
    ),
    page(
        "The artifact gap and the closed-box problem",
        "Prompts, embeddings and knowledge can change separately.",
        "Remote model internals are usually outside our control.",
        "Debug using observed inputs, evidence, outputs and versions.",
        note="Do not claim that all classical models are explainable or that replay is impossible. The practical limitation is that hosted generation can vary and model internals are unavailable. Capture the surrounding artifacts so regressions can be localized empirically.",
    ),
)
s1 += lesson(
    3,
    page(
        "Keep the software-engineering foundation",
        "Version control and CI still coordinate changes.",
        "Containers and reproducible dependencies still matter.",
        "Infrastructure configuration still needs review and rollback.",
        note="LLMOps extends existing engineering practice. Unit tests remain useful for deterministic logic; semantic evaluations add a different form of evidence. The current project has a lock file, Docker packaging and tests; CI and infrastructure-as-code are separate gaps.",
    ),
    diagram(
        "What changes from MLOps to LLMOps",
        [
            ("Data", "Features → documents + vectors"),
            ("Tuning", "Parameters → prompts + retrieval"),
            ("Artifacts", "Weights → coupled runtime assets"),
            ("Evaluation", "Labels → semantic criteria"),
        ],
        [],
        "These are parallel comparison dimensions, not an ordered pipeline. Traditional ML still uses data and LLM systems can still be fine-tuned. This view highlights the primary levers in an API-backed RAG application.",
    ),
    page(
        "Semantic drift needs meaning-aware evidence",
        "Different words can express the same request.",
        "Similar words can refer to different domains.",
        "Replay representative cases and review emerging topics.",
        note="Use banking versus river-bank questions as a conceptual ambiguity example. Distribution statistics alone do not establish equivalent meaning. NexaAssist currently compares golden-run scores and collects feedback; it does not implement a topic-drift detector.",
    ),
)
s1 += lesson(
    4,
    diagram(
        "Four phases, four decisions",
        [
            ("Discover", "Problem + permitted data"),
            ("Distill", "Prove retrieval and generation"),
            ("Deploy", "Validate the serving envelope"),
            ("Deliver", "Observe and improve"),
        ],
        [(0, 1, "scope"), (1, 2, "quality"), (2, 3, "SLO")],
        "The stages form a recurring lifecycle; the drawing shows one pass. Reviewed failures feed the next discovery and experimentation cycle. A phase gate needs a named artifact and an explicit decision.",
    ),
    page(
        "Discover produces an operating contract",
        "Define who asks what and which outcomes are excluded.",
        "Identify sources, freshness, permissions and disclosure.",
        "Name proposed quality, latency and cost criteria.",
        note="The data-governance decision can stop development even when a model demo works. Document who owns approval rather than inventing risk ratings or assuming an internal document may be sent to a provider.",
    ),
    page(
        "Distill produces evidence, not a favorite prompt",
        "Tune chunking, retrieval, prompt and model together.",
        "Use reviewed cases and capture per-case failures.",
        "Separate a missing source from unsupported generation.",
        note="The source places golden evaluation before deployment. In this workshop the deterministic labs run without network access; optional pre-release evaluation may call real providers. Neither a single good answer nor a valid schema is sufficient.",
    ),
    page(
        "Deploy and Deliver require different evidence",
        "Deploy: representative traffic within approved budgets.",
        "Deliver: quality signals, reviewed failures and recovery.",
        "Missing measurements remain unknown, not successful.",
        note="The course includes example quality and SLO numbers. They are not universal targets. In this repository gates.json explicitly labels its values as placeholders; the business and operational owners must confirm them.",
    ),
    *old(1, 19),
)
s1 += lesson(
    5,
    diagram(
        "RAG separates knowledge preparation from answering",
        [
            ("Sources", "Registered policy documents"),
            ("Ingestion", "Parse, redact, embed, upsert"),
            ("Knowledge", "Vectors + parent sections"),
            ("Inference", "Retrieve, prompt, generate"),
        ],
        [(0, 1, "load"), (1, 2, "write"), (2, 3, "search")],
        "Ingestion optimizes throughput, repeatability and data integrity. Online inference optimizes request latency and answer quality. Traceability links an answer back through the exact source version. The full interactive reference architecture is supplied alongside the deck.",
    ),
    page(
        "Freshness, permission and traceability are separate",
        "A fresh document can still be unauthorized.",
        "A permitted document can still be obsolete.",
        "An answer needs a recoverable source identity.",
        note="Data divergence is the gap between expected knowledge and what the index contains. In NexaAssist, effective-date and metadata filters constrain retrieval and provenance preserves source references. Corpus freshness approvals are still owner decisions.",
    ),
    page(
        "Repeated ingestion needs three guarantees",
        "Stable identities prevent duplicate accumulation.",
        "Compatible versions prevent mixed embedding spaces.",
        "Failure isolation preserves progress and exposes bad files.",
        note="The project has deterministic checksums and per-document failure isolation. The source discusses immutable candidate indexes and dead-letter handling; automatic blue/green promotion and a durable dead-letter queue are not implemented here.",
    ),
    page(
        "Budget the online path before adding hops",
        "Scenario: 2,000 ms total minus 1,500 ms generation.",
        "That leaves 500 ms for queueing, retrieval and overhead.",
        "Parallelism, caching and model choice require measurement.",
        note="The numbers are scenario data, not a measured NexaAssist SLO. Retrieval caching must include permissions, corpus version and freshness. A cache hit is not inherently free or safe, and no semantic cache is added by these slides.",
    ),
    *old(1, 9, 10),
)
s1 += lesson(
    6,
    page(
        "The source course builds an internal support assistant",
        "Staff search internal policies and tool instructions.",
        "The response must be grounded and cite its documentation.",
        "A use-case manifest keeps later scope changes reviewable.",
        note="The source uses a fictional Halluli support project with HR and internal-tool documents. NexaAssist applies the same operating principles to synthetic banking policy. Do not mix the two corpora or pretend their contracts are identical.",
    ),
    page(
        "Translate the stack without losing the lesson",
        "Course: FastAPI, PostgreSQL/pgvector, LiteLLM, Docker.",
        "NexaAssist: FastAPI, MongoDB Atlas, LangChain, Docker.",
        "Preserve responsibilities, validation and evaluation gates.",
        note="The database and model interface are explicit adaptations required by CLAUDE.md. The course uses a single database for converged operational data. NexaAssist uses Atlas collections for vectors, parents and feedback. No PostgreSQL migration or extra framework is introduced.",
    ),
    *old(1, 11, 12, 17),
    page(
        "Map the interface boundary honestly",
        "Course examples describe /ingest and /chat.",
        "NexaAssist uses an ingestion CLI and /answer routes.",
        "Operational traces and feedback retain answer context.",
        note="Endpoint names are not the architectural principle. Administrative ingestion stays outside public user serving, and the exact NexaAssist paths come from the API modules. The source lesson itself varies between HR and technical-support examples; our manifest consistently uses policy lookup.",
    ),
)
s1 += old(1, 14, 15, 16, 20, 21, 22)

s2 = old(2, 1, 2, 3)
s2 += lesson(
    7,
    page(
        "Documents carry meaning through structure",
        "Tables, headers and code blocks define useful boundaries.",
        "Extraction can mix unrelated columns and page furniture.",
        "Inspect representative parsed output before embedding.",
        note="The course starts with Markdown and recursive splitting. NexaAssist adds layout-aware PDF parsing and clause boundaries. A parser that runs successfully can still produce semantically damaged text; the chunking lab makes that visible.",
    ),
    *old(2, 5),
    page(
        "Embed-ETL has a safety order",
        "Parse and normalize → inspect structure.",
        "Redact sensitive fields → define stable chunk metadata.",
        "Only then compute embeddings and publish searchable data.",
        note="Embedding can disclose text to a provider as well as create a stored representation. The practical lesson is to remove sensitive material before that boundary and retain deletion/version metadata. Avoid the absolute claim that all embeddings are impossible to delete: known records can be retired, but hidden sensitive content is hard to locate.",
    ),
    *old(2, 6, 7, 8, 9, 10, 11),
    page(
        "Exercise / preserve the complete policy condition",
        "Find one table, one exception and one date caveat.",
        "Show the child text and its parent context.",
        "Explain which change could create an incomplete answer.",
        kind="lab",
        note="Use the actual synthetic PDF and existing chunks lab. Record the clause identity rather than only a character count. Expected learning: a smaller search unit needs enough surrounding context to preserve an exception, and larger chunks can weaken ranking.",
    ),
)
s2 += lesson(
    8,
    page(
        "An embedding is a representation, not an answer",
        "A model maps text into numeric coordinates.",
        "Similarity helps rank candidates; it does not prove authority.",
        "Use the same compatible model and dimension schema.",
        note="The source uses LiteLLM with provider embeddings and PostgreSQL vector columns. NexaAssist obtains integration-specific embeddings and explicitly configures Atlas dimensions. A nominally equal dimension count does not make two embedding models interchangeable.",
    ),
    page(
        "Approximate search trades exhaustive work for speed",
        "Nearest-neighbor structures avoid scanning every vector.",
        "Index settings affect latency and candidate recall.",
        "Measure expected sources under the actual filters.",
        note="HNSW is an example of approximate nearest-neighbor indexing, not an application-level correctness guarantee. The live Atlas configuration is documented locally. Do not manufacture cluster parameters or claim a throughput benchmark from an offline fake.",
    ),
    *old(2, 12, 13, 14, 15, 16),
    page(
        "Hit rate and multi-reference recall are different",
        "Single expected source: hit or miss among top-k.",
        "Multiple expected clauses: fraction of required references found.",
        "MRR adds where the first expected item appears.",
        note="The source labels its single-reference hit-rate exercise Recall@K. NexaAssist can require multiple clauses, so it reports reference recall separately. For two required clauses and one found, recall is one-half; an any-hit metric would hide the missing condition.",
    ),
    *old(2, 17, 18),
    page(
        "Version the retrieval artifact as a compatible set",
        "Record parser/chunker settings and embedding identity.",
        "Build a candidate knowledge snapshot.",
        "Evaluate before changing the serving configuration.",
        note="Changing embeddings or splitting changes retrieval behavior. The source proposes rebuilding a separate index version. Our code supports incremental upserts; immutable snapshots and traffic promotion are future operational capabilities.",
    ),
    page(
        "The course retrieval CI gate is an example",
        "Source example: fail when single-reference hit rate < 0.90.",
        "NexaAssist has local recall gates with placeholder targets.",
        "A live Atlas test needs a real compatible candidate index.",
        note="Do not claim that a local MongoDB container supplies Atlas Vector Search. CI should distinguish offline control-flow tests from a credentialed integration gate, and dataset owners must approve actual thresholds.",
    ),
    *old(2, 19, 20),
)
s2 += old(2, 21, 22)

s3 = old(3, 1, 2, 3)
s3 += lesson(
    9,
    *old(3, 4),
    diagram(
        "A production prompt separates three concerns",
        [
            ("Instructions", "Role, scope and abstention"),
            ("Untrusted data", "Question + retrieved documents"),
            ("Output contract", "Typed status + exact citations"),
        ],
        [(0, 1, "constrain"), (1, 2, "validate")],
        "The relationship is constraint and validation, not a claim that delimiters confer authority. System-role rules remain separate from untrusted user/context content. The source uses Jinja templates and XML; NexaAssist uses ChatPromptTemplate and JSON-serialized evidence.",
    ),
    page(
        "Delimiters mark structure; they do not stop every attack",
        "Wrap untrusted content with explicit boundaries.",
        "Escape delimiter-like content before rendering examples.",
        "Keep privileged instructions outside the data field.",
        note="The shared answer chain now escapes every human-message variable, wraps request/evidence fields in XML boundaries and ends with a reminder. Prompt 1.1.0 is versioned and fingerprint-pinned. These controls preserve structure; live injection resistance and policy semantics require model evaluation.",
    ),
    page(
        "The sandwich pattern repeats a narrow rule",
        "Give scope and grounding instructions before the data.",
        "Place the question inside its declared data boundary.",
        "End with a reminder to follow the output contract.",
        note="The source motivates this pattern with recency sensitivity. It is a prompt-design technique to evaluate, not a hard security boundary. Changing the actual answer prompt still requires versioning, pin updates and behavioral evaluation.",
    ),
    page(
        "JSON mode and strict schema solve different problems",
        "Valid JSON only guarantees a parseable representation.",
        "A schema checks fields, types and allowed status values.",
        "Source support and policy meaning need further checks.",
        note="The course demonstrates JSON-object output. NexaAssist uses integration strict JSON-schema output and validates AnswerDraft. Neither mechanism makes the contents automatically correct or safe.",
    ),
    *old(3, 5, 6, 7, 8),
    page(
        "A registry supports comparison and rollback",
        "Track prompt text, version, owner and evaluation evidence.",
        "Compare candidates with the same cases and configuration.",
        "Hot-swapping and A/B routing need their own controls.",
        note="The existing code stores prompts as versioned Python artifacts and returns fingerprints. It is not a hot-swapping prompt registry. Teach the registry responsibility without claiming a new service exists.",
    ),
    page(
        "Practical / render a boundary attack safely",
        "Run: python -m training.session3.prompt_boundaries",
        "Inspect escaped closing tags and retained question text.",
        "Check template variables and compare the production rendering.",
        kind="lab",
        note="The lab runs the actual answer chain with a fake model and parses the prompt it receives. Closing tags remain data and the system role survives. The fixture abstention does not prove that a live model ignores every injected instruction.",
    ),
    *old(3, 9, 10, 11, 12),
)
s3 += lesson(
    10,
    page(
        "Meaning defeats exact string comparison",
        "Paraphrases can be correct despite little word overlap.",
        "A tiny negation can reverse an otherwise similar answer.",
        "Use semantic criteria plus deterministic contract checks.",
        note="BLEU and ROUGE can remain useful for some tasks, but overlap alone is a poor release gate for policy answers. Use an original example: “eligible after twelve months” versus “ineligible after twelve months” to show why shared words are insufficient.",
    ),
    diagram(
        "The RAG triad assigns different questions",
        [
            ("Question", "What was asked?"),
            ("Retrieved context", "Was useful evidence found?"),
            ("Generated answer", "Is it supported and responsive?"),
        ],
        [(0, 1, "context relevance"), (1, 2, "faithfulness"), (0, 2, "answer relevance")],
        "The triad localizes faults. Specific Ragas metrics have their own implementation definitions and reference requirements; do not replace them with a vague all-purpose accuracy score.",
    ),
    *old(3, 13, 14),
    page(
        "A judge needs a rubric and calibration",
        "Provide query, context, response and explicit criteria.",
        "Score claims against evidence and record reasons.",
        "Compare a sample against human judgments.",
        note="Low temperature can reduce variability but does not make a judge deterministic. Watch for preference, ordering and correlated model errors. Human agreement checking is an outstanding project improvement; it is taught here as a required design consideration.",
    ),
    *old(3, 15, 16, 17, 18, 19),
    page(
        "Spend evaluation budget where it catches regressions",
        "A representative subset can gate frequent changes.",
        "Broader release or scheduled evaluations cover more cases.",
        "Keep judge, dataset and prompt identities in reports.",
        note="The source distinguishes a small CI set from larger scheduled evaluation. This project has evaluation CLIs and local tests, but no CI pipeline is added in this revision. A subset passing does not validate unseen categories.",
    ),
    *old(3, 20),
)
s3 += old(3, 21, 22)

s4 = old(4, 1, 2, 3)
s4 += lesson(
    11,
    page(
        "Grounded output can still be unsafe",
        "A source may contain private information.",
        "A user may request an unauthorized disclosure.",
        "A safe-looking request can consume excessive resources.",
        note="Correctness and safety are different dimensions. A faithful reproduction of restricted information is still a privacy problem. The source organizes its security discussion around input, output and resource controls.",
    ),
    page(
        "Recognize direct and indirect injection",
        "Direct: the user tries to override the assistant’s rules.",
        "Indirect: retrieved material contains hostile instructions.",
        "Defend at data, prompt, authorization and output boundaries.",
        note="Do not teach a list of forbidden words as complete injection protection. Text can be phrased or encoded many ways. Retrieved documents are untrusted data even when their surrounding system is useful.",
    ),
    page(
        "Risk names are stable; numbering is versioned",
        "The lesson uses older OWASP LLM01 / LLM04 / LLM06 labels.",
        "OWASP 2025 maps disclosure to LLM02 and consumption to LLM10.",
        "Record the list version when naming a risk.",
        note="Verified against https://genai.owasp.org/llm-top-10/ on 2026-10-23. Prompt injection remains LLM01:2025. Explain the source’s historical numbering without presenting it as the current taxonomy.",
    ),
    *old(4, 5, 8, 9, 10, 11, 12),
    page(
        "Treat residual risk as part of the result",
        "Patterns cover selected identifiers, not all personal data.",
        "Quotas are per process; proxy behavior affects client identity.",
        "Authorization and retention still need deployment decisions.",
        note="Keep the source’s defense-in-depth lesson, while avoiding a claim that these controls alone make the service suitable for public internet exposure. NexaAssist remains a training app with explicit live and organizational gaps.",
    ),
)
s4 += lesson(
    12,
    page(
        "Split response time into useful measurements",
        "TTFT: request start until the first output token.",
        "TPS: generation rate after output begins.",
        "End-to-end latency also includes queues and retrieval.",
        note="A buffered API cannot expose user-visible TTFT from generation_ms. Streaming can improve perceived progress, but does not remove prompt processing or queueing delays. Targets should follow the product’s usage rather than universal numbers.",
    ),
    page(
        "Weight memory is only the starting estimate",
        "Approximate decimal GB = parameter billions × bytes/parameter.",
        "Scenario: 8B × 2 bytes = 16 GB for FP16 weights.",
        "Reserve additional memory for cache, runtime and concurrency.",
        note="This is a weight-size lower-bound estimate, not a complete GPU purchase recommendation. Runtimes can shard or offload models; memory layout, kernels and architecture influence feasibility. No hardware performance measurement is supplied.",
    ),
    page(
        "Quantization changes the weight budget",
        "FP16 uses roughly 2 bytes per parameter.",
        "INT8 uses roughly 1; packed INT4 roughly 0.5.",
        "Quality, kernel support and metadata overhead still matter.",
        note="Scenario: idealized 8B INT4 weights use about 4 decimal GB before overhead. Quantization is not a guarantee of identical behavior or usable throughput. Re-evaluate the actual model and task after changing precision.",
    ),
    page(
        "The KV cache grows with workload shape",
        "Longer context requires more cached attention state.",
        "Concurrent sequences increase the live memory footprint.",
        "A model loading successfully does not prove capacity.",
        note="KV memory depends on layer count, attention layout, sequence length, precision and batch size. Avoid treating a fixed “GB per 4000 tokens” number as universal. Capacity must be measured with the intended context and concurrency.",
    ),
    page(
        "API versus self-hosting is a utilization decision",
        "API: variable token cost plus provider limits and governance.",
        "Self-hosting: fixed capacity cost plus operating effort.",
        "Compare representative traffic, privacy and reliability needs.",
        note="Provider quotas, availability and network behavior limit effective scalability; API scale is not unlimited. A steady high-volume workload may justify owned capacity, while a bursty one may not. Use total cost, not token price alone.",
    ),
    page(
        "Separate input and output prices in the estimate",
        "Scenario: 1,000 queries/day, 500 input + 200 output tokens.",
        "At $0.10/$0.50 per 1M: $0.15/day, $4.50/30 days.",
        "These are scenario prices, not a current provider quote.",
        note="Compute input and output cost independently: 500,000 input tokens cost $0.05 and 200,000 output tokens cost $0.10. Multiply by 30 for this illustrative month. Include failed calls, retries, judges and embeddings in a complete estimate.",
    ),
    page(
        "Parallelism and batching solve different constraints",
        "Replicas distribute requests when a model fits per worker.",
        "Sharding distributes a model that needs multiple devices.",
        "Batching trades queue delay for better resource utilization.",
        note="The source covers data parallelism, model parallelism and asynchronous batching. None guarantees linear throughput in practice. Observe provider rate limits, memory pressure and per-request latency when tuning concurrency.",
    ),
    page(
        "Practical / calculate capacity and spend",
        "Run: python -m training.session4.capacity",
        "Verify weight-only estimates and scenario token costs.",
        "Write down the missing cache, runtime and concurrency inputs.",
        kind="lab",
        note="The calculation is deterministic and offline. It demonstrates arithmetic and assumptions, not a live hardware sizing or pricing recommendation.",
    ),
    *old(4, 17, 19),
)
s4 += lesson(
    13,
    page(
        "Async endpoints still need non-blocking internals",
        "Await asynchronous provider and HTTP clients.",
        "Offload synchronous database/file work explicitly.",
        "FastAPI does not offload every utility called inside async def.",
        note="The source text overstates automatic threadpool handling. Official FastAPI documentation distinguishes synchronous path operations/dependencies from ordinary utility calls. NexaAssist explicitly uses asyncio.to_thread for synchronous PyMongo work. Reference: https://fastapi.tiangolo.com/async/.",
    ),
    *old(4, 4, 6, 7),
    page(
        "Dependency injection defines resource ownership",
        "Create or cache shared clients with clear lifecycle.",
        "Inject application settings and replace services in tests.",
        "Keep domain logic callable outside HTTP routes.",
        note="Depends is a wiring mechanism, not a blanket singleton or startup guarantee. Resource ownership must be explicit in lifespan, caches or dependencies. The current service/chain split lets evaluation replay the same logic.",
    ),
    *old(4, 13, 14, 15, 16),
    page(
        "A reproducible image still needs safe deployment",
        "Freeze dependencies and build with an excluded-secret context.",
        "Inject secrets at runtime; do not COPY .env into images.",
        "Review networking, readiness and rollout in the target platform.",
        note="The source Docker example includes COPY .env while later advising runtime secrets. The revised training follows the runtime-secret practice and existing dockerignore. No cloud provider deployment is assumed or performed.",
    ),
    *old(4, 18),
)
s4 += old(4, 21, 22)

s5 = old(5, 1, 2, 3)
s5 += lesson(
    14,
    page(
        "Follow-up questions change retrieval requirements",
        "A query such as “Does that fee apply earlier?” lacks scope alone.",
        "Conversation history can resolve the subject and date.",
        "Memory adds privacy, latency and correctness obligations.",
        note="NexaAssist currently asks a standalone policy question per request. Teach the source’s orchestration design without claiming that persistence, rewriting or session authentication exists in production.",
    ),
    diagram(
        "Keep API workers stateless; store conversation state",
        [
            ("Request", "Session + user scope"),
            ("Load history", "Authorized durable turns"),
            ("Rewrite", "Standalone search query"),
            ("Retrieve / answer", "Generate, validate, persist"),
        ],
        [(0, 1, "hydrate"), (1, 2, "disambiguate"), (2, 3, "search")],
        "This is the course reference design, not an implemented NexaAssist workflow. A real implementation must authorize session access and isolate users. A worker-local list loses context across replicas and restarts.",
    ),
    page(
        "A sliding window is a budget approximation",
        "Load a bounded recent history instead of all turns.",
        "Message count is simple but ignores varying token length.",
        "Reserve tokens for instructions, evidence and output.",
        note="The source illustrates six recent messages. That is a heuristic, not a recommended universal setting. Production history requires deterministic ordering, retention, deletion and a token-aware budget appropriate to the selected model.",
    ),
    page(
        "Rewriting must preserve the user’s meaning",
        "Resolve references using only authorized recent history.",
        "Keep original question and rewritten search query separate.",
        "Validate output; time out or fall back when rewriting fails.",
        note="A cheap rewriter is another model call and failure surface. It can change a fee date or invent a product. A fallback to the original question preserves availability but may retrieve poorly; asking for clarification can be safer depending on the contract.",
    ),
    page(
        "New state needs multi-turn evaluation",
        "Capture history, current input and expected source.",
        "Test incorrect rewrites, missing history and cross-user access.",
        "Recheck retrieval and answer quality before rollout.",
        note="The source expands its single-turn golden set when adding memory. Existing single-turn success does not demonstrate conversational quality. Use explicit reference identities rather than evaluating fluency alone.",
    ),
    page(
        "Practical / model the memory contract offline",
        "Run: python -m training.session5.memory_design",
        "Inspect a bounded fixture and a failed-rewrite fallback.",
        "Explain why the simulation is not a durable session service.",
        kind="lab",
        note="This educational simulation uses no LLM or database and does not add conversation memory to the API. Learners submit an implementation plan naming storage, authorization, token budgeting and multi-turn tests.",
    ),
)
s5 += lesson(
    15,
    *old(5, 4, 5, 6, 7),
    page(
        "Quality is maintained in three layers",
        "Automated gates catch known regressions.",
        "Human review assesses context and newly observed failures.",
        "Governance controls changes to meaning and risk.",
        note="The layers complement each other. LLM-based evaluations can vary even in an offline run; do not call them deterministic simply because the dataset is fixed. Preserve judge versions and compare a sample to reviewed human assessments.",
    ),
    page(
        "The review queue needs the exact interaction",
        "Link the input, evidence references, output and versions.",
        "Prioritize explicit complaints and representative samples.",
        "Review the source before accepting the correction.",
        note="The stored response is client supplied and does not prove server execution. The authenticated export reads the accepted institution-scoped review and requires a separately curated GoldenAnswer. It returns an audit bundle without changing the shipped dataset or establishing semantic truth.",
    ),
    *old(5, 11, 12, 13, 14, 15),
    page(
        "Watch both semantic and operational drift",
        "Topic shifts can expose gaps in the golden set.",
        "Policy updates can invalidate otherwise stable answers.",
        "Judge changes can move scores without application changes.",
        note="NexaAssist has comparison functions and sampled judging, not a complete semantic drift detector. Treat changing scores as evidence to investigate, aligning datasets and judge configuration before assigning cause.",
    ),
    *old(5, 8, 9, 10, 16, 17, 18),
)
s5 += lesson(
    16,
    *old(5, 19),
    page(
        "Bound an agent before granting actions",
        "Limit steps, time, token spend and tool permissions.",
        "Isolate side effects and preserve an audit trail.",
        "Evaluate tool choice, arguments and recovery behavior.",
        note="A read-only assistant becomes materially different when it can modify a record. The source names iteration caps, allowlists and sandboxed execution. These are design requirements for a future layer, not controls implemented by the current chain.",
    ),
    page(
        "Multimodal inputs expand the ingestion boundary",
        "OCR or vision extraction introduces interpretation errors.",
        "Images and audio can carry identifiers or instructions.",
        "Queue expensive processing and evaluate the extracted evidence.",
        note="A text-first index can simplify downstream retrieval but still needs modality-specific validation and privacy review. Adding image input is not merely changing an embedding model.",
    ),
    page(
        "Model distillation introduces a training lifecycle",
        "Curate teacher traces into reviewed training data.",
        "Evaluate a smaller student on quality and safety cases.",
        "Version the dataset, model and rollback decision.",
        note="The 4D phase named Distill is broader than knowledge distillation. Keep those two meanings distinct. A smaller model can reduce resource use, but improvement must be measured for the task.",
    ),
    page(
        "Edge execution shifts the operational trade-off",
        "Local inference can reduce network disclosure and round trips.",
        "Device differences affect performance and version consistency.",
        "Telemetry, updates and recovery need a new design.",
        note="Avoid the source’s absolute “near-zero latency” phrasing. On-device models can be slow or constrained, and local processing does not guarantee that every feature avoids external calls.",
    ),
    page(
        "The lifecycle survives a change in capabilities",
        "Define the new permission and data boundaries.",
        "Evaluate before deployment and version the artifacts.",
        "Observe failures and close the reviewed feedback loop.",
        note="Agents, multimodality, distillation and edge execution introduce different engineering work. The operating principles continue to apply; capability should follow a concrete use case and a measurable acceptance plan.",
    ),
)
s5 += old(5, 21, 22)

SESSIONS: list[dict[str, Any]] = []
for index, slides in enumerate([s1, s2, s3, s4, s5]):
    opening = deepcopy(SHOWCASES[index][:2])
    walkthrough, debrief = SHOWCASES[index][2:]
    opening[1]["note"] += (
        f"\n\nCode walkthrough: {walkthrough['source']}\n{walkthrough['code']}\n\n"
        + " ".join(debrief["body"])
        + " "
        + debrief["note"]
    )
    slides[3:3] = opening
    session = {**deepcopy(ORIGINAL[index]), "slides": slides}
    session["slides"][0]["body"][1] = (
        f"Session {index + 1} of 5 · 3 hours · source-aligned workshop"
    )
    session["slides"][0]["note"] += (
        " This revised deck follows the course lesson sequence; exact lesson URLs appear in section notes and the coverage map."
    )
    SESSION_LESSONS = sorted({s["lesson"] for s in slides if "lesson" in s})
    session["lessons"] = ", ".join(str(n) for n in SESSION_LESSONS)
    SESSIONS.append(session)
assert {s["lesson"] for session in SESSIONS for s in session["slides"] if "lesson" in s} == set(
    range(1, 17)
)
compact_sessions(SESSIONS)
