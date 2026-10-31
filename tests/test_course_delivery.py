from __future__ import annotations

import json
import re
from pathlib import Path
from posixpath import normpath
from xml.etree import ElementTree
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1] / "training/decks"


def test_local_course_and_project_document_links_resolve() -> None:
    missing = []
    documents = list(ROOT.parent.glob("session*/*.md")) + list(ROOT.parents[1].glob("*.md"))
    for document in documents:
        for link in re.findall(r"\]\(([^)]+)\)", document.read_text()):
            target = link.split("#", 1)[0]
            if (
                target
                and "://" not in target
                and not target.startswith("mailto:")
                and not (document.parent / target).exists()
            ):
                missing.append(f"{document.name}: {target}")
    assert not missing, "Broken course links: " + "; ".join(missing)


def test_first_two_sessions_are_compact_editable_architecture_decks() -> None:
    manifest = json.loads((ROOT / "course_manifest.json").read_text())
    for session in manifest[:2]:
        number = session["number"]
        # Session 2's expanded core brief explicitly permits up to 19 slides.
        assert 12 <= len(session["slides"]) <= (16 if number == 1 else 19)
        with ZipFile(ROOT / f"Session_{number}.pptx") as deck:
            pages = [
                name
                for name in deck.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            ]
            assert len(pages) == len(session["slides"])
            canvas = ElementTree.fromstring(deck.read("ppt/presentation.xml")).find(
                "{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz"
            )
            assert (
                canvas is not None
                and abs(int(canvas.attrib["cx"]) / int(canvas.attrib["cy"]) - 16 / 9) < 0.001
            )
            diagrams = [
                i for i, slide in enumerate(session["slides"], 1) if slide.get("architecture_view")
            ]
            assert len(diagrams) >= 4
            for page in diagrams:
                xml = ElementTree.fromstring(deck.read(f"ppt/slides/slide{page}.xml"))
                assert xml.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/main}t"), (
                    "Diagrams must retain native labels"
                )
                authoring_source = session["slides"][page - 1].get(
                    "native_authoring_source",
                    f"NexaAssist_S{number}_aligned_20261023/svg_output/slide_{page:02d}.svg",
                )
                svg = ElementTree.parse(ROOT / authoring_source)
                assert any(element.get("marker-end") for element in svg.iter()), (
                    "Relationships need arrowheads"
                )
                # Imported native objects retain their source IDs; require a visible
                # diagram caption in the legend band as well as authored legend groups.
                assert any(
                    element.get("id") == "diagram-legend"
                    or (
                        element.tag == "{http://www.w3.org/2000/svg}text"
                        and 590 <= float(element.get("y", "0")) <= 650
                        and "".join(element.itertext()).strip()
                    )
                    for element in svg.iter()
                )


def test_session2_core_covers_requested_tools_and_model_profiles() -> None:
    namespace = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    with ZipFile(ROOT / "Session_2.pptx") as deck:
        slides = [
            name
            for name in deck.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
        assert len(slides) == 19
        text = " ".join(
            node.text or ""
            for name in slides
            for node in ElementTree.fromstring(deck.read(name)).iter(namespace + "t")
        )
    for required in (
        "Phoenix",
        "Ragas",
        "LiteLLM",
        "Guardrails AI",
        "qwen3.5:9b-mlx",
        "qwen3-embedding:0.6b",
        "text-embedding-3-small",
        "OpenAI",
    ):
        assert required in text


def test_all_course_lessons_were_visited_and_have_published_slide_coverage() -> None:
    visits = json.loads((ROOT / "course_visit_log.json").read_text())
    coverage = json.loads((ROOT / "lesson_coverage.json").read_text())
    assert visits["unvisited_course_links"] == []
    assert len(visits["visits"]) == 17
    assert all(5 <= visit["elapsed_seconds"] <= 10 for visit in visits["visits"])
    assert {row["lesson"] for row in coverage} == set(range(1, 17))
    assert {row["url"] for row in coverage} <= {v["url"] for v in visits["visits"]}
    for session in range(1, 6):
        with ZipFile(ROOT / f"Session_{session}.pptx") as deck:
            slides = [
                n
                for n in deck.namelist()
                if n.startswith("ppt/slides/slide") and n.endswith(".xml")
            ]
            notes = [
                n
                for n in deck.namelist()
                if n.startswith("ppt/notesSlides/notesSlide") and n.endswith(".xml")
            ]
            assert len(slides) == len(notes)
            for row in coverage:
                if row["session"] == session:
                    for number in row["slides"]:
                        assert f"ppt/slides/slide{number}.xml" in slides
                        relationships = ElementTree.fromstring(
                            deck.read(f"ppt/slides/_rels/slide{number}.xml.rels")
                        )
                        note_link = next(
                            link
                            for link in relationships
                            if link.attrib["Type"].endswith("/notesSlide")
                        )
                        note = ElementTree.fromstring(
                            deck.read(normpath("ppt/slides/" + note_link.attrib["Target"]))
                        )
                        assert row["url"] in " ".join(note.itertext())
