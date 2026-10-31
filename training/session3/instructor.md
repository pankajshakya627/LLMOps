# Session 3: instructor guide

Use [the deck notes](../decks/NexaAssist_S3_aligned_20261023/notes/total.md) as the slide-by-slide script, and the [handout](handout.md) for commands. Each slide's notes explain visible claims, source references, expected outcomes and limits. Instructor notes and answers are visible in this local kit; give students the handouts when you want them to predict independently.

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

A hash tracks prompt identity; it does not prove improvement. A matching quote does not establish entailment. Incomplete expected evidence points to retrieval; unsupported output with complete evidence points to generation. Keep reviewer metadata outside the strict GoldenAnswer schema. Synthetic scores test gate mechanics, while live runs test actual models.

## Assessment rubric (class exercise)

One point each for a reproducible command/result, correct failure classification, a source/code reference, a stated limitation, and an evidence-supported gate decision. Require all five for the class artifact to be complete; this is an instructional rubric, not a production KPI. Return incomplete work for correction rather than lowering the bar. Keep unresolved production owner decisions explicit.

## Revised lesson sequence

L9: Prompt Engineering and Prompt Life Cycle Management, L10: Evaluation of LLM Outputs: Metrics, Tests, and Human Feedback.

Use the source-aligned deck and COURSE_ALIGNMENT.md. The additional concept slides can be assigned for pre-reading; keep the 90-minute practical window.

## Opening showcase

Use slides 4–5 and run `uv run --no-sync python -m training.showcase --session 3`. Follow the code walkthrough and debrief in slide 5 notes. Use [the shared runbook](../SHOWCASE_RUNBOOK.md) for exact inputs, failure conditions, expected evidence and implementation limits.
