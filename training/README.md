# Training labs

Runnable practicals for the LLMOps course. Each session has a student handout and the lab scripts it refers to.
Start with [the showcase runbook](SHOWCASE_RUNBOOK.md) and run `uv run --no-sync python -m training.showcase` for all five classes. Run everything from the project root. Labs marked offline need no database, network or model key.

| Session | Theme | Handout | Offline labs |
|---|---|---|---|
| 1 | Discover: lifecycle, release evidence, evaluation baseline and governance | [handout](session1/handout.md) | Source tamper, gate validation, inventory and provider-change review |
| 2 | LLMOps Core: observability, evals, gateways and security, with RAGOps | [handout](session2/handout.md) | Trace capture, eval gates, routing/cache matrix, guardrail cases; [live tool guide](session2/live_practicals.md) |
| 3 | Distill II: prompts, generation and quality gates | [handout](session3/handout.md) | `python -m training.session3.answers`, `python -m training.session3.gates` |
| 4 | Deploy: serving, security, readiness and cost | [handout](session4/handout.md) | `python -m training.session4.serving` |
| 5 | Deliver: observability, feedback and rollback | [handout](session5/handout.md) | `python -m training.session5.incident` |

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/nexaassist
uv run --no-sync python -m training.session2.chunks
uv run --no-sync pytest tests/test_training_labs.py   # keeps the labs from silently breaking
```

The scripts print through `training/console.py` (plain lines for students) because they are not part of the service, which logs JSON through structlog.
All five [editable decks and instructor notes](decks/README.md) are stored here. The [use-case manifest](use_case_manifest.md) records scope and unresolved owner decisions. The course follows the Educative LLMOps themes with original NexaAssist examples; it retains MongoDB Atlas and the project's layer rules.

Sessions 1–2 now follow the supplied `LLMOps_Syllabus.md`; use the [current syllabus-to-slide map](decks/SYLLABUS_ALIGNMENT.md) and required 90-minute practical blocks at the top of their handouts. The earlier [Educative coverage map](decks/COURSE_ALIGNMENT.md) remains a supporting record. Additional offline exercises cover prompt boundaries, capacity/cost arithmetic, and the conversation-memory design contract. [System Design and C4 companion materials](decks/README.md#architecture-and-system-design) are included.
