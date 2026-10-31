"""Lab 1: chunk a policy PDF at three sizes and show a table chunk and per-document counts.

Run from the project root: uv run --no-sync python -m training.session2.chunks
No network, database or model key is used.
"""

from __future__ import annotations

from pathlib import Path

from app.chains.chunking import chunk_by_clause
from app.chains.parsing import parse_document
from training.console import say

POLICIES = Path("nexa_synthetic_data/policies")
v3 = POLICIES / "POL-HL-V3_NexaHome_Loan_Policy_v3.0.pdf"
elements = parse_document(str(v3))
say(
    "parsed elements:",
    len(elements),
    "| first:",
    type(elements[0]).__name__,
    repr(elements[0].text[:50]),
)

for size in (300, 1200, 5000):
    chunks = chunk_by_clause(elements, size, 150)
    longest = max(len(c.text) for c in chunks)
    say(
        f"max_characters={size:>5}: {len(chunks):>3} chunks, {sum(c.has_table for c in chunks)} with a table, longest {longest} chars"
    )

say("\n--- a table chunk (kept whole) ---")
table = next(c for c in chunk_by_clause(elements, 1200, 150) if c.clause == "3.4")
say(table.section, "|", table.clause, table.clause_heading)
say(table.text[:260])

say("\n--- chunks per document at 1200 ---")
for pdf in sorted(POLICIES.glob("*.pdf")):
    if pdf.name.startswith(("POL-", "CIR-")):
        say(f"{pdf.name[:34]:<36}", len(chunk_by_clause(parse_document(str(pdf)), 1200, 150)))
