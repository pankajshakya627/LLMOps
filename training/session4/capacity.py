"""Scenario arithmetic, not live prices or a complete GPU sizing recommendation."""

from __future__ import annotations

from training.console import say


def main() -> None:
    parameters_billion = 8
    for label, bytes_per_parameter in [("FP16", 2), ("INT8", 1), ("INT4", 0.5)]:
        weight_gb = parameters_billion * bytes_per_parameter
        say(f"{label}: weight-only decimal GB={weight_gb:g}")
    queries = 1000
    daily_cost = queries * (500 * 0.10 + 200 * 0.50) / 1_000_000
    assert abs(daily_cost - 0.15) < 1e-9
    assert abs(daily_cost * 30 - 4.50) < 1e-9
    say(f"Scenario cost: daily=${daily_cost:.2f}, 30 days=${daily_cost * 30:.2f}")
    say("Missing capacity inputs: KV cache, runtime overhead, context length, concurrency.")
    say("Prices and traffic are invented scenario inputs; no current quote is asserted.")


if __name__ == "__main__":
    main()
