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
# Put Pricing Tests - Equation 7 (Result 3) in Return Space
# ============================================================================

def test_put_pricing_basic():
    """
    Test 1: Basic put pricing test
    
    Equation 7 in return space:
    P(K2) = P(K1) * [α - r2^(1-α) - (α-1)r2] / [α - r1^(1-α) - (α-1)r1]
    where r = (S0 - K) / S0
    
    This formula works for any real α > 1, not just integers.
    """
    result = price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=3)
    # This should calculate the put price for K2=80 given K1=90 with P(K1)=2.0
    assert result > 0


def test_put_pricing_non_integer_alpha():
    """
    Test 2: Put pricing with non-integer alpha should work correctly
    The corrected formula works for any real alpha > 1
    """
    result = price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=2.5)
    assert result > 0
    
    # Also test with alpha = 2.75 (common tail index)
    result2 = price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=2.75)
    assert result2 > 0


def test_put_k2_equals_k1_returns_p_k1():
    """Test 3: When K2 == K1, P(K2) should equal P(K1)"""
    result = price_put(s0=100, k1=90, k2=90, p_k1=2.0, alpha=3)
    assert result == pytest.approx(2.0)


def test_put_k2_equals_k1_non_integer_alpha():
    """Test 4: When K2 == K1 with non-integer alpha, P(K2) should equal P(K1)"""
    result = price_put(s0=100, k1=90, k2=90, p_k1=2.0, alpha=2.5)
    assert result == pytest.approx(2.0)


def test_put_alpha_must_be_greater_than_one():
    """Test 5: alpha must be greater than 1"""
    with pytest.raises(ValueError, match="alpha must be greater than 1"):
        price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=1)
    with pytest.raises(ValueError, match="alpha must be greater than 1"):
        price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=0.5)


def test_put_strikes_must_be_less_than_s0():
    """Test 6: For puts, K1 and K2 must be less than S0"""
    with pytest.raises(ValueError, match="k1 must be less than s0"):
        price_put(s0=100, k1=100, k2=80, p_k1=2.0, alpha=3)
    with pytest.raises(ValueError, match="k2 must be less than s0"):
        price_put(s0=100, k1=90, k2=100, p_k1=2.0, alpha=3)


def test_put_p_k1_must_be_positive():
    """Test 7: p_k1 must be positive"""
    with pytest.raises(ValueError, match="p_k1 must be positive"):
        price_put(s0=100, k1=90, k2=80, p_k1=0, alpha=3)
    with pytest.raises(ValueError, match="p_k1 must be positive"):
        price_put(s0=100, k1=90, k2=80, p_k1=-1, alpha=3)


def test_put_deeper_otm_lower_price():
    """Test 8: For puts, as K2 decreases (further OTM), price should decrease"""
    p_at_80 = price_put(s0=100, k1=90, k2=80, p_k1=2.0, alpha=3)
    p_at_70 = price_put(s0=100, k1=90, k2=70, p_k1=2.0, alpha=3)
    p_at_60 = price_put(s0=100, k1=90, k2=60, p_k1=2.0, alpha=3)
    assert p_at_80 > p_at_70 > p_at_60 > 0


def test_put_calculation_accuracy():
    """Test 9: Verify the calculation matches the formula in return space"""
    s0, k1, k2, p_k1, alpha = 100, 90, 80, 2.0, 3
    
    # Manual calculation according to corrected formula in return space
    # P(K2) = P(K1) * [α - r2^(1-α) - (α-1)*r2] / [α - r1^(1-α) - (α-1)*r1]
    r1 = (s0 - k1) / s0  # (100-90)/100 = 0.1
    r2 = (s0 - k2) / s0  # (100-80)/100 = 0.2
    
    numerator = alpha - r2 ** (1 - alpha) - (alpha - 1) * r2
    denominator = alpha - r1 ** (1 - alpha) - (alpha - 1) * r1
    expected = p_k1 * numerator / denominator
    
    result = price_put(s0=s0, k1=k1, k2=k2, p_k1=p_k1, alpha=alpha)
    assert result == pytest.approx(expected)


def test_put_calculation_accuracy_non_integer_alpha():
    """Test 10: Verify calculation with non-integer alpha"""
    s0, k1, k2, p_k1, alpha = 100, 90, 80, 2.0, 2.5
    
    # Manual calculation according to corrected formula in return space
    # P(K2) = P(K1) * [α - r2^(1-α) - (α-1)*r2] / [α - r1^(1-α) - (α-1)*r1]
    r1 = (s0 - k1) / s0  # 0.1
    r2 = (s0 - k2) / s0  # 0.2
    
    numerator = alpha - r2 ** (1 - alpha) - (alpha - 1) * r2
    denominator = alpha - r1 ** (1 - alpha) - (alpha - 1) * r1
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


def test_put_cli_non_integer_alpha(monkeypatch, capsys):
    """
    Test CLI interface for put option pricing with non-integer alpha.
    """
    from src.option_pricer import main as cli_main
    # Simulate user typing: choice=2 (put), s0=100, k1=90, k2=80, p_k1=2.0, alpha=2.5
    inputs = iter(["2", "100", "90", "80", "2.0", "2.5"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    cli_main()
    captured = capsys.readouterr()
    assert "P(K2) =" in captured.out
