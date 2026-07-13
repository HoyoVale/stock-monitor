"""Structured logging configuration using stdlib + JSON format.

Supports LOG_LEVEL and LOG_FILE env vars. Logs are written as
single-line JSON objects for easy ingestion by log aggregators.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "")  # e.g. logs/app.log
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # "json" or "text"


class JSONFormatter(logging.Formatter):
    """Emit log records as JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        entry: dict[str, Any] = {
            "timestamp": ts,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            entry["exception"] = self.formatException(record.exc_info)
        # Include any extra fields attached to the record
        for key in ("elapsed_ms", "status_code", "method", "path", "datasource"):
            val = getattr(record, key, None)
            if val is not None:
                entry[key] = val
        return json.dumps(entry, ensure_ascii=False)


def configure_logging() -> None:
    """Configure root logger with JSON or text formatter."""
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    # Remove existing handlers to avoid duplicates on reload
    root.handlers.clear()

    handler: logging.Handler
    if LOG_FILE:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(
            LOG_FILE, when="midnight", interval=1, backupCount=30, encoding="utf-8"
        )
    else:
        handler = logging.StreamHandler(sys.stdout)

    if LOG_FORMAT == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
        )
    root.addHandler(handler)

    # Quiet noisy third-party loggers
    for noisy in ("aiosqlite", "httpx", "httpcore", "apscheduler"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
