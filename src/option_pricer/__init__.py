"""Option pricer: a pure pricing model with CLI and browser adapters."""

from .application.pricing import PricingResult, price_option
from .application.requests import BlackScholesRequest, PowerLawRequest, PricingRequest
from .domain.errors import ErrorCode, PricingError
from .domain.types import OptionType, PricingMethod
from .version import __version__

__all__ = [
    "BlackScholesRequest",
    "ErrorCode",
    "OptionType",
    "PowerLawRequest",
    "PricingError",
    "PricingMethod",
    "PricingRequest",
    "PricingResult",
    "__version__",
    "price_option",
]
