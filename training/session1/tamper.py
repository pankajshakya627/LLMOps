"""Lab 3: show that ingestion refuses a source document that differs from the register.

Run from the project root: uv run --no-sync python -m training.session1.tamper
Works on a temporary copy; nothing in the project is changed. No network or credentials.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from app.core.config import Settings
from app.services.ingestion import requests_from_register
from training.console import say

settings = Settings(
    _env_file=None,
    mongodb_uri="mongodb://unused",
    mongodb_db="d",
    mongodb_collection="c",
    openai_api_key="unused",
    institution="NexaBank",
    jurisdiction="IN",
    confidentiality_level="internal",
)
source = Path("nexa_synthetic_data")
work = Path(tempfile.mkdtemp())
shutil.copytree(source / "policies", work / "policies")
shutil.copy(source / "document_register.json", work / "document_register.json")

verified = requests_from_register(work / "document_register.json", settings)
say("1. untouched copy:", len(verified), "documents verified")

victim = work / "policies" / "POL-HL-V3_NexaHome_Loan_Policy_v3.0.pdf"
data = bytearray(victim.read_bytes())
data[-20] ^= 1  # flip one bit near the end of the file
victim.write_bytes(bytes(data))
try:
    requests_from_register(work / "document_register.json", settings)
except ValueError as error:
    say("2. tampered copy refused:", error)
shutil.rmtree(work)
