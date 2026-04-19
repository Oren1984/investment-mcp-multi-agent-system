from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_name: str = "investment-mcp-system"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql://invest_user:invest_pass@localhost:5432/investment_db"
    database_url_async: str = "postgresql+asyncpg://invest_user:invest_pass@localhost:5432/investment_db"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # LLM
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # External data APIs
    news_api_key: str = ""
    alpha_vantage_key: str = ""

    # Analysis defaults
    default_analysis_period: str = "1y"
    max_concurrent_runs: int = 5
    crew_verbose: bool = False

    # Demo mode — set DEMO_MODE=true to skip real LLM calls and return synthetic reports.
    # Auto-activates when ANTHROPIC_API_KEY is missing or still the placeholder value.
    # Set to false and supply a real ANTHROPIC_API_KEY to run live analysis.
    demo_mode: bool = False

    # Authentication — set API_KEY to a non-empty value to enable header auth
    # Leave empty to disable auth (suitable for local dev only)
    api_key: str = ""

    # Rate limiting (requests per minute per IP on POST /analyze)
    rate_limit_analyze: str = "10/minute"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
