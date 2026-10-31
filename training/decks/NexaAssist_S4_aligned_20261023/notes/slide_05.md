python -m training.showcase --session 4 Provider failures then quota: [503, 503, 429]. Invalid input: 422; failed readiness: 503. Allow 20 minutes. Predict which requests consume quota. The driver deadline is covered separately and is not a hard wall-clock guarantee. Limits are per process/client; this is not a distributed quota.

Code walkthrough: app/database/mongo.py
def ping_database(settings: Settings) -> None:
    """Bound the readiness probe without shortening normal query deadlines."""
    with timeout(2):
        _database(settings).command("ping")

Status, retry behavior and response privacy. Measure latency and cost under representative traffic. Offline failures establish no capacity target. Retain an HTTP transcript. Explain health versus readiness and unknown versus passing measurements. Prices and SLO targets remain placeholders pending owner confirmation.