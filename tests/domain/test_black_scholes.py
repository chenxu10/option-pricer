"""Black-Scholes-Merton model tests, independent of any adapter."""

import math

import pytest

from option_pricer.domain.black_scholes import normal_cdf, price
from option_pricer.domain.errors import ErrorCode, PricingError
from option_pricer.domain.types import OptionType


def test_atm_call_golden_value() -> None:
    result = price(
        option_type=OptionType.CALL,
        spot=100,
        strike=100,
        time_to_expiry=0.25,
        rate=0.05,
        volatility=0.2,
    )
    assert result == pytest.approx(4.614997129602855, rel=1e-12)


def test_atm_put_golden_value() -> None:
    result = price(
        option_type=OptionType.PUT,
        spot=100,
        strike=100,
        time_to_expiry=0.25,
        rate=0.05,
        volatility=0.2,
    )
    assert result == pytest.approx(3.372777178991008, rel=1e-12)


def test_put_call_parity() -> None:
    call = price(
        option_type=OptionType.CALL,
        spot=100,
        strike=110,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.25,
    )
    put = price(
        option_type=OptionType.PUT,
        spot=100,
        strike=110,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.25,
    )
    assert call - put == pytest.approx(100 - 110 * math.exp(-0.03 * 0.5), rel=1e-12)


def test_deep_otm_call_is_positive() -> None:
    result = price(
        option_type=OptionType.CALL,
        spot=100,
        strike=200,
        time_to_expiry=0.25,
        rate=0.05,
        volatility=0.2,
    )
    assert result > 0
    assert math.isfinite(result)


def test_call_bounds() -> None:
    call = price(
        option_type=OptionType.CALL,
        spot=100,
        strike=90,
        time_to_expiry=1.0,
        rate=0.05,
        volatility=0.2,
    )
    assert 0 < call <= 100


def test_put_bounds() -> None:
    put = price(
        option_type=OptionType.PUT,
        spot=100,
        strike=90,
        time_to_expiry=1.0,
        rate=0.05,
        volatility=0.2,
    )
    assert 0 < put <= 90 * math.exp(-0.05)


def test_call_increases_with_spot_and_decreases_with_strike() -> None:
    low_spot = price(
        option_type=OptionType.CALL,
        spot=90,
        strike=100,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.2,
    )
    high_spot = price(
        option_type=OptionType.CALL,
        spot=110,
        strike=100,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.2,
    )
    low_strike = price(
        option_type=OptionType.CALL,
        spot=100,
        strike=90,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.2,
    )
    high_strike = price(
        option_type=OptionType.CALL,
        spot=100,
        strike=110,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.2,
    )
    assert high_spot > low_spot
    assert low_strike > high_strike


def test_put_increases_with_strike_and_decreases_with_spot() -> None:
    low_spot = price(
        option_type=OptionType.PUT,
        spot=90,
        strike=100,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.2,
    )
    high_spot = price(
        option_type=OptionType.PUT,
        spot=110,
        strike=100,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.2,
    )
    low_strike = price(
        option_type=OptionType.PUT,
        spot=100,
        strike=90,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.2,
    )
    high_strike = price(
        option_type=OptionType.PUT,
        spot=100,
        strike=110,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.2,
    )
    assert low_spot > high_spot
    assert high_strike > low_strike


def test_call_increases_with_volatility() -> None:
    low_vol = price(
        option_type=OptionType.CALL,
        spot=100,
        strike=100,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.1,
    )
    high_vol = price(
        option_type=OptionType.CALL,
        spot=100,
        strike=100,
        time_to_expiry=0.5,
        rate=0.03,
        volatility=0.4,
    )
    assert high_vol > low_vol


def test_normal_cdf_properties() -> None:
    assert normal_cdf(0) == pytest.approx(0.5)
    assert normal_cdf(1.96) == pytest.approx(0.9750021048517795)
    assert normal_cdf(-1.0) + normal_cdf(1.0) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("field", "kwargs", "code"),
    [
        ("spot", {"spot": 0}, ErrorCode.SPOT_NOT_POSITIVE),
        ("strike", {"strike": 0}, ErrorCode.STRIKE_NOT_POSITIVE),
        ("time_to_expiry", {"time_to_expiry": 0}, ErrorCode.TIME_NOT_POSITIVE),
        ("volatility", {"volatility": 0}, ErrorCode.VOLATILITY_NOT_POSITIVE),
    ],
)
def test_positive_inputs_are_required(field: str, kwargs: dict[str, float], code: ErrorCode) -> None:
    base = {
        "option_type": OptionType.CALL,
        "spot": 100.0,
        "strike": 100.0,
        "time_to_expiry": 0.5,
        "rate": 0.03,
        "volatility": 0.2,
    }
    base.update(kwargs)
    with pytest.raises(PricingError) as excinfo:
        price(**base)
    assert excinfo.value.code is code
    assert excinfo.value.field == field


def test_non_finite_spot_is_rejected() -> None:
    with pytest.raises(PricingError) as excinfo:
        price(
            option_type=OptionType.CALL,
            spot=float("nan"),
            strike=100,
            time_to_expiry=0.5,
            rate=0.03,
            volatility=0.2,
        )
    assert excinfo.value.code is ErrorCode.NON_FINITE_INPUT


def test_invalid_option_type_is_rejected() -> None:
    with pytest.raises(PricingError) as excinfo:
        price(
            option_type="call",  # type: ignore[arg-type]
            spot=100,
            strike=100,
            time_to_expiry=0.5,
            rate=0.03,
            volatility=0.2,
        )
    assert excinfo.value.code is ErrorCode.UNKNOWN_OPTION_TYPE


def test_negative_rate_is_allowed() -> None:
    call = price(
        option_type=OptionType.CALL,
        spot=100,
        strike=100,
        time_to_expiry=0.5,
        rate=-0.01,
        volatility=0.2,
    )
    put = price(
        option_type=OptionType.PUT,
        spot=100,
        strike=100,
        time_to_expiry=0.5,
        rate=-0.01,
        volatility=0.2,
    )
    assert call > 0
    assert put > 0
    assert call - put == pytest.approx(100 - 100 * math.exp(0.01 * 0.5), rel=1e-12)
