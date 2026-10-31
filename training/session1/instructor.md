# Session 1: instructor guide

Use [the deck notes](../decks/NexaAssist_S1_aligned_20261023/notes/total.md) as the slide-by-slide script, and the [handout](handout.md) for commands. Each slide's notes explain visible claims, source references, expected outcomes and limits. Instructor notes and answers are visible in this local kit; give students the handouts when you want them to predict independently.

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

Production constraints include latency, cost and variable semantic quality. A gate is a documented decision based on evidence. Ingestion maintains the knowledge assets separately from online requests. Prompts are independently changing artifacts. SHA-256 detects byte changes relative to the register; it proves neither policy correctness nor permission.

## Assessment rubric (class exercise)

One point each for a reproducible command/result, correct failure classification, a source/code reference, a stated limitation, and an evidence-supported gate decision. Require all five for the class artifact to be complete; this is an instructional rubric, not a production KPI. Return incomplete work for correction rather than lowering the bar. Keep unresolved production owner decisions explicit.

## Revised lesson sequence

L1: What Is LLMOps, and Why Does It Exist?, L2: How We Reached LLMOps, L3: MLOps to LLMOps: What Changes and What Stays, L4: The 4D Framework (Discover, Distill, Deploy, Deliver), L5: Architecture of a Retrieval-Augmented Generation Application, L6: Scoping and Planning a Production RAG Application.

Use the source-aligned deck and COURSE_ALIGNMENT.md. The additional concept slides can be assigned for pre-reading; keep the 90-minute practical window.

## Opening showcase

Use slides 6–9 for architecture, 11 and 13 for code, and 14 for the source-boundary demonstration. Run `uv run --no-sync python -m training.showcase --session 1`. Follow slide 14 notes and the handout. Use [the shared runbook](../SHOWCASE_RUNBOOK.md) for exact inputs, failure conditions, expected evidence and implementation limits.
