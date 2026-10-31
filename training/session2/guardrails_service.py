"""Compatibility entry point; implementation lives in app.security."""

from app.security.guardrails_service import app, main

__all__ = ["app", "main"]

if __name__ == "__main__":
    main()
