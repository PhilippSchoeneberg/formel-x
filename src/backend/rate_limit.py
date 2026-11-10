"""In-memory sliding-window rate limiting for login and registration.

Good enough for a single app process. With several processes or servers, move the counters to
a shared store (e.g. Redis), because each process would otherwise count on its own.
"""

import math
import time
from collections import deque
from dataclasses import dataclass

from fastapi import HTTPException, Request, status


@dataclass(frozen=True)
class Rule:
    limit: int      # attempts allowed ...
    window: float   # ... within this many seconds


# Failed logins per client IP and per email address; registrations per client IP.
LOGIN_FAILURES_PER_IP = Rule(limit=20, window=15 * 60)
LOGIN_FAILURES_PER_EMAIL = Rule(limit=5, window=15 * 60)
REGISTRATIONS_PER_IP = Rule(limit=5, window=60 * 60)
# Group names work like join codes, so slow down guessing them.
GROUP_LOOKUPS_PER_IP = Rule(limit=30, window=60)

_MAX_KEYS = 50_000


class RateLimiter:
    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self._hits: dict[str, deque] = {}

    def _recent(self, key, rule):
        now = self._clock()
        hits = self._hits.get(key)
        if hits is None:
            return now, None
        while hits and hits[0] <= now - rule.window:
            hits.popleft()
        if not hits:
            del self._hits[key]
            return now, None
        return now, hits

    def retry_after(self, key, rule):
        """Seconds until another attempt is allowed, or 0 if one is allowed now."""
        now, hits = self._recent(key, rule)
        if hits is None or len(hits) < rule.limit:
            return 0
        return max(1, math.ceil(hits[0] + rule.window - now))

    def hit(self, key, rule):
        now, hits = self._recent(key, rule)
        if hits is None:
            if len(self._hits) >= _MAX_KEYS:
                self._hits.clear()  # crude memory cap; only matters under a flood of distinct keys
            hits = self._hits[key] = deque()
        hits.append(now)

    def reset(self, key):
        self._hits.pop(key, None)

    def check(self, *checks):
        """Raises 429 when any (key, rule) pair is over its limit."""
        wait = max((self.retry_after(key, rule) for key, rule in checks), default=0)
        if wait:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "too_many_attempts",
                headers={"Retry-After": str(wait)},
            )


def client_ip(request: Request):
    # Behind a reverse proxy, uvicorn's --proxy-headers puts the real client address here
    # (for proxies listed in FORWARDED_ALLOW_IPS).
    return request.client.host if request.client else "unknown"


def get_rate_limiter(request: Request) -> RateLimiter:
    return request.app.state.rate_limiter
