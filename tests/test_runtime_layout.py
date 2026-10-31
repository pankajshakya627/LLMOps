from __future__ import annotations

import ast
import re
from pathlib import Path

from app.evaluation.gates import load_gates
from app.evaluation.run import load_cases

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"


def test_runtime_resources_are_owned_by_the_application() -> None:
    assert (
        (APP / "observability/requirements-server.txt")
        .read_text()
        .strip()
        .endswith("arize-phoenix==20.26.0")
    )
    assert (APP / "observability/requirements-client.txt").is_file()
    assert (APP / "observability/README.md").is_file()
    assert (APP / "operations/README.md").is_file()
    assert (APP / "README.md").is_file()
    assert len(load_cases(APP / "evaluation/datasets/answer.jsonl")) == 10
    assert load_gates(APP / "evaluation/gates.json").status == "placeholder"


def test_application_code_does_not_import_course_modules() -> None:
    for path in APP.rglob("*.py"):
        if "results" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert not node.value.startswith(
                    ("training/", "evaluation/gates.json", "evaluation/datasets/")
                ), path
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("training"), path
            elif isinstance(node, ast.Import):
                assert all(not alias.name.startswith("training") for alias in node.names), path


def test_legacy_fixture_paths_resolve_to_the_app_owned_files() -> None:
    for name in ("gates.json", "datasets/answer.jsonl", "datasets/retrieval.jsonl"):
        legacy = ROOT / "evaluation" / name
        assert legacy.is_symlink()
        assert legacy.resolve() == APP / "evaluation" / name


def test_project_runtime_commands_do_not_require_course_paths() -> None:
    for path in [ROOT / "README.md", APP / "README.md", *APP.rglob("README.md")]:
        if "results" in path.parts:
            continue
        for block in re.findall(r"```(?:bash|sh)\n(.*?)```", path.read_text(), re.DOTALL):
            assert "training/" not in block and "training." not in block, path
    dockerfile = (APP / "Dockerfile").read_text()
    assert "COPY --chmod=u=rw,go=r evaluation/" not in dockerfile
