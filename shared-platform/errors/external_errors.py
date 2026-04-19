from errors.base import ExternalServiceError


class ServiceUnavailableError(ExternalServiceError):
    """Raised when an external service is unavailable."""


class TimeoutServiceError(ExternalServiceError):
    """Raised when an external service times out."""