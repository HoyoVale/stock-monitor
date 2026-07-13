"""Request logging middleware — logs every HTTP request with timing."""

import time
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("stock_monitor.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request duration, status, method, and path for every request."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000  # ms

        logger.info(
            "%s %s → %d  %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "elapsed_ms": round(elapsed, 1),
            },
        )
        return response
