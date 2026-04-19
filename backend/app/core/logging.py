import logging
import sys
from contextvars import ContextVar
from typing import Any
import json
from datetime import datetime, timezone

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
run_id_var: ContextVar[str] = ContextVar("run_id", default="")


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(""),
            "run_id": run_id_var.get(""),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        for key in ("ticker", "agent_name", "tool_name", "duration_ms", "status"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO", fmt: str = "json") -> None:
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    if fmt == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    root.handlers = [handler]


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
