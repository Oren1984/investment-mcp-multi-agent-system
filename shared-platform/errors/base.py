class SharedPlatformError(Exception):
    """Base exception for all shared platform errors."""


class ConfigurationError(SharedPlatformError):
    """Raised when configuration is invalid or missing."""


class ValidationError(SharedPlatformError):
    """Raised when validation fails."""


class ExternalServiceError(SharedPlatformError):
    """Raised when an external dependency fails."""