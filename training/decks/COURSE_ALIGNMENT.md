# Educative LLMOps → five-session coverage map

**Historical supporting map.** Sessions 1–2 were subsequently aligned to the supplied `LLMOps_Syllabus.md` on 24 October 2026. Use [SYLLABUS_ALIGNMENT.md](SYLLABUS_ALIGNMENT.md) for their current slide topics, practical evidence and coverage depth. The lesson links below remain supporting material in the notes; this table describes the preceding edition's emphasis.

All sixteen lessons and the overview were visited through signed-in Safari on 2026-10-23. Each page was allowed seven seconds to load (observed visit duration 7.28–7.31 seconds). Every lesson link discovered within the course was visited. Raw lesson text is not redistributed.

The lesson order below is the course order. Five sessions are a teaching adaptation. Each section presents the lesson concept before local code, an exercise, or a clearly identified design-only extension.

| Lesson | Source | Session | Slides |
|---|---|---|---|
| 1 | [What Is LLMOps, and Why Does It Exist?](https://www.educative.io/courses/llmops/what-is-llmops-and-why-does-it-exist) | 1 | 2–2 |
| 2 | [How We Reached LLMOps](https://www.educative.io/courses/llmops/how-we-reached-llmops) | 1 | 3–3 |
| 3 | [MLOps to LLMOps: What Changes and What Stays](https://www.educative.io/courses/llmops/mlops-to-llmops-what-changes-and-what-stays) | 1 | 4–4 |
| 4 | [The 4D Framework (Discover, Distill, Deploy, Deliver)](https://www.educative.io/courses/llmops/the-4d-framework-discover-distill-deploy-deliver) | 1 | 5–5 |
| 5 | [Architecture of a Retrieval-Augmented Generation Application](https://www.educative.io/courses/llmops/architecture-of-a-retrieval-augmented-generation-application) | 1 | 6–11 |
| 6 | [Scoping and Planning a Production RAG Application](https://www.educative.io/courses/llmops/scoping-and-planning-a-production-rag-application) | 1 | 12–15 |
| 7 | [Data Foundations for LLMOps](https://www.educative.io/courses/llmops/data-foundations-for-llmops) | 2 | 2–7 |
| 8 | [Embeddings, Vector Storage, and Evaluation](https://www.educative.io/courses/llmops/embeddings-vector-storage-and-evaluation) | 2 | 8–15 |
| 9 | [Prompt Engineering and Prompt Life Cycle Management](https://www.educative.io/courses/llmops/prompt-engineering-and-prompt-life-cycle-management) | 3 | 6–21 |
| 10 | [Evaluation of LLM Outputs: Metrics, Tests, and Human Feedback](https://www.educative.io/courses/llmops/evaluation-of-llm-outputs-metrics-tests-and-human-feedback) | 3 | 22–34 |
| 11 | [Security, Compliance, and Responsible Operation in LLMOps](https://www.educative.io/courses/llmops/security-compliance-and-responsible-operation-in-llmops) | 4 | 6–16 |
| 12 | [Inference Infrastructure: Hardware, Economics, and Latency](https://www.educative.io/courses/llmops/inference-infrastructure-hardware-economics-and-latency) | 4 | 17–27 |
| 13 | [Hosting, Serving, and Scaling LLMs in Production](https://www.educative.io/courses/llmops/hosting-serving-and-scaling-llms-in-production) | 4 | 28–39 |
| 14 | [Orchestration and Application Logic](https://www.educative.io/courses/llmops/orchestration-and-application-logic) | 5 | 6–12 |
| 15 | [Quality, Human-in-the-Loop, and Governance Systems](https://www.educative.io/courses/llmops/quality-human-in-the-loop-and-governance-systems) | 5 | 13–31 |
| 16 | [Future Directions in LLMOps](https://www.educative.io/courses/llmops/future-directions-in-llmops) | 5 | 32–38 |

## What changed from the first decks

Added explicit teaching sections for AI/ML/GenAI/LLM scope, the evolution of the operating burden, MLOps component changes, artifact opacity, all 4D gates, the source-course support project and stack, prompt delimiters/sandwich/registry, semantic metrics and judges, inference hardware and economics, session state/rewrite trade-offs, and future capabilities. Existing code walkthroughs now sit under those concepts.

## Explicit adaptations

- PostgreSQL/pgvector → MongoDB Atlas Vector Search, as required by CLAUDE.md.
- LiteLLM/Jinja examples → existing LangChain integrations and ChatPromptTemplate; the shared prompt now uses escaped XML data fields, with an offline contract exercise.
- /ingest and /chat examples → ingestion CLI and /answer in this project.
- Conversation memory, query rewriting and blue/green promotion remain design exercises. Authenticated, reviewer-curated golden export is implemented; automatic dataset promotion is not.
- Dataset/judge behavior is probabilistic; a fixed offline dataset does not make model evaluation deterministic.
- Course example thresholds and arithmetic are examples, not approved targets or current prices.

## Technical corrections retained in the teaching notes

The serving lesson overstates automatic handling of synchronous helpers inside async functions. Follow [FastAPI’s concurrency documentation](https://fastapi.tiangolo.com/async/): ordinary blocking utility calls need explicit offloading or an async client. The course Docker example copies .env even though its deployment guidance recommends runtime secrets; this kit follows runtime injection.

The course uses older OWASP labels. [OWASP 2025](https://genai.owasp.org/llm-top-10/) lists prompt injection as LLM01, sensitive disclosure as LLM02 and unbounded consumption as LLM10. Low temperature is not a determinism guarantee. Weight-memory arithmetic excludes KV cache and runtime overhead; local inference does not imply zero latency.

## Showcase revision

Sessions 1–2 now place the offline demonstration on slide 14 after the architecture and code walkthroughs. Sessions 3–5 retain the opening scenario and demonstration pages. See [the complete runbook](../SHOWCASE_RUNBOOK.md). Prompt lifecycle, output evaluation and governance lessons were reread in Safari for this implementation pass; see [the additional visit record](course_refresh_visit_log.json).

## Compact Sessions 1–2, 2026-10-24

Sessions 1 and 2 now each contain sixteen editable slides. Repeated section dividers and secondary explanations moved into notes/handouts. Session 1 retains lessons 1–6 and adds source-checked C4 context/container, offline/online and request-flow diagrams. Session 2 retains lessons 7–8 with ingestion, parent storage, retrieval and amendment diagrams. Expanded versions are archived locally.
