"""Taleb-style power-law extrapolation of out-of-the-money option prices.

Equation 6 of Taleb et al. (2019), "Tail option pricing under power laws":

    C(K2) = C(K1) * ((K2 - S0) / (K1 - S0)) ** (1 - alpha)

For puts the formula is applied in return space, r = (S0 - K) / S0, so that
r > 0 for out-of-the-money puts:

    P(K2) = P(K1) * (alpha - r2**(1-alpha) - (alpha-1)*r2)
                   / (alpha - r1**(1-alpha) - (alpha-1)*r1)

The functions below are pure: no I/O, no JSON, no presentation concerns.
"""

from .errors import ErrorCode, PricingError
from .validation import ensure_finite_result, require_number, require_positive


def call_price(
    *,
    spot: float,
    anchor_strike: float,
    target_strike: float,
    anchor_price: float,
    alpha: float,
) -> float:
    """Price a call at ``target_strike`` from the anchor call at ``anchor_strike``."""

    spot = require_positive(
        spot,
        field="spot",
        label="spot",
        code=ErrorCode.SPOT_NOT_POSITIVE,
    )
    anchor_strike = require_number(
        anchor_strike,
        field="anchor_strike",
        label="anchor strike",
    )
    target_strike = require_number(
        target_strike,
        field="target_strike",
        label="target strike",
    )
    anchor_price = require_positive(
        anchor_price,
        field="anchor_price",
        label="anchor price",
        code=ErrorCode.ANCHOR_PRICE_NOT_POSITIVE,
    )
    alpha = _validate_alpha(alpha)

    if anchor_strike <= spot:
        raise PricingError(
            ErrorCode.STRIKE_DOMAIN,
            "K1 must be greater than S0 for calls.",
            "anchor_strike",
        )
    if target_strike <= spot:
        raise PricingError(
            ErrorCode.STRIKE_DOMAIN,
            "K2 must be greater than S0 for calls.",
            "target_strike",
        )

    try:
        ratio = (target_strike - spot) / (anchor_strike - spot)
        price = ratio ** (1.0 - alpha) * anchor_price
    except (OverflowError, ZeroDivisionError) as exc:
        raise PricingError(
            ErrorCode.NUMERICAL_OVERFLOW,
            "The calculation overflowed; check alpha and the strikes.",
            "alpha",
        ) from exc

    return ensure_finite_result(price, field="target_strike")


def put_price(
    *,
    spot: float,
    anchor_strike: float,
    target_strike: float,
    anchor_price: float,
    alpha: float,
) -> float:
    """Price a put at ``target_strike`` from the anchor put at ``anchor_strike``."""

    spot = require_positive(
        spot,
        field="spot",
        label="spot",
        code=ErrorCode.SPOT_NOT_POSITIVE,
    )
    anchor_strike = require_number(
        anchor_strike,
        field="anchor_strike",
        label="anchor strike",
    )
    target_strike = require_number(
        target_strike,
        field="target_strike",
        label="target strike",
    )
    anchor_price = require_positive(
        anchor_price,
        field="anchor_price",
        label="anchor price",
        code=ErrorCode.ANCHOR_PRICE_NOT_POSITIVE,
    )
    alpha = _validate_alpha(alpha)

    if anchor_strike >= spot:
        raise PricingError(
            ErrorCode.STRIKE_DOMAIN,
            "K1 must be less than S0 for puts.",
            "anchor_strike",
        )
    if target_strike >= spot:
        raise PricingError(
            ErrorCode.STRIKE_DOMAIN,
            "K2 must be less than S0 for puts.",
            "target_strike",
        )

    r1 = (spot - anchor_strike) / spot
    r2 = (spot - target_strike) / spot

    try:
        numerator = alpha - r2 ** (1.0 - alpha) - (alpha - 1.0) * r2
        denominator = alpha - r1 ** (1.0 - alpha) - (alpha - 1.0) * r1
    except (OverflowError, ZeroDivisionError) as exc:
        raise PricingError(
            ErrorCode.NUMERICAL_OVERFLOW,
            "The calculation overflowed; check alpha and the strikes.",
            "alpha",
        ) from exc

    if abs(denominator) < 1e-15:
        raise PricingError(
            ErrorCode.NUMERICAL_SINGULARITY,
            "The denominator is too close to zero; adjust the anchor strike.",
            "anchor_strike",
        )

    price = anchor_price * numerator / denominator
    return ensure_finite_result(price, field="target_strike")


def _validate_alpha(alpha: float) -> float:
    value = require_number(alpha, field="alpha", label="alpha")
    if value <= 1.0:
        raise PricingError(
            ErrorCode.ALPHA_OUT_OF_RANGE,
            "alpha must be greater than 1.",
            "alpha",
        )
    return value
