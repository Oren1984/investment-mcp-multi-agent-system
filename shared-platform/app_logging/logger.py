import logging
import os

from app_logging.formatters import get_standard_formatter
from config.settings import Settings


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger configured to the level defined in Settings.

    Root handler setup is idempotent — safe to call multiple times.
    """
    settings = Settings()
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level.upper())
    _ensure_root_configured(settings)
    return logger


def _ensure_root_configured(settings: Settings) -> None:
    """Configure the root logger once. Subsequent calls are no-ops."""
    root = logging.getLogger()
    if root.handlers:
        return

    formatter = get_standard_formatter()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    log_dir = os.path.dirname(settings.log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    file_handler = logging.FileHandler(settings.log_file)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    root.setLevel(settings.log_level.upper())
