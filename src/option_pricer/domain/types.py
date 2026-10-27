"""Small value types shared by the pricing domain."""

from enum import StrEnum


class OptionType(StrEnum):
    """The two option flavours understood by the model."""

    CALL = "call"
    PUT = "put"


class PricingMethod(StrEnum):
    """The pricing approaches exposed by the application layer."""

    POWER_LAW = "power_law"
    BLACK_SCHOLES = "black_scholes"
