"""
Simple in-memory rate limiter middleware
Limits requests per IP per minute
"""

import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# { ip: [timestamp, ...] }
_request_log: dict = defaultdict(list)

RATE_LIMIT = 60        # max requests
WINDOW_SECONDS = 60    # per minute


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Purge old entries
        _request_log[ip] = [t for t in _request_log[ip] if now - t < WINDOW_SECONDS]

        if len(_request_log[ip]) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={
                    "error": True,
                    "status_code": 429,
                    "message": f"Rate limit exceeded. Max {RATE_LIMIT} requests per minute.",
                },
            )

        _request_log[ip].append(now)
        response = await call_next(request)
        return response
