from errors.base import ConfigurationError


class MissingEnvironmentVariableError(ConfigurationError):
    """Raised when a required environment variable is missing."""


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration values are invalid."""