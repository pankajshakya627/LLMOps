"""Author editable SVG slide sources; export with the ppt-master tools documented in README."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

from training.console import say
from training.decks.aligned_content import SESSIONS

BASE = Path(__file__).resolve().parent
SKILL = Path("/Users/pankaj/.agents/skills/ppt-master")
COLORS = {
    "background": "#F5F3EC",
    "primary": "#132C42",
    "body_text": "#132C42",
    "secondary_text": "#526375",
    "divider": "#CCD3D8",
    "surface": "#FFFFFF",
    "secondary_background": "#E8EDF0",
    "positive": "#176849",
    "warning": "#98521A",
    "negative": "#A13442",
}
ROLES = {
    "body": 26,
    "title": 40,
    "subtitle": 30,
    "annotation": 20,
    "footnote": 16,
    "display": 76,
    "code": 20,
}


def folder(session: dict[str, Any]) -> Path:
    return BASE / f"NexaAssist_S{session['number']}_aligned_20261023"


def prepare(session: dict[str, Any]) -> None:
    target = folder(session)
    if not target.exists():
        subprocess.run(
            [
                sys.executable,
                str(SKILL / "scripts/project_manager.py"),
                "init",
                f"NexaAssist_S{session['number']}_aligned",
                "--dir",
                str(BASE),
            ],
            check=True,
        )
    (target / "sources/course_sources.md").write_text(
        "# Source record\n\nEducative LLMOps: https://www.educative.io/courses/llmops\n"
        "Read all 16 lessons and the overview via signed-in Safari on 2026-10-23, allowing seven seconds per page. "
        "Every course lesson link discovered on those pages was visited; see course_visit_log.json. "
        "This is original NexaAssist courseware, not a reproduction of Educative lesson text.\n\n"
        f"Session {session['number']}: lesson themes {session['lessons']}. Five sessions and lab sequence are our adaptation.\n"
        "Implementation source: local app/, evaluation/, tests/ and training/. "
        "No live benchmark, model availability or current provider price is asserted.\n"
    )
    colors = {**COLORS, "accent": session["accent"]}
    info = {
        "Project Name": target.name,
        "Canvas Format": "PPT 16:9, 1280 × 720",
        "Page Count": str(len(session["slides"])),
        "Primary Language": "en",
        "Target Audience": "Python developers with REST familiarity",
        "Communication Intent": "Teach concepts through actual NexaAssist code and practical failure experiments",
        "Desired Audience Outcome": "Run the session labs and defend an evidence-based gate decision",
        "Core Message / Ask / Action": "Version, measure and review the artifacts that change RAG behavior",
        "Delivery Context": "Instructor-led three-hour workshop",
        "Artifact Afterlife": "Editable slides, notes and repo handouts",
        "Reading Mode": "balanced",
        "Content Strategy": "Original code walkthroughs, concise concepts and concrete exercises",
        "Design Style": "Engineering field guide",
        "AI Image Acquisition Path": "not applicable",
        "Generation Mode": "continuous",
        "Spec Refinement": "disabled",
        "Speaker Notes": "enabled — delegated author decision",
        "Custom Animations": "disabled — delegated author decision",
        "Narration Audio": "disabled — delegated author decision",
        "Created Date": "2026-10-23",
    }
    out = [
        "<!-- ppt-master-schema: design-spec/v1 -->",
        f"# {target.name} - Design Spec",
        "\n## I. Project Information",
        "\n| Item | Value |",
        "| --- | --- |",
    ]
    out += [f"| {k} | {v} |" for k, v in info.items()]
    out += [
        "\n## II. Canvas Specification",
        "\n| Property | Value |",
        "| --- | --- |",
        "| Format | PPT 16:9 |",
        "| Dimensions | 1280 × 720 |",
        "| viewBox | `0 0 1280 720` |",
        "| Margins | 64 px |",
        "| Content Area | 64 160 1152 470 |",
        "\n## III. Visual Theme",
        "\n### Theme Style",
        "- **Mode**: custom",
        "- **Mode Behavior**: Start with a measurable outcome, explain the mechanism, exercise real code, inspect failure and close with a gate.",
        "- **Visual style**: custom",
        "- **Visual Style Behavior**: Engineering field guide with warm paper, dark code fields, numbered sequences and broad whitespace; use sharp edges and a restrained per-session accent.",
        "- **Theme**: NexaAssist engineering workshop",
        "- **Tone**: Precise, practical and candid",
        "\n### Color Scheme",
        "\n| Role | HEX | Purpose |",
        "| --- | --- | --- |",
    ]
    out += [f"| {k.replace('_', ' ').title()} | {v} | {k} |" for k, v in colors.items()]
    out += [
        "\n## IV. Typography System",
        "\n### Font Plan",
        "\n| Role | Character (Reference) | Primary | English if non-English | Fallback tail |",
        "| --- | --- | --- | --- | --- |",
        "| Title | Strong technical sans | Trebuchet MS | | |",
        "| Body | Neutral readable sans | Arial | | |",
        "| Code | Literal monospace | Courier New | | |",
        "- **Title stack**: Trebuchet MS",
        "- **Body stack**: Arial",
        "- **Code stack**: Courier New",
        "- **Display stack**: Trebuchet MS",
        "- **Role rationale**: Code preserves source indentation; display establishes the session title.",
        "\n### Font Size Hierarchy",
        "\n| Purpose | Anchor Size (px) |",
        "| --- | ---: |",
    ]
    out += [f"| {k.title()} | {v} |" for k, v in ROLES.items()]
    out += [
        "\n## V. Layout Principles",
        "\n### Deck-wide Direction",
        "- **Hierarchy direction**: Title, mechanism or exercise, interpretation.",
        "- **Composition tendency**: Mix open text, code fields, vertically numbered flows and lab/gate pages.",
        "- **Cross-page continuity**: Session accent, stable footer and source caption.",
        "- **Spacing posture**: Variable by teaching duty.",
        "- **Spacing anchors**: page margin 64 px; block gap 24 px; column gutter 40 px; corner radius 0 px; body leading 38 px.",
        "\n## VI. Icon Usage Specification",
        "- **Primary bundled library**: none",
        "\n| Icon Path | Suitable Scenarios |",
        "| --- | --- |",
        "\n## VIII. Image Resource List",
        "\n| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        "\nNo raster images: diagrams and actual code communicate the mechanisms directly.",
        "\n## IX. Content Outline",
    ]
    for i, slide in enumerate(session["slides"], 1):
        relation = (
            "link: labelled dependencies between the stated units"
            if slide["kind"] == "diagram"
            else "order: stages follow the written sequence"
            if slide["kind"] == "flow"
            else "none"
        )
        relation = slide.get("relationships", relation)
        content = " · ".join(slide["body"])
        if slide["kind"] == "code":
            content += " Source excerpt: " + slide["code"].replace("\n", " / ")
        out += [
            f"\n#### Slide {i:02d} - {slide['title']}",
            f"- **Audience move**: Uncertain about {slide['title'].lower()} → can explain the mechanism or required decision.",
            f"- **Relationships**: {relation}",
            f"- **Composition**: {slide['kind']} page, with the dominant teaching task as focal point.",
            f"- **Title**: {slide['title']}",
            f"- **Core message**: {slide['body'][0]}",
            f"- **Content**: {content}",
        ]
    out += [
        "\n## X. Speaker Notes Requirements",
        "- **Generation**: enabled",
        "Explain visible claims, practical commands, expected outcomes, sources and limitations.",
    ]
    (target / "design_spec.md").write_text("\n".join(out) + "\n")
    lock = [
        "<!-- ppt-master-schema: spec-lock/v1 -->",
        "# Execution Lock",
        "\n## canvas",
        "- viewBox: 0 0 1280 720",
        "- format: PPT 16:9",
        "\n## communication",
        "- primary_language: en",
        "- audience: Python developers with REST familiarity",
        "- objective: Run NexaAssist practicals and defend the session gate decision.",
        "- core_message: Version, measure and review the artifacts that change RAG behavior.",
        "- consumption_mode: balanced",
        "\n## mode",
        "- mode: custom",
        "- mode_behavior: Explain a mechanism, exercise the code, diagnose failure and close with a gate.",
        "\n## visual_style",
        "- visual_style: custom",
        "- visual_style_behavior: Warm paper, dark code fields, numbered flows and restrained accent; vary composition by teaching duty.",
        "\n## colors",
    ]
    lock += [f"- {k}: {v}" for k, v in colors.items()]
    lock += [
        "\n## typography",
        "- font_family: Arial",
        "- title_family: Trebuchet MS",
        "- body_family: Arial",
        "- code_family: Courier New",
        "- display_family: Trebuchet MS",
    ]
    lock += [f"- {k}: {v}" for k, v in ROLES.items()]
    lock += ["\n## icons", "- library: none", "- inventory: none", "\n## page_rhythm"]
    lock += [
        f"- P{i:02d}: "
        + (
            "anchor"
            if s["kind"] in ("cover", "ending", "gate")
            else "dense"
            if s["kind"] == "code"
            else "breathing"
        )
        for i, s in enumerate(session["slides"], 1)
    ]
    lock += [
        "\n## pptx_structure",
        "- mode: flat",
        "\n## forbidden",
        "- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`",
        "- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters",
    ]
    (target / "spec_lock.md").write_text("\n".join(lock) + "\n")


def text(
    x: int,
    y: int,
    value: str,
    size: int = 26,
    fill: str = "#132C42",
    family: str = "Arial",
    width: int = 1080,
    leading: int = 38,
) -> str:
    # shortcut: deterministic wrapping uses a conservative character estimate; validate SVG extents before exporting.
    lines = (
        [value]
        if family == "Courier New"
        else textwrap.wrap(
            value,
            width=max(8, int(width / (size * 0.57))),
            break_long_words=False,
            break_on_hyphens=False,
        )
        or [""]
    )
    spans = "".join(
        f'<tspan x="{x}" y="{y + i * leading}">{html.escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return f'<text xml:space="preserve" x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}">{spans}</text>'


def group(identity: str, bounds: str, content: str) -> str:
    return f'<g id="{identity}" data-pptx-bounds="{bounds}">{content}</g>'


def draw(session: dict[str, Any], number: int) -> None:
    slide = session["slides"][number - 1]
    target = folder(session)
    kind = slide["kind"]
    accent = session["accent"]
    dark = kind in ("cover", "section", "gate", "ending")
    bg = "#132C42" if dark else "#F5F3EC"
    ink = "#FFFFFF" if dark else "#132C42"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" data-pptx-page-role="{"cover" if kind == "cover" else "ending" if kind == "ending" else "content"}">',
        f'<rect id="background" data-pptx-role="background" x="0" y="0" width="1280" height="720" fill="{bg}"/>',
        group(
            "session-label",
            "64 27 1152 26",
            text(
                64,
                47,
                f"NEXAASSIST  /  SESSION {session['number']:02d}  /  {session['title'].upper()}",
                16,
                "#BBCBD7" if dark else "#526375",
            ),
        ),
    ]
    if kind == "diagram":
        parts.append(
            f'<defs><marker id="diagram-arrow" markerWidth="8" markerHeight="8" '
            f'refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" '
            f'fill="{accent}"/></marker></defs>'
        )
    if kind == "cover":
        parts += [
            group(
                "cover-title",
                "64 150 1000 125",
                text(64, 230, slide["title"], 76, ink, "Trebuchet MS"),
            ),
            group(
                "cover-subtitle",
                "64 295 1000 100",
                text(64, 330, session["subtitle"], 30, ink, width=1000, leading=42),
            ),
            group(
                "cover-description",
                "64 475 1050 95",
                text(64, 510, "\n".join(slide["body"]), 26, ink, width=1050),
            ),
            f'<rect id="accent-bar" data-pptx-role="decoration" x="64" y="402" width="160" height="6" fill="{accent}"/>',
        ]
    else:
        parts.append(
            group(
                "page-title",
                "64 76 1152 120",
                text(64, 123, slide["title"], 40, ink, "Trebuchet MS", width=1152, leading=50),
            )
        )
        if kind == "code":
            source = slide["source"]
            code_lines = textwrap.dedent(slide["code"]).splitlines()
            assert len(code_lines) <= 12
            code_size = 18 if max(map(len, code_lines)) > 82 else 20
            code_svg = '<rect x="64" y="205" width="1152" height="335" fill="#132C42"/>'
            for i, line in enumerate(code_lines):
                assert len(line) <= 102, (source, line)
                code_svg += text(
                    88,
                    237 + i * 25,
                    line,
                    code_size,
                    "#F5F3EC",
                    "Courier New",
                    width=1090,
                    leading=25,
                )
            parts.append(group("source-code", "64 205 1152 335", code_svg))
            parts.append(
                group(
                    "interpretation",
                    "64 565 1135 75",
                    text(64, 592, slide["body"][0], 26, width=1135),
                )
            )
        elif kind == "diagram":
            nodes = slide["nodes"]
            positions = [(64, 240), (736, 240), (736, 455), (64, 455)]
            content = ""
            for a, b, label in slide["edges"]:
                x1, y1 = positions[a]
                x2, y2 = positions[b]
                if y1 == y2:
                    right = x2 > x1
                    ax, ay = x1 + (480 if right else 0), y1 + 62
                    bx, by = x2 + (0 if right else 480), y2 + 62
                    lx, ly = min(ax, bx) + 16, ay - 15
                else:
                    ax, ay = x1 + 240, y1 + 124
                    bx, by = x2 + 240, y2
                    lx, ly = min(ax, bx) + 14, (ay + by) // 2
                content += (
                    f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" '
                    f'stroke="{accent}" stroke-width="3" marker-end="url(#diagram-arrow)"/>'
                )
                content += text(lx, ly, label, 16, "#526375", width=180, leading=19)
            for i, (label, detail) in enumerate(nodes):
                x, y = positions[i]
                content += f'<rect x="{x}" y="{y}" width="480" height="124" fill="#FFFFFF" stroke="{accent}" stroke-width="2"/>'
                content += text(x + 20, y + 37, label, 26, width=438, leading=32)
                content += text(x + 20, y + 82, detail, 20, "#526375", width=438, leading=26)
            parts.append(group("concept-diagram", "64 212 1152 400", content))
        elif kind == "flow":
            # Numbering carries order without implying a causal dependency between stages.

            for i, body in enumerate(slide["body"]):
                y = 242 + i * 132
                content = (
                    f'<rect x="64" y="{y}" width="46" height="46" fill="{accent}"/>'
                    + text(77, y + 32, str(i + 1), 26, "#FFFFFF")
                    + text(142, y + 31, body, 26, width=1040)
                )
                parts.append(group(f"stage-{i + 1}", f"64 {y} 1152 100", content))
        elif kind == "lab":
            lab = '<rect x="64" y="205" width="1152" height="99" fill="#132C42"/>' + text(
                88, 245, slide["body"][0], 20, "#FFFFFF", "Courier New", width=1090, leading=28
            )
            parts.append(group("lab-command", "64 205 1152 99", lab))
            for i, body in enumerate(slide["body"][1:]):
                parts.append(
                    group(
                        f"lab-task-{i + 1}",
                        f"64 {350 + i * 115} 1100 100",
                        text(64, 385 + i * 115, body, 26, width=1100),
                    )
                )
            parts.append(
                group(
                    "lab-mode",
                    "64 600 1152 30",
                    text(
                        64,
                        622,
                        "PAIR LAB  /  Predict → run → inspect → explain  /  uv run --no-sync",
                        16,
                        accent,
                    ),
                )
            )
        else:
            for i, body in enumerate(slide["body"]):
                y = 235 + i * 120
                bullet = f'<rect x="64" y="{y - 22}" width="5" height="42" fill="{accent}"/>'
                content = bullet + text(92, y, body, 26, ink, width=1090)
                parts.append(group(f"point-{i + 1}", f"64 {y - 28} 1152 105", content))
    source = (
        slide.get("source")
        or "Original workshop adaptation · Educative LLMOps + local NexaAssist code"
    )
    if slide.get("lesson"):
        source = f"Educative L{slide['lesson']:02d} / " + (
            slide.get("source") or "Course concept + NexaAssist adaptation; URL in notes"
        )
    if "Scenario" in slide["note"] or "scenario" in slide["note"]:
        source = "SCENARIO DATA  /  " + source
    footer = text(
        64, 681, source, 16, "#BBCBD7" if dark else "#526375", width=1060, leading=18
    ) + text(
        1150,
        681,
        f"{number:02d}/{len(session['slides'])}",
        16,
        "#BBCBD7" if dark else "#526375",
        width=100,
    )
    parts += [group("footer", "64 655 1152 50", footer), "</svg>"]
    (target / f"svg_output/slide_{number:02d}.svg").write_text("\n".join(parts))
    say(
        f"S{session['number']} P{number:02d} modules: core"
        + (", structure" if kind in ("flow", "diagram") else "")
        + " | "
        + kind
    )


def notes(session: dict[str, Any]) -> None:
    target = folder(session)
    output = []
    for number, slide in enumerate(session["slides"], 1):
        # Final SVG content is the authority for the notes coverage check.
        from xml.etree import ElementTree

        svg = ElementTree.parse(target / f"svg_output/slide_{number:02d}.svg")
        visible = " ".join(svg.getroot().itertext())
        assert slide["title"].split()[0] in visible
        body = " ".join(slide["body"])
        source = slide.get("source")
        narration = f"{body} {slide['note']}"
        if source:
            narration += f" The implementation or concept reference is {source}."
        output.append(f"# {number:02d}_{slide['title']}\n\n{narration}\n")
    (target / "notes/total.md").write_text("\n---\n\n".join(output))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "early", "rest", "notes"])
    args = parser.parse_args()
    for session in SESSIONS:
        if args.action == "prepare":
            prepare(session)
        elif args.action == "notes":
            notes(session)
        else:
            for number in (
                range(1, 6) if args.action == "early" else range(6, len(session["slides"]) + 1)
            ):
                draw(session, number)
    if args.action == "prepare":
        (BASE / "course_manifest.json").write_text(
            json.dumps(SESSIONS, ensure_ascii=False, indent=2)
        )


if __name__ == "__main__":
    main()
