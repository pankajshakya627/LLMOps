from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


def run_lab(module: str, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a training lab exactly as a student would: from the project root, offline."""
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )


def test_session1_tamper_lab_accepts_the_original_and_refuses_a_changed_file() -> None:
    result = run_lab("training.session1.tamper")
    assert result.returncode == 0, result.stderr
    assert "1. untouched copy: 8 documents verified" in result.stdout
    assert "2. tampered copy refused: POL-HL-V3: file sha256 does not match" in result.stdout


def test_session1_gate_check_accepts_shipped_file_and_rejects_bad_numbers(tmp_path: Path) -> None:
    shipped = run_lab("training.session1.check_gates", "app/evaluation/gates.json")
    assert shipped.returncode == 0, shipped.stderr
    assert "status=placeholder" in shipped.stdout

    broken = json.loads(Path("app/evaluation/gates.json").read_text())
    broken["faithfulness_min"] = 1.5
    path = tmp_path / "gates.json"
    path.write_text(json.dumps(broken))
    rejected = run_lab("training.session1.check_gates", str(path))
    assert rejected.returncode == 1
    assert "faithfulness_min" in rejected.stdout


def test_session2_chunk_lab_shows_that_size_only_matters_for_oversized_clauses() -> None:
    result = run_lab("training.session2.chunks")
    assert result.returncode == 0, result.stderr
    assert "max_characters=  300:  40 chunks, 5 with a table, longest 372 chars" in result.stdout
    assert "max_characters= 1200:  32 chunks, 5 with a table, longest 530 chars" in result.stdout
    assert "max_characters= 5000:  32 chunks, 5 with a table, longest 530 chars" in result.stdout
    assert "<table>" in result.stdout


def test_session2_ingestion_twin_is_idempotent_and_reembeds_on_a_model_change() -> None:
    result = run_lab("training.session2.ingest_twin")
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.startswith("run ")]
    assert [line.split("embedded=")[1].split()[0] for line in lines] == ["32", "0", "32", "0"]
    assert "parent_id            POL-HL-V3_s03" in result.stdout


def test_session2_asof_lab_prints_the_filter_and_versions_in_force() -> None:
    result = run_lab("training.session2.asof")
    assert result.returncode == 0, result.stderr
    assert '{"effective_date": {"$lte": "2026-06-30"}}' in result.stdout
    assert '{"confidentiality_level": "internal"}' in result.stdout
    assert "2026-06-30: POL-HL-V3, POL-PL-V1" in result.stdout
    assert "2026-07-01: POL-HL-V3, CIR-2026-07" in result.stdout


def test_session2_recall_lab_scores_the_four_scenarios() -> None:
    result = run_lab("training.session2.recall")
    assert result.returncode == 0, result.stderr
    assert "B: right clause is rank 4        recall@k=1.0  mrr=0.25" in result.stdout
    assert "D: empty result                  recall@k=0.0" in result.stdout
    assert "'recall_at_k': 0.5" in result.stdout


def test_session2_redaction_lab_masks_identifiers_but_not_amounts() -> None:
    result = run_lab("training.session2.redact")
    assert result.returncode == 0, result.stderr
    assert "[REDACTED_EMAIL]" in result.stdout and "[REDACTED_AADHAAR]" in result.stdout
    assert "OUT: Maximum loan Rs 7,50,00,000 for 240 months" in result.stdout


@pytest.mark.parametrize("session", [f"session{i}" for i in range(1, 6)])
def test_every_handout_names_only_modules_that_exist(session: str) -> None:
    text = (Path("training") / session / "handout.md").read_text()
    modules = set(re.findall(r"training\.session\d\.\w+", text))
    modules.update(re.findall(r"python\s+-m\s+(app\.[\w.]+)", text))
    assert modules, "the handout should name an application or lab module to run"
    for module in modules:
        assert Path(module.replace(".", "/") + ".py").is_file(), module


@pytest.mark.parametrize(
    "module,expected",
    [
        ("training.session3.answers", "output PII: status=insufficient_evidence, model_calls=1"),
        ("training.session3.gates", "generation fault: gate=FAIL, failure_type=generation_error"),
        ("training.session4.serving", "two provider failures then rate limit: [503, 503, 429]"),
        ("training.session5.incident", "no traffic: all SLOs not_measured"),
        ("training.session3.prompt_boundaries", "production prompt rendered"),
        ("training.session4.capacity", "Scenario cost: daily=$0.15, 30 days=$4.50"),
        ("training.session5.memory_design", "bounded fixture: 2 messages"),
        ("training.session2.policy_dates", "2026-07-01: fee=0.30%; cited=CIR-2026-07"),
        ("training.session3.comparison", "different dataset: comparison refused"),
        ("training.session5.feedback_loop", "accepted + curated target=200"),
    ],
)
def test_later_session_labs(module: str, expected: str) -> None:
    result = run_lab(module)
    assert result.returncode == 0, result.stderr
    assert expected in result.stdout


def test_showcase_entry_point_runs_one_session() -> None:
    result = run_lab("training.showcase", "--session", "5")
    assert result.returncode == 0, result.stderr
    assert "SESSION 5" in result.stdout and "SESSION 4" not in result.stdout
    assert "accepted + curated target=200" in result.stdout
    assert result.stdout.index("SESSION 5") < result.stdout.index("export without token")
