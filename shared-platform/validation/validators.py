from errors.validation_errors import InvalidPayloadError


def require_non_empty_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidPayloadError(f"{field_name} must be a non-empty string")
    return value.strip()


def require_positive_int(value: int, field_name: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise InvalidPayloadError(f"{field_name} must be a positive integer")
    return value