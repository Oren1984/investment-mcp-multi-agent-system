from errors.base import ValidationError


class InvalidPayloadError(ValidationError):
    """Raised when input payload validation fails."""


class InvalidSchemaError(ValidationError):
    """Raised when schema validation fails."""