# Session 2: syllabus revision, 24 October 2026

Source-preserving Edit Native PPTX workspace. The original deck is retained at `sources/source.pptx`; edit only `authoring-svg-flat/` and `notes/`. The 16-page roster and order are preserved, so no page_plan.json is needed. All pages receive syllabus attribution and instructor notes; inspected architecture and code objects retain their original native identity.

The user requested syllabus alignment of PPTs 1 and 2 with practical coverage. Content plan: see ../SYLLABUS_ALIGNMENT.md and ../syllabus_alignment.json. Notes are on; narration is off; source transition and animation policies are preserved. No page reordering, repetition or same-deck link changes are planned.

Export with ppt-master svg_quality_checker.py --roundtrip, then svg_to_pptx.py --roundtrip; the native exporter writes to exports/. The earlier *_aligned_20261023/svg_output projects and Python content generator describe the preceding edition and must not overwrite this delivery.
