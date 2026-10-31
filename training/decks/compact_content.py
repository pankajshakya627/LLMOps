"""Sixteen-page teaching editions of Sessions 1 and 2, with code-grounded diagrams."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from training.decks.course_content import code, page


def compact_sessions(sessions: list[dict[str, Any]]) -> None:
    source = [{slide["title"]: slide for slide in session["slides"]} for session in sessions[:2]]
    lessons = {
        slide["lesson"]: {key: slide[key] for key in ("lesson", "lesson_title", "lesson_url")}
        for session in sessions[:2]
        for slide in session["slides"]
        if "lesson" in slide
    }

    def keep(session: int, title: str) -> dict[str, Any]:
        return deepcopy(source[session - 1][title])

    def topic(number: int, slide: dict[str, Any]) -> dict[str, Any]:
        slide.update(lessons[number])
        slide["note"] += f" Source lesson: {lessons[number]['lesson_url']}."
        return slide

    def architecture(
        number: int, title: str, *body: str, view: str, note: str, source: str
    ) -> dict[str, Any]:
        slide = topic(number, page(title, *body, kind="architecture", note=note, source=source))
        slide["architecture_view"] = view
        slide["relationships"] = (
            "link: labelled directed dependencies; boundary and element types distinguish C4 levels where named"
        )
        return slide

    s1 = [
        keep(1, "Discover"),
        keep(1, "LLMOps manages behavior under real constraints"),
        topic(
            2,
            page(
                "From models to operated applications",
                "AI → ML → GenAI → LLMs: a scope relationship.",
                "The application owns data, prompts and integration.",
                "Hosted-model behavior still needs measured evidence.",
                note="AI also includes non-learning systems; this is not a deployment pipeline. Research, the 2022 interface shift and the integration era explain the changing operating burden. Prompts, embeddings and knowledge change independently. These themes consolidate the longer lesson-2 reference pages.",
            ),
        ),
        keep(1, "What changes from MLOps to LLMOps"),
        keep(1, "Four phases, four decisions"),
        architecture(
            5,
            "C4 / system context",
            "People ask, review and maintain policy knowledge.",
            "NexaAssist depends on models, Atlas and optional telemetry.",
            view="context",
            source="docs/architecture/c4-context.md",
            note="Read the system as a black box. Staff ask scoped questions, the reviewer reviews feedback using a bearer credential, and the operator runs registered-file ingestion. The external model provider embeds and generates via HTTPS. Atlas supplies managed storage through the MongoDB protocol. Phoenix receives OpenInference traces and explicitly exported Ragas annotations. This working-copy view is not a production deployment or proof of user-level authorization.",
        ),
        architecture(
            5,
            "C4 / containers and ownership",
            "Streamlit renders; FastAPI coordinates the answer path.",
            "The ingestion CLI maintains Atlas knowledge collections.",
            view="containers",
            source="docs/architecture/c4-containers.md",
            note="Inside NexaAssist, Streamlit, FastAPI and the ingestion CLI are separate running applications. LangChain runs inside API/CLI processes and is not a separate service. Atlas stores child vectors, parent sections and feedback; these are logical collections, not separate database servers. The CLI embeds changed text through the model provider and upserts chunks/parents. The API reads scoped evidence, embeds queries, generates answers and optionally exports telemetry. The UI calls the API using JSON HTTP.",
        ),
        architecture(
            5,
            "Two paths share one knowledge contract",
            "Offline: prepare and publish trusted searchable evidence.",
            "Online: retrieve, generate and validate a scoped answer.",
            view="two-paths",
            source="app/chains/ingestion.py; app/services/retrieval.py; app/chains/answer.py",
            note="The offline path runs registered files through verification, parse, clause chunking, configured PII redaction, metadata/checksum comparison, changed-chunk embedding and upsert. Child vectors and unembedded parent sections live in Atlas. Online, validated scope and a scrubbed query drive retrieval; parents and complete linked amendments feed the answer prompt. The provider drafts a strict response and local citation/output checks accept it, ask for clarification or abstain. The two paths share document identity, effective dates and embedding compatibility.",
        ),
        architecture(
            5,
            "One answer / request and failure flow",
            "Validate → retrieve scoped evidence → build the prompt.",
            "Generate → check output → return answer or abstention.",
            view="answer-flow",
            source="app/api/answer.py; app/services/answer.py; app/chains/answer.py",
            note="The route validates the request and rate limit, then delegates. The service scrubs query identifiers. Retrieval applies institution, dates, jurisdiction, confidentiality and optional product filters, expands parents and resolves linked amendments. Missing evidence or an amendment that cannot fit ends in safe abstention without generation. Otherwise the strict draft is checked for PII and exact citations. Citation failure permits one repair, then abstention. A scope clarification becomes a fixed safe question. Returned provenance identifies prompt/model/retrieval/evidence. Sampling is optional background work, not streaming.",
        ),
        keep(1, "Freshness, permission and traceability are separate"),
        topic(
            5,
            code(
                "Code / pure chain, strict draft",
                "app/chains/answer.py",
                "generation = ANSWER_PROMPT",
                3,
                "The same LCEL chain is callable from the service and evaluation.",
            ),
        ),
        topic(
            6,
            page(
                "Scope the policy assistant before release",
                "Staff receive cited explanations or safe non-answers.",
                "Credit decisions and account actions are outside scope.",
                "The manifest names permitted sources and unresolved owners.",
                note="The Educative project is a fictional internal support assistant. NexaAssist adapts its principles to synthetic banking policy, retaining MongoDB Atlas and LangChain rather than PostgreSQL/pgvector and LiteLLM. Read training/use_case_manifest.md. Distinguish source permission from document freshness. Actual data, SME, product and operational approvers remain owner decisions.",
            ),
        ),
        topic(
            6,
            code(
                "Code / reject changed source bytes",
                "app/services/ingestion.py",
                "def _verify_source",
                6,
                "A source must match the register before parsing or embedding.",
            ),
        ),
        topic(
            6,
            page(
                "Practical / prove the source boundary",
                "python -m training.showcase --session 1",
                "Observe: 8 original documents verify.",
                "Tampered copy: hash mismatch; ingestion is refused.",
                kind="lab",
                note="Allow 20 minutes of the practical block. Predict the failing document, run the demonstration and inspect requests_from_register/_verify_source. Only a temporary copy is modified. Record the ID, verification error and release decision. Byte identity alone does not prove permission or correct policy meaning.",
            ),
        ),
        topic(
            6,
            page(
                "The release file is more than application code",
                "Record prompt, model, corpus and embedding identities.",
                "Attach golden results and measured operating evidence.",
                "Keep placeholder targets and missing approvals visible.",
                note="Use app/evaluation/gates.json and training/use_case_manifest.md. Thresholds and token prices remain placeholders; no live service or capacity evidence is established by offline fakes. CI, durable memory and blue/green promotion remain separate work. A compatible rollback includes chunk and parent collections, not only an index name. Read the longer handout for the gate-schema exercise.",
            ),
        ),
        page(
            "Session 1 / architecture exit gate",
            "Trace one staff question across the real layers.",
            "Explain which source or output failure stops an answer.",
            "Submit the scope manifest and source-verification evidence.",
            kind="gate",
            note="Use the diagrams and literal code excerpts as the assessment. Ask why LangChain is inside the API process, why lookup date differs from sanction date, and why missing measurement is not a pass. Supporting detail remains in the Session 1 handout and archived expanded deck. Next, prove the retrieval evidence before changing generation.",
        ),
    ]
    s1[3]["relationships"] = (
        "compare: four independent MLOps-to-LLMOps changes; each cell maps before to after"
    )
    s2 = [
        keep(2, "Distill I"),
        keep(2, "Documents carry meaning through structure"),
        architecture(
            7,
            "Ingestion / prepare evidence before embedding",
            "Verify → parse → chunk → redact and fingerprint.",
            "Embed changed children; publish children and parents.",
            view="ingestion",
            source="app/services/ingestion.py; app/chains/ingestion.py",
            note="The source register is verified before building requests. LCEL performs parse, clause chunking, configured redaction, enrichment/checksum, stored-checksum comparison and changed-child upsert. Entire parent sections are stored separately without embeddings. The service removes stale children after successful ingestion; one document failure is isolated and reported. Writes span collections and are not a concurrent transactional publisher. Provider disclosure occurs at embedding, so configured redaction must precede it.",
        ),
        architecture(
            7,
            "Storage / search children, read parent sections",
            "A child identifies the precise matched clause.",
            "Its parent supplies neighboring conditions and tables.",
            view="parents",
            source="app/chains/ingestion.py; app/chains/retrieval.py; app/database/mongo.py",
            note="For POL-HL-V3, clause 6.2 is a child in the fee section. parent_id links it to the complete section, which also contains other fee conditions. Atlas embeds child text; the parent store is not embedded. Retrieval verifies parent metadata scope and falls back to the child if the parent is missing or mismatched. A matched child is not the author of every parent clause. Required linked amendments are handled separately and the context packer never cuts a table.",
        ),
        keep(2, "Chunk around clauses, then size"),
        topic(
            7,
            code(
                "Code / the ingestion fingerprint",
                "app/chains/ingestion.py",
                "def chunk_checksum",
                7,
                "Text, metadata, embedding model and dimensions determine whether to re-embed.",
            ),
        ),
        topic(
            7,
            page(
                "Practical / observe repeatable ingestion",
                "python -m training.session2.ingest_twin",
                "Expected embedding counts: 32 → 0 → 32 → 0.",
                "Inspect one child ID, checksum and parent section.",
                kind="lab",
                note="The lab uses the real PDF and ingestion chain with deterministic fake embeddings and in-memory stores. Run 3 changes the model identifier; it demonstrates invalidation, not actual provider model compatibility. Run chunks and redact from the handout as extensions. Retain a table, an exception and a date caveat in the chunk experiment.",
            ),
        ),
        topic(
            8,
            page(
                "Embeddings and the Atlas index must agree",
                "Use the same model and dimensions for write and query.",
                "Create the vector/filter index from the documented JSON.",
                "Parent sections need no vector index.",
                note="Open app/database/indexes.md and app/chains/embeddings.py. The documented example uses 1536 dimensions; runtime configuration and the selected model must agree. Equal dimension count does not make two models compatible. The index must include every metadata filter field. The full-text Atlas Search index is separate and used only for configured hybrid retrieval. No live index is created or verified by this deck.",
            ),
        ),
        architecture(
            8,
            "Retrieval / scope first, then expand evidence",
            "Apply policy filters before ranking candidates.",
            "Expand parents and complete linked amendments.",
            view="retrieval",
            source="app/services/retrieval.py; app/chains/retrieval.py; app/database/retrieval.py",
            note="The scrubbed query and request scope feed a shared pre-filter. Dense search is the baseline; hybrid BM25/vector RRF and reranking are conditional settings. The parent store expands each matched child only after scope validation. Linked circulars are loaded by scoped database queries and can exceed top_k as separate amendments. The final context packs complete evidence within its budget. This diagram shows the baseline and names optional ranking in its search node; it does not imply every request uses all modes.",
        ),
        topic(
            8,
            code(
                "Code / date and permission filters",
                "app/chains/retrieval.py",
                "filters: list[dict[str, object]]",
                9,
                "Product scope is added when supplied; model similarity never overrides this filter.",
            ),
        ),
        architecture(
            8,
            "Amendments / lookup date and sanction date",
            "The circular enters policy scope on 1 July 2026.",
            "Its revised fee applies to sanctions from that date.",
            view="amendment-dates",
            source="nexa_synthetic_data/document_register.json; nexa_synthetic_data/policies/CIR-2026-07_Circular_NexaHome_Fee_and_PartPrepayment.pdf",
            note="The base processing fee is 0.35%, minimum ₹5,000 and maximum ₹15,000, plus GST. CIR-2026-07 clause 3.1 changes it to 0.30%, minimum ₹5,000 and maximum ₹10,000; clause 5.1 restricts it to sanctions on or after 1 July 2026. A July policy lookup for a June sanction retains the earlier fee. These are synthetic policy terms. Do not infer precedence from rank or a higher version number.",
        ),
        architecture(
            8,
            "Load the amendment's complete condition",
            "A fee quote without applicability can mislead.",
            "Resolve the linked instrument as a complete unit.",
            view="amendment-links",
            source="app/database/retrieval.py; app/models/retrieval.py",
            note="POL-HL-V3 clause 6.2 links through supersedes metadata to CIR-2026-07. The full circular supplies precedence (2.1), revised fee (3.1) and sanction applicability (5.1). Other terms remain unchanged and part-prepayment opt-in has a separate rule. Circular links are followed transitively. Inconsistent instrument metadata fails closed; an entirely missing indexed chunk cannot be detected without a source ingestion manifest.",
        ),
        keep(2, "Hit rate and multi-reference recall are different"),
        topic(
            8,
            page(
                "Practical / replay the July policy boundary",
                "python -m training.showcase --session 2",
                "June: 0.35% / POL-HL-V3; July: 0.30% / CIR-2026-07.",
                "Wrong product: insufficient_evidence; no citations.",
                kind="lab",
                note="The actual registered PDFs pass through real parsing, ingestion, scope filters, parent expansion, linked amendments and citation checks. Embeddings, vector ranking, Mongo transport and model drafts are fixtures. Both sanction and lookup dates are explicit in the two examples. Inspect full quoted text and record why the wrong product must abstain. This does not measure live model reasoning or Atlas recall.",
            ),
        ),
        topic(
            8,
            page(
                "Practical / diagnose a retrieval miss",
                "python -m training.session2.recall",
                "Compare k=1, 3 and 5; distinguish recall from rank.",
                "One of two required clauses found → recall 0.5.",
                kind="lab",
                note="Expected evidence is explicit document/clause identity. A first expected item at rank 4 has reciprocal rank 0.25, even when recall is 1 for a single-reference case. A full linked circular can satisfy both required clauses. The lab scores constructed results through the actual scorer; these are not measured retrieval results. Course single-reference hit rate and multi-reference recall are different definitions.",
            ),
        ),
        page(
            "Session 2 / evidence exit gate",
            "Show a stable child ID and a compatible parent scope.",
            "Find fee plus applicability; report missing references.",
            "Submit recall/MRR evidence and unresolved live checks.",
            kind="gate",
            note="Require the chunk experiment, re-ingestion transcript and two-clause retrieval diagnosis. Quality gates remain placeholder targets. Live Atlas retrieval requires a compatible queryable index and approved credentials; a local Mongo fake is not Atlas Vector Search. Keep candidate chunk/parent collections and embedding versions compatible for any future blue/green plan. Next, control what generation may claim.",
        ),
    ]
    for session, slides in zip(sessions[:2], (s1, s2), strict=True):
        assert len(slides) == 16
        session["slides"] = slides
        session["slides"][0]["body"][1] = (
            f"Session {session['number']} of 5 · 16-slide teaching edition"
        )
