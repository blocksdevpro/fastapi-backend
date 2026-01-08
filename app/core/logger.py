import json
import logging
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

request_id_ctx = ContextVar("request_id", default="")


class RequestIDFilter(logging.Filter):
    """Adds request_id from context to log records."""

    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        record.request_id = request_id_ctx.get() or "-"
        return super().filter(record)


class JsonFormatter(logging.Formatter):
    """Formats log records as JSON with standard fields."""

    RESERVED_ATTRS = {
        "name",
        "msg",
        "args",
        "created",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "thread",
        "threadName",
        "taskName",
        "exc_info",
        "exc_text",
        "stack_info",
        "request_id",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "level": record.levelname,
            "logger": record.name,
            "timestamp": self.formatTime(record, self.datefmt),
            "request_id": getattr(record, "request_id", "-"),
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key not in self.RESERVED_ATTRS:
                log_data[key] = value

        return json.dumps(log_data, default=str)


def configure_logging(
    level: int = logging.INFO,
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True,
) -> None:
    """
    Configure application logging with JSON formatting.

    Args:
        level: Logging level (default: INFO)
        log_dir: Directory for log files (default: "logs")
        max_bytes: Max size per log file in bytes (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        enable_console: Enable console logging (default: True)
        enable_file: Enable file logging (default: True)
    """
    # Initialize formatter
    formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S")
    request_filter = RequestIDFilter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # Console handler
    if enable_console:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.addFilter(request_filter)
        root_logger.addHandler(stream_handler)

    # File handler
    if enable_file:
        logs_path = Path(log_dir)
        logs_path.mkdir(exist_ok=True, parents=True)

        file_handler = RotatingFileHandler(
            logs_path / "app.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(request_filter)
        root_logger.addHandler(file_handler)
