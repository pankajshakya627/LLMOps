"""Opening demonstrations grounded in implemented RAG controls."""

from __future__ import annotations

from training.decks.course_content import code, page

SHOWCASES = [
    [
        page(
            "Showcase / can we trust this policy?",
            "Staff need the approved policy explanation.",
            "A file changes while its register hash stays fixed.",
            "The ingestion boundary must reject that file.",
            note="Open the synthetic register. Ask learners to predict whether a plausible PDF remains authoritative when its bytes change. Inspect source verification before discussing models.",
        ),
        page(
            "Run the evidence-integrity demonstration",
            "python -m training.showcase --session 1",
            "Original: 8 documents verified.",
            "Tampered copy: hash mismatch; ingestion refused.",
            kind="lab",
            note="Allow 12 minutes. Run from the root using the existing environment. The script changes a temporary copy. Retain the document ID and mismatch, then name the release artifact needing review.",
        ),
        code(
            "Code / check integrity before model work",
            "app/services/ingestion.py",
            "def requests_from_register",
            10,
            "Trace the register entry to the exact source bytes.",
        ),
        page(
            "Evidence to keep from Session 1",
            "Input: registered file and expected SHA-256.",
            "Failure: mismatch before parsing or embedding.",
            "Decision: hold ingestion and review the source.",
            note="Submit a transcript, source ID and owner decision. Byte identity does not establish permission or semantic correctness.",
        ),
    ],
    [
        page(
            "Showcase / a fee changes on 1 July",
            "30 June sanction and lookup: base policy fee.",
            "1 July sanction and lookup: linked circular fee.",
            "A different product must not reuse those sources.",
            note="Use actual registered POL-HL-V3 and CIR-2026-07 PDFs. State both lookup and sanction dates. A later lookup does not change an earlier sanction's fee. All policies are synthetic.",
        ),
        page(
            "Run the dated-policy demonstration",
            "python -m training.showcase --session 2",
            "June: 0.35% / POL-HL-V3.",
            "July: 0.30% / CIR-2026-07; quotes verified.",
            kind="lab",
            note="Allow 20 minutes. Parsing, ingestion, date/product filters, parent expansion, linked amendments and answer checks are real code. Mongo transport, embedding, ranking and model outputs are fixtures. Inspect the full circular, including applicability and revised caps.",
        ),
        code(
            "Code / include the linked amendment",
            "app/chains/retrieval.py",
            "if amendment_search is not None and rows:",
            10,
            "The amendment's applicability travels with its fee revision.",
        ),
        page(
            "Break it / change only the product",
            "NEXA-HL → NEXA-PL with the fee question.",
            "Expect insufficient_evidence and no citation.",
            "Explain the separate role of the sanction date.",
            kind="lab",
            note="The script asserts the wrong-product outcome. Change one input at a time and inspect source IDs. The fake generator does not measure live reasoning or ranking quality.",
        ),
    ],
    [
        page(
            "Showcase / reject a convincing bad answer",
            "An attacker supplies closing tags and instructions.",
            "A generated draft cites an invented quote.",
            "A candidate has a lower faithfulness score.",
            note="Distinguish escaped syntax, citation validation and semantic evaluation. A delimiter test does not prove injection resistance; valid quotes do not establish every claim.",
        ),
        page(
            "Run prompt and evaluation demonstrations",
            "python -m training.showcase --session 3",
            "Tag escape retained; bad quote → abstention.",
            "Same cases: −0.25; changed dataset: refused.",
            kind="lab",
            note="Allow 25 minutes. Also exercise the output PII rail. Inspect prompt version 1.1.0, the one-repair limit and dataset/judge identity checks. Scores and drafts are visibly synthetic.",
        ),
        code(
            "Code / fingerprint each reviewed case",
            "app/evaluation/run.py",
            "def case_fingerprint",
            4,
            "Scope and reviewed expectations belong to case identity.",
        ),
        page(
            "Release decision / identity before score",
            "Align reviewed cases and the judge contract.",
            "Inspect case flips alongside aggregate deltas.",
            "Regenerate reports that lack identity evidence.",
            note="The application model or prompt may change deliberately. Dataset, judge model/prompt and metric versions must align. CLI exits 2 for incomparable evidence, 1 for regressions or newly failing cases. Live golden evaluation is still required before release.",
        ),
    ],
    [
        page(
            "Showcase / the service fails safely",
            "Provider failure → private details stay private.",
            "Repeated calls → the configured quota applies.",
            "Database failure → readiness reports unavailable.",
            note="Use actual FastAPI routing, dependency injection, limiter and schemas with fake dependencies. Readiness tests a database ping, not vector-index availability.",
        ),
        page(
            "Run the serving-failure demonstration",
            "python -m training.showcase --session 4",
            "Provider failures then quota: [503, 503, 429].",
            "Invalid input: 422; failed readiness: 503.",
            kind="lab",
            note="Allow 20 minutes. Predict which requests consume quota. The driver deadline is covered separately and is not a hard wall-clock guarantee. Limits are per process/client; this is not a distributed quota.",
        ),
        code(
            "Code / bound the database ping",
            "app/database/mongo.py",
            "def ping_database",
            4,
            "The driver deadline applies inside the offloaded call.",
        ),
        page(
            "Serving evidence to inspect",
            "Status, retry behavior and response privacy.",
            "Measure latency and cost under representative traffic.",
            "Offline failures establish no capacity target.",
            note="Retain an HTTP transcript. Explain health versus readiness and unknown versus passing measurements. Prices and SLO targets remain placeholders pending owner confirmation.",
        ),
    ],
    [
        page(
            "Showcase / a complaint becomes a test",
            "A staff member flags an unhelpful answer.",
            "A reviewer checks sources and accepts the signal.",
            "A separate curated answer becomes a golden case.",
            note="Acceptance does not authenticate the client response or certify the correction. Export requires the same input, explicit expected status/output and source references for an answered target. Detected PII is blocked.",
        ),
        page(
            "Run the reviewed-feedback demonstration",
            "python -m training.showcase --session 5",
            "No token: 401; pending: 409; curated export: 200.",
            "Validate JSONL, keep the review, rehearse recovery.",
            kind="lab",
            note="Allow 25 minutes. Actual API/services and institution-scoped database logic run with a Mongo fake. Validate the exported case via load_golden, inspect the audit bundle, then run the incident check. Nothing is deployed.",
        ),
        code(
            "Code / read the accepted stored review",
            "app/services/feedback.py",
            "record = await asyncio.to_thread(database.get_feedback",
            10,
            "The export decision uses server-side review state.",
        ),
        page(
            "Close the loop with evidence",
            "Signal → reviewed case → failing replay → fix.",
            "Keep the case and audit bundle under review.",
            "Release after quality and operational checks agree.",
            kind="flow",
            note="The workflow does not automate dataset promotion, training or deployment. An SME verifies policy meaning. Blue/green, memory and existing category mapping decisions remain outside this change.",
        ),
    ],
]
