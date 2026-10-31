from __future__ import annotations

import math
from collections.abc import Awaitable, Callable
from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, Request

from app.core.config import Settings, get_settings
from app.core.rate_limit import SlidingWindowLimiter

logger = structlog.get_logger()
_limiters: dict[tuple[str, int], SlidingWindowLimiter] = {}


def reset_limiters() -> None:
    _limiters.clear()


def limit_requests(group: str) -> Callable[..., Awaitable[None]]:
    """Dependency: at most RATE_LIMIT_PER_MINUTE requests per client address per group.

    The client is the direct peer address. Behind a reverse proxy every caller shares the
    proxy's address, so limit at the proxy as well (forwarded headers are not trusted here).
    """

    async def dependency(
        request: Request, settings: Annotated[Settings, Depends(get_settings)]
    ) -> None:
        if settings.rate_limit_per_minute == 0:
            return
        limiter = _limiters.setdefault(
            (group, settings.rate_limit_per_minute),
            SlidingWindowLimiter(settings.rate_limit_per_minute, 60),
        )
        retry_after = limiter.check(request.client.host if request.client else "unknown")
        if retry_after is not None:
            logger.warning("rate_limited", group=group)
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(max(1, math.ceil(retry_after)))},
            )

    return dependency
