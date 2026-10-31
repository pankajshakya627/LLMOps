from __future__ import annotations

import re
from collections import Counter

# Order matters: the longer, more specific patterns run before the digit-only ones.
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")),
    ("PAN", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")),
    ("AADHAAR", re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b")),
    ("PHONE", re.compile(r"(?<![\d,])(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}(?![\d,])")),
)


def redact(text: str) -> tuple[str, Counter[str]]:
    """Replace personal identifiers with typed placeholders; report how many of each."""
    counts: Counter[str] = Counter()
    for kind, pattern in PATTERNS:
        text, replaced = pattern.subn(f"[REDACTED_{kind}]", text)
        if replaced:
            counts[kind] = replaced
    return text, counts
