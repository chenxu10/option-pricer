"""Typed domain errors.

The model never returns error strings and never prints.  It raises a
``PricingError`` carrying a stable machine-readable code, an optional field
name, and a neutral English message.  Adapters decide how to present it.
"""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable error identifiers used by both the CLI and the JSON contract."""

    INVALID_REQUEST = "INVALID_REQUEST"
    UNSUPPORTED_VERSION = "UNSUPPORTED_VERSION"
    UNKNOWN_METHOD = "UNKNOWN_METHOD"
    UNKNOWN_OPTION_TYPE = "UNKNOWN_OPTION_TYPE"
    INVALID_NUMBER = "INVALID_NUMBER"
    NON_FINITE_INPUT = "NON_FINITE_INPUT"
    SPOT_NOT_POSITIVE = "SPOT_NOT_POSITIVE"
    STRIKE_NOT_POSITIVE = "STRIKE_NOT_POSITIVE"
    ANCHOR_PRICE_NOT_POSITIVE = "ANCHOR_PRICE_NOT_POSITIVE"
    ALPHA_OUT_OF_RANGE = "ALPHA_OUT_OF_RANGE"
    STRIKE_DOMAIN = "STRIKE_DOMAIN"
    TIME_NOT_POSITIVE = "TIME_NOT_POSITIVE"
    VOLATILITY_NOT_POSITIVE = "VOLATILITY_NOT_POSITIVE"
    NUMERICAL_SINGULARITY = "NUMERICAL_SINGULARITY"
    NUMERICAL_OVERFLOW = "NUMERICAL_OVERFLOW"
    NUMERICAL_ERROR = "NUMERICAL_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class PricingError(Exception):
    """A failure that can be explained to a caller without a traceback."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        field: str | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.field = field
        super().__init__(message)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"PricingError(code={self.code!r}, field={self.field!r}, message={self.message!r})"
