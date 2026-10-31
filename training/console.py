"""Human-readable output for the training labs.

Application code logs JSON through structlog. The labs exist to be read by students, so they
write plain lines to stdout through this one helper instead of calling print().
"""

from __future__ import annotations

import sys


def say(*parts: object) -> None:
    sys.stdout.write(" ".join(str(part) for part in parts) + "\n")
