# Sessions 1–2 — current delivery verification

Updated **24 October 2026**. Session 1 retains its verified **16 slides**. Session 2 is now **LLMOps Core: Observability, Evaluation & Security**, with **19 slides, 19 linked notes and a 19-page PDF**, below the requested 20-page limit. All content is native editable text and geometry; the preceding Session 2 deck is preserved at `NexaAssist_S2_core_20261024/sources/source.pptx`.

| Deck | Content / practicals | Slides |
|---|---|---:|
| Session 1 — Discover | Lifecycle inventory, release/evaluation evidence, governance and provider-change review | 16 |
| Session 2 — LLMOps Core | Retained RAGOps, Datadog/Phoenix tracing, Ragas/DeepEval evaluation, LiteLLM/Portkey routing and security/Guardrails AI/NeMo | 19 |

The alternatives are identified explicitly. Datadog, Ragas, LiteLLM and Guardrails AI are the worked tools. The [Session 2 handout](../session2/handout.md) provides the 90-minute practical block; the [live guide](../session2/live_practicals.md) contains service setup, an evaluation harness, fallback/load-balancing/cache experiments and a schema-validation exercise. The [LiteLLM YAML](../session2/litellm.yaml) defines Ollama `qwen3.5:9b-mlx`, `qwen3-embedding:0.6b`, OpenAI chat from environment and `text-embedding-3-small`. Chat fallback is separate from embedding profiles; cache is off initially.

## Verification

- Session 2 round-trip SVG checks: **19/19 passed, zero warnings/errors**. Native export postflight and package delivery check: **passed, zero warning categories**.
- All 19 manifest titles, native text, practical-guide references and actual note relationships checked. The course delivery test follows PPTX note relationships rather than assuming note part names match slide numbers. It also checks current authoring sources, diagrams, the 19-page count and requested tools/model tags: **3 passed**.
- All 19 SVG previews and exported LibreOffice PDF pages rendered. The exported pages were reviewed in grouped four-page panels; no unresolved visual findings. PDF, session overview and course preview refreshed.
- Full offline regression suite after the note-relationship check was corrected: **214 passed, 1 pre-existing failure in 32.47 seconds**. The retained failure requires the missing `C4-Documentation/nexaassist-architecture.html`. No test was skipped, deleted or suppressed.
- **Ruff passed. Mypy passed for 122 source files.** The four-alias YAML parsed and its route/secret/cache boundaries were checked. Both documented Python framework snippets compile; the installed Ragas scoring signatures were inspected. These static checks do not establish live tool success.

## Sources and limits

Current workspaces are `NexaAssist_S1_syllabus_20261024/` and `NexaAssist_S2_core_20261024/`. Session 2 uses `page_plan.json`, `authoring-svg-flat/core_NN.svg` and `notes/core_NN.md`; its `validation/` contains quality/export/delivery/readback and visual receipts. The [syllabus map](SYLLABUS_ALIGNMENT.md), machine map, lesson coverage and course manifest reflect the new order. The older generated workspaces/content scripts describe earlier editions and must not overwrite this native revision.

Application code and production thresholds were unchanged. Ollama was not serving locally; LiteLLM and Guardrails AI were not installed in the app environment. No models were pulled and no live provider, Atlas, gateway or Datadog workflow was executed. Offline fixtures, configuration predictions, observed live results and unmeasured checks are distinguished. The required local controls passed in the offline suite; optional framework examples await instructor preflight and live validation. PowerPoint itself was not opened; LibreOffice rendered the PPTX with project fonts, which are not embedded.
