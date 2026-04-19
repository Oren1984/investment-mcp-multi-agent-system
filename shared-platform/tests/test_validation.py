import pytest

from errors.validation_errors import InvalidPayloadError
from validation.validators import require_non_empty_string, require_positive_int


def test_require_non_empty_string_accepts_valid_input():
    assert require_non_empty_string(" hello ", "name") == "hello"


def test_require_non_empty_string_rejects_empty_input():
    with pytest.raises(InvalidPayloadError):
        require_non_empty_string("   ", "name")


def test_require_positive_int_accepts_valid_input():
    assert require_positive_int(3, "count") == 3


def test_require_positive_int_rejects_invalid_input():
    with pytest.raises(InvalidPayloadError):
        require_positive_int(0, "count")