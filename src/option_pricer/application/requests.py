"""Typed requests crossing the application boundary.

The CLI constructs these directly.  The web bridge constructs them from JSON.
Both therefore enter the same use case and the same validation rules.
"""

from dataclasses import dataclass
from typing import ClassVar

from ..domain.types import OptionType, PricingMethod


@dataclass(frozen=True, slots=True)
class PowerLawRequest:
    """A request for Taleb-style power-law extrapolation."""

    option_type: OptionType
    spot: float
    anchor_strike: float
    target_strike: float
    anchor_price: float
    alpha: float

    method: ClassVar[PricingMethod] = PricingMethod.POWER_LAW


@dataclass(frozen=True, slots=True)
class BlackScholesRequest:
    """A request for a European Black-Scholes-Merton price."""

    option_type: OptionType
    spot: float
    strike: float
    time_to_expiry: float
    rate: float
    volatility: float

    method: ClassVar[PricingMethod] = PricingMethod.BLACK_SCHOLES


type PricingRequest = PowerLawRequest | BlackScholesRequest
