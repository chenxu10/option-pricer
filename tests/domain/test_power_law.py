"""Behaviour of the power-law tail model.

These tests know nothing about the CLI, the web bridge, or JSON.  If the
formula changes, this file should fail; if a presentation layer changes, it
should not.
"""

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from option_pricer.domain.errors import ErrorCode, PricingError
from option_pricer.domain.power_law import call_price, put_price


def test_call_qqq_golden_value() -> None:
    price = call_price(
        spot=581.73,
        anchor_strike=590,
        target_strike=600,
        anchor_price=0.03,
        alpha=2.6,
    )
    assert price == pytest.approx(0.008440115585640976, rel=1e-12)


def test_put_golden_value() -> None:
    price = put_price(
        spot=100,
        anchor_strike=90,
        target_strike=80,
        anchor_price=2.0,
        alpha=3,
    )
    assert price == pytest.approx(0.46090534979423864, rel=1e-12)


def test_put_non_integer_alpha() -> None:
    price = put_price(
        spot=100,
        anchor_strike=90,
        target_strike=80,
        anchor_price=2.0,
        alpha=2.5,
    )
    assert price == pytest.approx(0.613562560852693, rel=1e-12)


def test_call_target_equal_anchor_returns_anchor_price() -> None:
    price = call_price(spot=100, anchor_strike=120, target_strike=120, anchor_price=5.0, alpha=3)
    assert price == pytest.approx(5.0)


def test_put_target_equal_anchor_returns_anchor_price() -> None:
    price = put_price(spot=100, anchor_strike=90, target_strike=90, anchor_price=2.0, alpha=2.5)
    assert price == pytest.approx(2.0)


def test_call_decreases_as_target_moves_further_otm() -> None:
    prices = [
        call_price(spot=100, anchor_strike=120, target_strike=k, anchor_price=5.0, alpha=3)
        for k in (130, 140, 150)
    ]
    assert prices[0] > prices[1] > prices[2] > 0


def test_put_decreases_as_target_moves_further_otm() -> None:
    prices = [
        put_price(spot=100, anchor_strike=90, target_strike=k, anchor_price=2.0, alpha=3)
        for k in (80, 70, 60)
    ]
    assert prices[0] > prices[1] > prices[2] > 0


def test_call_is_homogeneous_in_price_scale() -> None:
    base = call_price(spot=100, anchor_strike=120, target_strike=130, anchor_price=5.0, alpha=3)
    scaled = call_price(spot=200, anchor_strike=240, target_strike=260, anchor_price=10.0, alpha=3)
    assert scaled == pytest.approx(base * 2.0)


def test_put_is_homogeneous_in_price_scale() -> None:
    base = put_price(spot=100, anchor_strike=90, target_strike=80, anchor_price=2.0, alpha=2.5)
    scaled = put_price(spot=200, anchor_strike=180, target_strike=160, anchor_price=4.0, alpha=2.5)
    assert scaled == pytest.approx(base * 2.0)


@pytest.mark.parametrize("alpha", [1.0, 0.5, -3.0])
def test_alpha_must_be_greater_than_one(alpha: float) -> None:
    with pytest.raises(PricingError) as excinfo:
        call_price(spot=100, anchor_strike=120, target_strike=130, anchor_price=5.0, alpha=alpha)
    assert excinfo.value.code is ErrorCode.ALPHA_OUT_OF_RANGE
    assert excinfo.value.field == "alpha"


def test_call_strikes_must_be_above_spot() -> None:
    with pytest.raises(PricingError) as excinfo:
        call_price(spot=100, anchor_strike=100, target_strike=130, anchor_price=5.0, alpha=3)
    assert excinfo.value.code is ErrorCode.STRIKE_DOMAIN
    assert excinfo.value.field == "anchor_strike"

    with pytest.raises(PricingError) as excinfo:
        call_price(spot=100, anchor_strike=120, target_strike=90, anchor_price=5.0, alpha=3)
    assert excinfo.value.code is ErrorCode.STRIKE_DOMAIN
    assert excinfo.value.field == "target_strike"


