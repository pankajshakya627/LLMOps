"""Lab 6: show personal-data redaction before embedding.

Run from the project root: uv run --no-sync python -m training.session2.redact
No network, database or model key is used.
"""

from __future__ import annotations

from app.chains.redaction import redact
from training.console import say

samples = [
    "Contact asha.rao@nexabank.example or +91 98765 43210 for exceptions.",
    "Customer PAN ABCDE1234F, Aadhaar 1234 5678 9012.",
    "Maximum loan Rs 7,50,00,000 for 240 months at 0.30% fee (min 5,000, max 10,000).",
    "Reference number 9876543210123 was issued in clause 6.2.",
]
for text in samples:
    clean, counts = redact(text)
    say("IN :", text)
    say("OUT:", clean, dict(counts), "\n")
