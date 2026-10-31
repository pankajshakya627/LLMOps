python -m training.showcase --session 2 June: 0.35% / POL-HL-V3. July: 0.30% / CIR-2026-07; quotes verified. Allow 20 minutes. Parsing, ingestion, date/product filters, parent expansion, linked amendments and answer checks are real code. Mongo transport, embedding, ranking and model outputs are fixtures. Inspect the full circular, including applicability and revised caps.

Code walkthrough: app/chains/retrieval.py
        if amendment_search is not None and rows:
            documents = await amendment_search.ainvoke(
                {
                    "doc_ids": list(
                        dict.fromkeys(document.metadata["doc_id"] for document, _ in rows)
                    ),
                    "pre_filter": {"$and": filters},
                }
            )
            amendments = [

NEXA-HL → NEXA-PL with the fee question. Expect insufficient_evidence and no citation. Explain the separate role of the sanction date. The script asserts the wrong-product outcome. Change one input at a time and inspect source IDs. The fake generator does not measure live reasoning or ranking quality.