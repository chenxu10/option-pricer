"""Numeric validation helpers shared by the domain functions.

They are intentionally small and standard-library only.  Keeping validation
here means every adapter gets the same rules, in one place.
"""

import math

from .errors import ErrorCode, PricingError


def require_number(value: object, *, field: str, label: str) -> float:
    """Return ``value`` as a finite float or raise a typed domain error."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PricingError(
            ErrorCode.INVALID_NUMBER,
            f"{label} must be a number.",
            field,
        )
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:  # pragma: no cover - defensive
        raise PricingError(
            ErrorCode.INVALID_NUMBER,
            f"{label} must be a number.",
            field,
        ) from exc
    if not math.isfinite(number):
        raise PricingError(
            ErrorCode.NON_FINITE_INPUT,
            f"{label} must be finite.",
            field,
        )
    return number


def require_positive(
    value: object,
    *,
    field: str,
    label: str,
    code: ErrorCode,
) -> float:
    """Return a strictly positive finite float or raise a typed error."""

    number = require_number(value, field=field, label=label)
    if number <= 0:
        raise PricingError(code, f"{label} must be positive.", field)
    return number


def ensure_finite_result(value: float, *, field: str) -> float:
    """Reject non-finite or negative computed prices."""

    if not math.isfinite(value):
        raise PricingError(
            ErrorCode.NUMERICAL_OVERFLOW,
            "The calculation produced a non-finite result; check the inputs.",
            field,
        )
    if value < 0:
        raise PricingError(
            ErrorCode.NUMERICAL_ERROR,
            "The calculation produced a negative price; check the inputs.",
            field,
        )
    # Normalise negative zero, which is valid JSON but confusing in output.
    return 0.0 if value == 0 else float(value)
