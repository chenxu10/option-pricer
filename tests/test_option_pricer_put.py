"""
Core Option Pricing Logic Tests - Put Options

These tests verify the mathematical pricing calculations for put options.
They are completely decoupled from any presentation layer (CLI, GUI, Web).

If the pricing formula changes, these tests should fail.
If the presentation changes, these tests should still pass.
"""
import pytest
from src.option_pricer import price_put


# ============================================================================
# Put Pricing Tests - Equation 7 (Result 3)
# ============================================================================

def test_put_pricing_basic():
    """
    Test 1: Basic put pricing test
    Equation 7: P(K2) = P(K1) * [numerator] / [denominator]
    where numerator = (K2-S0)^(1-α) - S0^(1-α)*((α-1)K2 + S0)
    and denominator = (K1-S0)^(1-α) - S0^(1-α)*((α-1)K1 + S0)
    
    Note: alpha must be integer for real-valued results (non-integer alpha produces complex numbers)
    """
    result = price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=3)
    # This should calculate the put price for K2=80 given K1=90 with P(K1)=2.0
    assert result > 0.08


def test_put_k2_equals_k1_returns_p_k1():
    """Test 2: When K2 == K1, P(K2) should equal P(K1)"""
    result = price_put(s0=100, k1=90, k2=90, p_k1=2.0, alpha=3)
    assert result == pytest.approx(2.0)


def test_put_alpha_must_be_greater_than_one():
    """Test 3: alpha must be greater than 1"""
    with pytest.raises(ValueError, match="alpha must be greater than 1"):
        price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=1)
    with pytest.raises(ValueError, match="alpha must be greater than 1"):
        price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=0.5)


def test_put_strikes_must_be_less_than_s0():
    """Test 4: For puts, K1 and K2 must be less than S0"""
    with pytest.raises(ValueError, match="k1 must be less than s0"):
        price_put(s0=100, k1=100, k2=80, p_k1=2.0, alpha=3)
    with pytest.raises(ValueError, match="k2 must be less than s0"):
        price_put(s0=100, k1=90, k2=100, p_k1=2.0, alpha=3)


def test_put_p_k1_must_be_positive():
    """Test 5: p_k1 must be positive"""
    with pytest.raises(ValueError, match="p_k1 must be positive"):
        price_put(s0=100, k1=90, k2=80, p_k1=0, alpha=3)
    with pytest.raises(ValueError, match="p_k1 must be positive"):
        price_put(s0=100, k1=90, k2=80, p_k1=-1, alpha=3)


def test_put_deeper_otm_lower_price():
    """Test 6: For puts, as K2 decreases (further OTM), price should decrease"""
    p_at_80 = price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=3)
    p_at_70 = price_put(s0=100, k1=90, k2=70, p_k1=2.0, alpha=3)
    p_at_60 = price_put(s0=100, k1=90, k2=60, p_k1=2.0, alpha=3)
    assert p_at_80 > p_at_70 > p_at_60 > 0


def test_put_calculation_accuracy():
    """Test 7: Verify the calculation matches the formula exactly"""
    s0, k1, k2, p_k1, alpha = 100, 90, 80, 2.0, 3
    
    # Manual calculation according to Equation 7
    numerator = (k2 - s0) ** (1 - alpha) - (s0 ** (1 - alpha)) * ((alpha - 1) * k2 + s0)
    denominator = (k1 - s0) ** (1 - alpha) - (s0 ** (1 - alpha)) * ((alpha - 1) * k1 + s0)
    expected = p_k1 * numerator / denominator
    
    result = price_put(s0=s0, k1=k1, k2=k2, p_k1=p_k1, alpha=alpha)
    assert result == pytest.approx(expected)


# ============================================================================
# CLI Integration Tests - Put Options
# ============================================================================

def test_put_cli_end_to_end(monkeypatch, capsys):
    """
    Test CLI interface for put option pricing.
    """
    from src.option_pricer import main as cli_main
    # Simulate user typing: choice=2 (put), s0=100, k1=90, k2=80, p_k1=2.0, alpha=3
    inputs = iter(["2", "100", "90", "80", "2.0", "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    cli_main()
    captured = capsys.readouterr()
    assert "P(K2) =" in captured.out
