"""The application use case: one request in, one result out."""

from dataclasses import dataclass

from ..domain import black_scholes, power_law
from ..domain.errors import ErrorCode, PricingError
from ..domain.types import OptionType, PricingMethod
from .requests import BlackScholesRequest, PowerLawRequest, PricingRequest


@dataclass(frozen=True, slots=True)
class PricingResult:
    """A priced option plus the metadata a presentation layer needs."""

    price: float
    method: PricingMethod
    option_type: OptionType


def price_option(request: PricingRequest) -> PricingResult:
    """Dispatch a typed request to the model and wrap the result.

    This is deliberately thin.  It contains no formulas and no presentation
    logic; its only job is to route between the model and the adapters.
    """

    if not isinstance(request, (PowerLawRequest, BlackScholesRequest)):
        raise TypeError(f"unsupported request type: {type(request)!r}")

    if not isinstance(request.option_type, OptionType):
        raise PricingError(
            ErrorCode.UNKNOWN_OPTION_TYPE,
            "option type must be 'call' or 'put'.",
            "option_type",
        )

    if isinstance(request, PowerLawRequest):
        if request.option_type is OptionType.CALL:
            price = power_law.call_price(
                spot=request.spot,
                anchor_strike=request.anchor_strike,
                target_strike=request.target_strike,
                anchor_price=request.anchor_price,
                alpha=request.alpha,
            )
        else:
            price = power_law.put_price(
                spot=request.spot,
                anchor_strike=request.anchor_strike,
                target_strike=request.target_strike,
                anchor_price=request.anchor_price,
                alpha=request.alpha,
            )
    elif isinstance(request, BlackScholesRequest):
        price = black_scholes.price(
            option_type=request.option_type,
            spot=request.spot,
            strike=request.strike,
            time_to_expiry=request.time_to_expiry,
            rate=request.rate,
            volatility=request.volatility,
        )
    else:  # pragma: no cover - type checkers protect this path
        raise TypeError(f"unsupported request type: {type(request)!r}")

    return PricingResult(
        price=price,
        method=request.method,
        option_type=request.option_type,
    )
