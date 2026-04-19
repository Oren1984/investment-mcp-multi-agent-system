from config.loader import load_settings
from app_logging.logger import get_logger


def main():
    settings = load_settings()
    logger = get_logger(__name__)

    logger.info("Starting shared platform")
    logger.info("Environment: %s", settings.app_env)
    logger.info("Debug mode: %s", settings.debug)

    print("Shared platform initialized successfully")


if __name__ == "__main__":
    main()