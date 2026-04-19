from config.settings import Settings


def load_settings() -> Settings:
    """
    Load and return platform settings.
    Central entry point for configuration access.
    """
    return Settings()