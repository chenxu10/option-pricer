"""Black-Scholes-Merton European option pricing, standard library only.

The normal CDF is evaluated with ``math.erfc`` rather than
``0.5 * (1 + erf(x / sqrt(2)))``.  The erfc form avoids cancellation in the
far tail, which is exactly the region this project cares about.
"""

import math

from .errors import ErrorCode, PricingError
from .types import OptionType
from .validation import ensure_finite_result, require_number, require_positive

_SQRT_TWO = math.sqrt(2.0)


def normal_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""

    return 0.5 * math.erfc(-x / _SQRT_TWO)


def price(
    *,
    option_type: OptionType,
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    volatility: float,
) -> float:
    """Return the Black-Scholes-Merton price of a European option."""

    if not isinstance(option_type, OptionType):
        raise PricingError(
            ErrorCode.UNKNOWN_OPTION_TYPE,
            "option type must be 'call' or 'put'.",
            "option_type",
        )

    spot = require_positive(
        spot,
        field="spot",
        label="spot",
        code=ErrorCode.SPOT_NOT_POSITIVE,
    )
    strike = require_positive(
        strike,
        field="strike",
        label="strike",
        code=ErrorCode.STRIKE_NOT_POSITIVE,
    )
    time_to_expiry = require_positive(
        time_to_expiry,
        field="time_to_expiry",
        label="time to expiry",
        code=ErrorCode.TIME_NOT_POSITIVE,
    )
    rate = require_number(rate, field="rate", label="rate")
    volatility = require_positive(
        volatility,
        field="volatility",
        label="volatility",
        code=ErrorCode.VOLATILITY_NOT_POSITIVE,
    )

    try:
        sqrt_t = math.sqrt(time_to_expiry)
        d1 = (math.log(spot / strike) + (rate + 0.5 * volatility * volatility) * time_to_expiry) / (
            volatility * sqrt_t
        )
        d2 = d1 - volatility * sqrt_t
        discount = math.exp(-rate * time_to_expiry)

        if option_type is OptionType.CALL:
            value = spot * normal_cdf(d1) - strike * discount * normal_cdf(d2)
        else:
            value = strike * discount * normal_cdf(-d2) - spot * normal_cdf(-d1)
    except (OverflowError, ValueError, ZeroDivisionError) as exc:
        raise PricingError(
            ErrorCode.NUMERICAL_OVERFLOW,
            "The calculation failed numerically; check the inputs.",
            "strike",
        ) from exc

    # Deep out-of-the-money prices can suffer a tiny negative cancellation.
    if -1e-12 < value < 0:
        value = 0.0

    return ensure_finite_result(value, field="strike")
