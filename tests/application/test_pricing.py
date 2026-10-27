"""Application-layer dispatch tests."""

import pytest

from option_pricer.application.pricing import price_option
from option_pricer.application.requests import BlackScholesRequest, PowerLawRequest
from option_pricer.domain.errors import ErrorCode, PricingError
from option_pricer.domain.types import OptionType, PricingMethod


def test_power_law_call_dispatch() -> None:
    result = price_option(
        PowerLawRequest(
            option_type=OptionType.CALL,
            spot=581.73,
            anchor_strike=590,
            target_strike=600,
            anchor_price=0.03,
            alpha=2.6,
        )
    )
    assert result.method is PricingMethod.POWER_LAW
    assert result.option_type is OptionType.CALL
    assert result.price == pytest.approx(0.008440115585640976, rel=1e-12)


def test_power_law_put_dispatch() -> None:
    result = price_option(
        PowerLawRequest(
            option_type=OptionType.PUT,
            spot=100,
            anchor_strike=90,
            target_strike=80,
            anchor_price=2.0,
            alpha=3,
        )
    )
    assert result.method is PricingMethod.POWER_LAW
    assert result.option_type is OptionType.PUT
    assert result.price == pytest.approx(0.46090534979423864, rel=1e-12)


def test_black_scholes_dispatch() -> None:
    result = price_option(
        BlackScholesRequest(
            option_type=OptionType.CALL,
            spot=100,
            strike=100,
            time_to_expiry=0.25,
            rate=0.05,
            volatility=0.2,
        )
    )
    assert result.method is PricingMethod.BLACK_SCHOLES
    assert result.option_type is OptionType.CALL
    assert result.price == pytest.approx(4.614997129602855, rel=1e-12)


def test_domain_errors_propagate_unchanged() -> None:
    with pytest.raises(PricingError) as excinfo:
        price_option(
            PowerLawRequest(
                option_type=OptionType.CALL,
                spot=100,
                anchor_strike=90,
                target_strike=130,
                anchor_price=5.0,
                alpha=3,
            )
        )
    assert excinfo.value.code is ErrorCode.STRIKE_DOMAIN
    assert excinfo.value.field == "anchor_strike"


def test_invalid_option_type_is_rejected_at_the_seam() -> None:
    with pytest.raises(PricingError) as excinfo:
        price_option(
            PowerLawRequest(
                option_type="call",  # type: ignore[arg-type]
                spot=100,
                anchor_strike=120,
                target_strike=130,
                anchor_price=5.0,
                alpha=3,
            )
        )
    assert excinfo.value.code is ErrorCode.UNKNOWN_OPTION_TYPE


def test_unknown_request_type_is_a_programming_error() -> None:
    with pytest.raises(TypeError):
        price_option("not a request")  # type: ignore[arg-type]