def test_put_strikes_must_be_below_spot() -> None:
    with pytest.raises(PricingError) as excinfo:
        put_price(spot=100, anchor_strike=100, target_strike=80, anchor_price=2.0, alpha=3)
    assert excinfo.value.code is ErrorCode.STRIKE_DOMAIN
    assert excinfo.value.field == "anchor_strike"

    with pytest.raises(PricingError) as excinfo:
        put_price(spot=100, anchor_strike=90, target_strike=100, anchor_price=2.0, alpha=3)
    assert excinfo.value.code is ErrorCode.STRIKE_DOMAIN
    assert excinfo.value.field == "target_strike"


def test_anchor_price_must_be_positive() -> None:
    for anchor_price in (0.0, -1.0):
        with pytest.raises(PricingError) as excinfo:
            call_price(
                spot=100,
                anchor_strike=120,
                target_strike=130,
                anchor_price=anchor_price,
                alpha=3,
            )
        assert excinfo.value.code is ErrorCode.ANCHOR_PRICE_NOT_POSITIVE
        assert excinfo.value.field == "anchor_price"


def test_spot_must_be_positive() -> None:
    with pytest.raises(PricingError) as excinfo:
        call_price(spot=0, anchor_strike=120, target_strike=130, anchor_price=5.0, alpha=3)
    assert excinfo.value.code is ErrorCode.SPOT_NOT_POSITIVE


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_inputs_are_rejected(bad: float) -> None:
    with pytest.raises(PricingError) as excinfo:
        call_price(spot=bad, anchor_strike=120, target_strike=130, anchor_price=5.0, alpha=3)
    assert excinfo.value.code is ErrorCode.NON_FINITE_INPUT


def test_overflow_is_a_typed_error() -> None:
    with pytest.raises(PricingError) as excinfo:
        call_price(
            spot=100,
            anchor_strike=200,
            target_strike=150,
            anchor_price=1.0,
            alpha=1e9,
        )
    assert excinfo.value.code is ErrorCode.NUMERICAL_OVERFLOW


@st.composite
def call_scenarios(draw: st.DrawFn) -> tuple[float, float, float, float, float]:
    spot = draw(st.floats(min_value=10, max_value=1000, allow_nan=False))
    anchor = spot + draw(st.floats(min_value=0.1, max_value=500, allow_nan=False))
    target = spot + draw(st.floats(min_value=0.1, max_value=500, allow_nan=False))
    price = draw(st.floats(min_value=0.001, max_value=100, allow_nan=False))
    alpha = draw(st.floats(min_value=1.01, max_value=10, allow_nan=False))
    return spot, anchor, target, price, alpha


@given(call_scenarios())
@settings(max_examples=50, deadline=None)
def test_call_is_positive_and_finite_for_valid_inputs(
    scenario: tuple[float, float, float, float, float],
) -> None:
    spot, anchor, target, price, alpha = scenario
    result = call_price(
        spot=spot,
        anchor_strike=anchor,
        target_strike=target,
        anchor_price=price,
        alpha=alpha,
    )
    assert math.isfinite(result)
    assert result >= 0


@st.composite
def put_scenarios(draw: st.DrawFn) -> tuple[float, float, float, float, float]:
    spot = draw(st.floats(min_value=10, max_value=1000, allow_nan=False))
    anchor = spot - draw(st.floats(min_value=0.1, max_value=spot * 0.8, allow_nan=False))
    target = spot - draw(st.floats(min_value=0.1, max_value=spot * 0.9, allow_nan=False))
    price = draw(st.floats(min_value=0.001, max_value=100, allow_nan=False))
    alpha = draw(st.floats(min_value=1.01, max_value=10, allow_nan=False))
    return spot, anchor, target, price, alpha


@given(put_scenarios())
@settings(max_examples=50, deadline=None)
def test_put_is_positive_and_finite_for_valid_inputs(
    scenario: tuple[float, float, float, float, float],
) -> None:
    spot, anchor, target, price, alpha = scenario
    result = put_price(
        spot=spot,
        anchor_strike=anchor,
        target_strike=target,
        anchor_price=price,
        alpha=alpha,
    )
    assert math.isfinite(result)
    assert result >= 0
