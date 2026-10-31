python -m training.showcase --session 5 No token: 401; pending: 409; curated export: 200. Validate JSONL, keep the review, rehearse recovery. Allow 25 minutes. Actual API/services and institution-scoped database logic run with a Mongo fake. Validate the exported case via load_golden, inspect the audit bundle, then run the incident check. Nothing is deployed.

Code walkthrough: app/services/feedback.py
    record = await asyncio.to_thread(database.get_feedback, feedback_id, settings)
    if record is None:
        raise LookupError("Feedback not found")
    if record.status != "accepted" or not record.reviewer or not record.review_note.strip():
        raise ValueError("Accepted feedback with a reviewer and review note is required")
    if case.input != record.request:
        raise ValueError("Golden input must match the reviewed feedback request")
    if case.expected_status == "answered" and not case.context:
        raise ValueError("An answered golden case requires source references")
    if redact(case.model_dump_json())[1]:

Signal → reviewed case → failing replay → fix. Keep the case and audit bundle under review. Release after quality and operational checks agree. The workflow does not automate dataset promotion, training or deployment. An SME verifies policy meaning. Blue/green, memory and existing category mapping decisions remain outside this change.