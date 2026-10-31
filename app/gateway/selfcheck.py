"""Exercise real LiteLLM routing and cache code with offline mock responses only."""

from __future__ import annotations

import asyncio
import random

from fastapi import HTTPException
from litellm import Router
from litellm.caching.caching import Cache
from litellm.proxy.db.exception_handler import PrismaDBExceptionHandler


async def main() -> None:
    # A missing optional DB dependency previously crashed the proxy's 401 error handler.
    assert not PrismaDBExceptionHandler.is_database_infrastructure_error(HTTPException(401))
    random.seed(0)
    router = Router(
        model_list=[
            {
                "model_name": "pool" if name != "backup" else "backup",
                "litellm_params": {
                    "model": f"openai/offline-{name}",
                    "api_key": "offline-not-a-key",
                    "mock_response": f"fixture-{name}",
                },
                "model_info": {"id": name},
            }
            for name in ("replica-a", "replica-b", "backup")
        ],
        routing_strategy="simple-shuffle",
        num_retries=0,
        max_fallbacks=1,
        timeout=1,
        fallbacks=[{"pool": ["backup"]}],
    )
    messages = [{"role": "user", "content": "Offline routing fixture"}]
    try:
        observed = set()
        for _ in range(20):
            response = await router.acompletion(model="pool", messages=messages)
            observed.add(response._hidden_params["model_id"])
        assert observed == {"replica-a", "replica-b"}
        response = await router.acompletion(
            model="pool", messages=messages, mock_testing_fallbacks=True
        )
        assert response._hidden_params["model_id"] == "backup"

        cache = Cache(type="local", default_in_memory_ttl=300)
        arguments = {"model": "pool", "messages": messages, "metadata": {"redis_namespace": "a"}}
        cache.add_cache({"answer": "offline fixture"}, **arguments)
        assert cache.get_cache(**arguments) == {"answer": "offline fixture"}
        assert cache.get_cache(**{**arguments, "metadata": {"redis_namespace": "b"}}) is None
        assert (
            cache.get_cache(
                **{**arguments, "messages": [{"role": "user", "content": "Changed evidence"}]}
            )
            is None
        )
    finally:
        router.reset()


if __name__ == "__main__":
    asyncio.run(main())
