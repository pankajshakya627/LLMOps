# LLMOps in five sessions — syllabus-aligned teaching decks

The five decks contain **152 editable slides with notes on every slide**. Sessions 1 and 2 have been revised against [LLMOps_Syllabus.md](../../LLMOps_Syllabus.md): **16 slides for Session 1 and 19 for Session 2**, with platform-agnostic operating controls, concrete offline practicals, expected outcomes and exit submissions. Session 1 covers lifecycle, release evidence and governance; Session 2 retains RAGOps and adds observability/tracing, eval harnesses, gateway routing/caching and security/guardrails with practicals. NexaAssist remains the worked example.

Use the [current syllabus-to-slide map](SYLLABUS_ALIGNMENT.md) and the required 90-minute practical blocks at the top of the Session 1–2 handouts. They distinguish concept introductions, runnable fixture demonstrations, design exercises and open live measurements. Sessions 3–5 retain their previous content; the map proposes where the remaining syllabus areas continue without asserting full coverage of every bullet.

The [showcase runbook](../SHOWCASE_RUNBOOK.md) documents the existing demonstrations. The [Educative coverage map](COURSE_ALIGNMENT.md) and [Safari visit log](course_visit_log.json) are supporting records from the previous revision; lesson URLs remain in notes. The supplied local syllabus is the primary authority for the revised Sessions 1–2.

| Session | Coverage | Slides | Deck | Handout |
|---|---|---:|---|---|
| 1 — Discover | Syllabus 01–03, 09–11; architecture and reliability introductions | 16 | [PowerPoint](Session_1.pptx) | [Practicals](../session1/handout.md) |
| 2 — LLMOps Core | RAGOps + observability, evaluation, gateways and security | 19 | [PowerPoint](Session_2.pptx) | [Practicals](../session2/handout.md) |
| 3 — Distill II | 9–10: prompt lifecycle and output evaluation | 36 | [PowerPoint](Session_3.pptx) | [Practicals](../session3/handout.md) |
| 4 — Deploy | 11–13: security, inference economics, serving and scaling | 41 | [PowerPoint](Session_4.pptx) | [Practicals](../session4/handout.md) |
| 5 — Deliver | 14–16: orchestration, governance, agents and future directions | 40 | [PowerPoint](Session_5.pptx) | [Practicals](../session5/handout.md) |

Each class is approximately three hours: 25 min concepts, 20 min code walkthrough, 90 min pair practicals including a break, 25 min gate review, 20 min recap. The decks contain reference slides and worked examples for pre-reading and follow-up; instructors can assign those before class to preserve practical time. The longer Session 1–2 handouts include optional extensions and homework.

## Architecture and System Design

- [Interactive RAG reference architecture](../../.archify/architecture-llmops-reference-20261023-220000/llmops-reference.html): course-concept view; artifact and real-browser checks passed.
- [C4 system context](../../docs/architecture/c4-context.md), [C4 containers](../../docs/architecture/c4-containers.md), and [answer sequence](../../docs/architecture/c4-dynamic-answer.md): current working-copy architecture and source references.
- [System Design document](system_design/NexaAssist_System_Design.docx) and [rendered PDF](system_design/NexaAssist_System_Design.pdf): cloned from the selected System Design template, preserving its styles, tables, page setup, header/footer structure and numbering. The retained reference is unchanged.
- [Architecture preview](course_preview.png), [Session 1 overview](Session_1_overview.png), [Session 2 overview](Session_2_overview.png), and [PDF decks](rendered).
- [Session 1–2 verification](session_1_2_verification.md): slide counts, source checks, visual review and test status.

The folder has no Git metadata, so no commit identity or production deployment is asserted. The Archify reference diagram is conceptual; the C4 documents describe inspected local files and identify conditional services.

## Practicals and implementation

