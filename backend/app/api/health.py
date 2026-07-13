"""Health & system status API — exposes structured health info."""

import logging
import os
import platform
import time

from fastapi import APIRouter

from app.datasource_stats import stats

router = APIRouter(prefix="/api", tags=["health"])

_start_time = time.time()
logger = logging.getLogger("stock_monitor.health")


@router.get("/health")
async def health_check():
    """Basic health check for Docker / orchestration."""
    return {"status": "ok", "service": "stock-monitor-backend"}


@router.get("/health/detailed")
async def detailed_health():
    """Detailed system health with datasource stats and uptime."""
    uptime_sec = int(time.time() - _start_time)
    return {
        "status": "ok",
        "version": "0.3.0",
        "uptime_seconds": uptime_sec,
        "python_version": platform.python_version(),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "datasources": stats.snapshot(),
    }


@router.post("/health/reset-stats")
async def reset_datasource_stats():
    """Reset datasource call statistics."""
    stats.reset()
    return {"ok": True, "message": "Datasource stats reset"}
