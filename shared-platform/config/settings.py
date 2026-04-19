import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "shared-platform")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = _to_bool(os.getenv("DEBUG"), default=True)

    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "standard")
    log_file: str = os.getenv("LOG_FILE", "logs/app.log")

    config_source: str = os.getenv("CONFIG_SOURCE", "env")

    retry_attempts: int = _to_int(os.getenv("RETRY_ATTEMPTS"), 3)
    retry_delay: int = _to_int(os.getenv("RETRY_DELAY"), 1)

    api_timeout: int = _to_int(os.getenv("API_TIMEOUT"), 10)

    enable_validation: bool = _to_bool(os.getenv("ENABLE_VALIDATION"), default=True)
    enable_retry: bool = _to_bool(os.getenv("ENABLE_RETRY"), default=True)