"""A fixture-only memory/rewrite design exercise; no durable session service is added."""

from __future__ import annotations

from training.console import say


def main() -> None:
    history = [
        {"role": "user", "content": "What is the NexaHome processing fee?"},
        {"role": "assistant", "content": "The fee depends on sanction date."},
        {"role": "user", "content": "Does that fee apply before July?"},
    ]
    recent = history[-2:]
    assert len(recent) == 2
    assert history[0] not in recent
    original = history[-1]["content"]
    failed_rewrite: str | None = None
    search_query = failed_rewrite or original
    assert search_query == original
    say("bounded fixture: 2 messages; earlier product scope can be lost")
    say("rewrite failure: original query retained; ambiguity still requires handling")
    say("Design before implementing: authorize session, persist turns, budget tokens, evaluate.")
    say("Simulation only: no memory, query rewriter or database was added to the API.")


if __name__ == "__main__":
    main()