Run from the repository root:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/nexaassist
uv sync --python 3.14 --locked --extra ui --extra evaluation
uv run --no-sync pytest tests/test_training_labs.py tests/test_course_delivery.py -q
```

Core labs reuse the real application chain, routes, retrieval scorers, gate functions and SLO/comparison logic with local fixtures or fake dependencies. New source-alignment exercises:

```bash
uv run --no-sync python -m training.session3.prompt_boundaries
uv run --no-sync python -m training.session4.capacity
uv run --no-sync python -m training.session5.memory_design
```

The first inspects the actual shared answer chain with a fake model and verifies its escaped data fields. The second calculates idealized weight memory and visibly invented token-price scenarios. The third exposes lost conversational scope and rewrite-fallback ambiguity using a fixture; it does not add durable memory to the API.

Required labs are offline. Live Atlas/OpenAI/Datadog exercises need approved credentials, data permissions and spend. Fakes establish control flow, not live quality or capacity. The output PII rail and readiness deadline from the first delivery remain in the shared implementation; this revision adds prompt 1.1.0, comparable-run checks and authenticated reviewer-curated export through the API and reviewer screen. Live behavior of the revised prompt still needs evaluation.

## Source adaptation and accuracy

Educative uses PostgreSQL/pgvector, LiteLLM, Jinja, /ingest and /chat examples. This project retains MongoDB Atlas, LangChain and the existing CLI/API contracts. Concepts such as registry hot-swapping, memory, query rewriting, automatic dataset promotion, CI and blue/green promotion are taught with their implementation status stated explicitly.

The coverage map explains technical corrections: asynchronous functions do not automatically offload synchronous helpers; secrets are injected at runtime; OWASP numbering is versioned; low temperature does not guarantee deterministic judging; GPU weight size omits cache/runtime overhead. Current model prices or availability are not asserted. `app/evaluation/gates.json` remains placeholder data.

## Sources and editing

For Sessions 1–2, the current editable sources are `NexaAssist_S1_syllabus_20261024/authoring-svg-flat/` and `NexaAssist_S2_core_20261024/authoring-svg-flat/`, with instructor notes under each `notes/`. Session 2 uses the 19-page `page_plan.json` and `core_NN.svg` authoring copies. These are source-preserving native edit workspaces; each retains the preceding PPTX at `sources/source.pptx`. `course_manifest.json` and `syllabus_alignment.json` describe the delivered content. Use the ppt-master **Edit Native PPTX** route: refresh summary → round-trip quality check → round-trip export → delivery check/readback. Do not use `finalize_svg.py` on these imported workspaces.

`aligned_content.py`, `compact_content.py`, `course_content.py` and `build_course.py` describe the previous source-course edition and the unchanged Sessions 3–5. Running their `prepare`, `notes`, `early` or `rest` actions for Sessions 1–2 would overwrite current copy or metadata. Earlier `NexaAssist_Sn_aligned_20261023/` projects and archived decks are historical references. Current `Session_n.pptx` files are the deliverables.

PPTX text and geometry are native editable objects. Fonts are Trebuchet MS, Arial and Courier New; fonts are not embedded. Sessions 1–2 use the native authoring workspaces above; the older generation projects use `svg_output/` and `svg_final/`. Validation/export receipts are local to the relevant workspace. Temporary export tools live in `/tmp/nexa-ppt-env` and may need recreation after OS cleanup; they are not app dependencies.

Keep the edited native text inside its available frame and inspect exported slides after any changes. LibreOffice PDFs and overview images accompany the delivered PPTX files. Older local preview servers may show the previous generation sources; use the exported current PDF/PPTX for this revision. The interactive Archify diagram retains its earlier validation record.

## Instructor showcase

Run `uv run --no-sync python -m training.showcase` for all five demonstrations, or add `--session N`. Session 1 runs its demonstration on slide 14. The revised Session 2 retains the policy-date demonstration on slide 6, with ingestion on slide 4 and the new tool practicals on slides 9, 12, 15, 17 and 18. Sessions 3–5 introduce their demonstrations on slides 4–5. The [runbook](../SHOWCASE_RUNBOOK.md) maps learner actions, code, expected failures, review artifacts and limitations.

## Session 2 core tool practicals

The [live practical guide](../session2/live_practicals.md) supplies Datadog setup, a small Ragas harness, gateway failure/cache/balancing experiments and Guardrails AI schema validation. The [LiteLLM YAML](../session2/litellm.yaml) exposes local Qwen chat/embeddings and OpenAI chat/embeddings without changing application factories or dependencies. Ollama was not serving locally during authoring; package/model installation and live service checks are instructor preflight. The 19-slide edition is below the user's 20-page limit.
