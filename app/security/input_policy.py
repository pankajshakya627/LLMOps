from __future__ import annotations

import re
import unicodedata

import structlog


class UnsafeQueryError(Exception):
    """The query contains a direct request to override the application's rules."""


RULES = (
    re.compile(
        r"(?:^|[.!?;\n])\s*(?:please\s+)?(?:ignore|disregard|override|forget)\s+"
        r"(?:(?:all|any|the)\s+)?(?:(?:previous|prior|above|system|developer|policy|safety)\s+)+"
        r"(?:instructions?|rules?|prompts?)\b"
    ),
    re.compile(
        r"(?:^|[.!?;\n])\s*(?:please\s+)?(?:reveal|print|dump|show)\s+"
        r"(?:the\s+)?(?:system|developer)\s+(?:prompt|instructions?)\b"
    ),
)


def enforce_input_policy(query: str) -> None:
    # shortcut: explicit English overrides only, add a measured classifier for broader semantic attacks.
    normalized = unicodedata.normalize("NFKC", query).casefold()
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Cf")
    if any(rule.search(normalized) for rule in RULES):
        structlog.get_logger().warning("prompt_injection_blocked")
        raise UnsafeQueryError("Query blocked by security policy.")
