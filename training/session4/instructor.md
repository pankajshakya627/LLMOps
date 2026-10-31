# Session 4: instructor guide

Use [the deck notes](../decks/NexaAssist_S4_aligned_20261023/notes/total.md) as the slide-by-slide script, and the [handout](handout.md) for commands. Each slide's notes explain visible claims, source references, expected outcomes and limits. Instructor notes and answers are visible in this local kit; give students the handouts when you want them to predict independently.

## Run sheet (180 minutes)

- 0–25: concept discussion; ask for a failure the current controls cannot detect.
- 25–45: follow the code referenced by the slides.
- 45–85: first pair experiments. Require predictions before execution.
- 85–95: break.
- 95–135: remaining core experiments and written interpretation.
- 135–160: gate review. Each pair names evidence, unknowns and the next decision.
- 160–180: quiz, feedback and next-session preparation.

Sessions 1–2 handouts contain more extensions than the in-class window allows. Use the deck's core labs in class and assign other extensions as homework. Required labs are offline. Do not improvise a live provider or database demonstration with unapproved data or spend.

## Answer key and debrief

422 means invalid input; 429 means quota exceeded; 503 means dependency unavailable. Health is liveness and readiness currently checks only the MongoDB ping. Pattern-based output checking cannot detect all PII. A driver deadline is not a hard real-time wall-clock guarantee. Empty traffic is not_measured, not pass. TTFT cannot be inferred from a buffered answer.

## Assessment rubric (class exercise)

One point each for a reproducible command/result, correct failure classification, a source/code reference, a stated limitation, and an evidence-supported gate decision. Require all five for the class artifact to be complete; this is an instructional rubric, not a production KPI. Return incomplete work for correction rather than lowering the bar. Keep unresolved production owner decisions explicit.

## Revised lesson sequence

L11: Security, Compliance, and Responsible Operation in LLMOps, L12: Inference Infrastructure: Hardware, Economics, and Latency, L13: Hosting, Serving, and Scaling LLMs in Production.

Use the source-aligned deck and COURSE_ALIGNMENT.md. The additional concept slides can be assigned for pre-reading; keep the 90-minute practical window.

## Opening showcase

Use slides 4–5 and run `uv run --no-sync python -m training.showcase --session 4`. Follow the code walkthrough and debrief in slide 5 notes. Use [the shared runbook](../SHOWCASE_RUNBOOK.md) for exact inputs, failure conditions, expected evidence and implementation limits.
