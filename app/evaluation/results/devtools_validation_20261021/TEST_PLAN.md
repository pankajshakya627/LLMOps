# Application validation plan — 21 October 2026

Run the existing Python and mock-API suites, Ruff, and Mypy. Use Chrome DevTools MCP in a temporary profile against localhost. Preserve source code and configuration. Use synthetic policy questions and clearly marked synthetic feedback only.

1. Inspect the welcome accessibility tree, console, network requests, screenshot, and a local performance trace.
2. Test keyboard focus and empty input without generating a model request.
3. Submit an Evidence-mode query, expand its source, and confirm RAGAS controls are disabled.
4. Submit an Answer-mode question with evaluation enabled; confirm one answer, citations, an evaluation link, and hidden score cards.
5. Save synthetic feedback and explicitly select/recheck the rejected review decision before saving. Confirm database readback and prevent overwriting a completed review. Clean up only records created by this run.
6. Check a separate browser context, a populated mobile view, and browser reconnect after a temporary network outage affecting only the test page.
7. Exercise API validation boundaries and independently reproduce the known fee problem.
8. Report passed, failed, and unverified items separately. Prior live-case evidence is labelled as prior evidence, never counted as newly rerun.

Limits: no real-person study, actual customer data, persistent infrastructure changes, production deployment, personal Chrome profile, or destructive corpus operations.
