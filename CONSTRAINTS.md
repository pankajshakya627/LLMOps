# Constraints

Reviewed 2026-10-23 for the five-session training delivery. Existing CLAUDE.md layer rules and settings remain authoritative.

## Floor

No new suppression comments, skipped/deleted tests, secrets, silent exception handlers or unimplemented code stubs. Do not lower evaluation thresholds to make an exercise pass. Mark scenario scores visibly. No live provider, Atlas or Phoenix calls during the required offline labs.

## Checks

| Dimension | Rule and reason | Command | When |
|---|---|---|---|
| Python quality | Zero new lint/type errors; keep training code readable | `ruff check .` and `mypy .` | Delivery |
| Behavior | All new and affected offline tests pass | `pytest tests/test_training_labs.py tests/test_answer.py tests/test_readiness_timeout.py` | Delivery |
| Regression | Report full offline suite failures without hiding them | `pytest -q tests` | Delivery |
| Slides | Five editable PPTX files; every slide has notes; no blocking export errors | ppt-master final SVG checker and native export postflight | Export |

## Known baseline issue

`tests/test_architecture_document.py` expects a missing `C4-Documentation/nexaassist-architecture.html` in this copy. Report it separately; do not skip, delete or weaken that test.

## Measured, not enforced as production targets

SLO and quality numbers in `app/evaluation/gates.json` remain placeholders. Offline fakes and scenario metrics cannot establish live correctness, security coverage or performance. CI, coverage percentages and external security scanners were not configured by this delivery.
