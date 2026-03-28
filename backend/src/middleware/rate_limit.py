"""Simple in-memory rate limiting middleware.

Tracks request counts per IP address with a sliding window. Applies
stricter limits to write endpoints (POST/PATCH/DELETE) than read
endpoints (GET). Returns 429 Too Many Requests when limits are exceeded.

For production with multiple instances, replace the in-memory store
with Redis using the same interface.
"""

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Rate limit configuration (requests per window)
# Read endpoints: 100 requests per 60 seconds per IP
READ_LIMIT = 100
# Write endpoints: 20 requests per 60 seconds per IP
WRITE_LIMIT = 20
# Window size in seconds
WINDOW_SECONDS = 60

# Endpoints exempt from rate limiting
_EXEMPT_PATHS = {"/api/health", "/api/webhooks/github"}

# Methods considered "write" operations
_WRITE_METHODS = {"POST", "PATCH", "PUT", "DELETE"}


class _RateLimitStore:
    """In-memory sliding window rate limiter.

    Tracks timestamps of recent requests per key (IP + method class).
    Evicts expired entries on each check to prevent memory growth.

    Attributes:
        _requests: Maps rate limit keys to lists of request timestamps.
    """

    def __init__(self) -> None:
        """Initialize an empty rate limit store."""
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if a request is allowed under the rate limit.

        Evicts timestamps older than the window, then checks if the
        count is under the limit. If allowed, records the new request.

        Args:
            key: Unique identifier for the rate limit bucket.
            limit: Maximum number of requests allowed in the window.
            window: Window size in seconds.

        Returns:
            True if the request is allowed, False if rate limited.
        """
        now = time.monotonic()
        cutoff = now - window

        # Evict expired timestamps
        timestamps = self._requests[key]
        self._requests[key] = [t for t in timestamps if t > cutoff]

        if len(self._requests[key]) >= limit:
            return False

        self._requests[key].append(now)
        return True


# Module-level store instance (shared across requests)
_store = _RateLimitStore()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that enforces per-IP rate limits.

    Applies different limits based on HTTP method (read vs. write).
    Exempt paths like health checks and webhooks are not rate limited.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Check rate limits before passing the request to the handler.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            The response from the handler, or a 429 if rate limited.
        """
        path = request.url.path

        # Skip rate limiting for exempt paths
        if path in _EXEMPT_PATHS:
            return await call_next(request)

        # Determine client IP (respects X-Forwarded-For for reverse proxies)
        client_ip = request.headers.get(
            "X-Forwarded-For", request.client.host if request.client else "unknown"
        ).split(",")[0].strip()

        method = request.method.upper()
        is_write = method in _WRITE_METHODS

        # Build rate limit key: IP + method class
        key = f"{client_ip}:{'write' if is_write else 'read'}"
        limit = WRITE_LIMIT if is_write else READ_LIMIT

        if not _store.is_allowed(key, limit, WINDOW_SECONDS):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(WINDOW_SECONDS)},
            )

        return await call_next(request)
