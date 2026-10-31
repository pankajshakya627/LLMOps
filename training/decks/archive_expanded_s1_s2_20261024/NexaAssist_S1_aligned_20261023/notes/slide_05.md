python -m training.showcase --session 1 Original: 8 documents verified. Tampered copy: hash mismatch; ingestion refused. Allow 12 minutes. Run from the root using the existing environment. The script changes a temporary copy. Retain the document ID and mismatch, then name the release artifact needing review.

Code walkthrough: app/services/ingestion.py
def requests_from_register(register_path: Path, settings: Settings) -> list[IngestRequest]:
    """One IngestRequest per authoritative document in document_register.json.

    Each source file must match the register's sha256 before it can be ingested.
    """
    return [
        IngestRequest(
            source_path=_verify_source(register_path.parent / entry["file"], entry),
            doc_id=entry["doc_id"],
            title=entry["title"],

Input: registered file and expected SHA-256. Failure: mismatch before parsing or embedding. Decision: hold ingestion and review the source. Submit a transcript, source ID and owner decision. Byte identity does not establish permission or semantic correctness.