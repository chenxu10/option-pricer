"""
Core Option Pricing Logic Tests - Call Options

These tests verify the mathematical pricing calculations for call options.
They are completely decoupled from any presentation layer (CLI, GUI, Web).

If the pricing formula changes, these tests should fail.
If the presentation changes, these tests should still pass.
"""
import pytest
from src.option_pricer import price_call


def test_basic_formula():
    """
    Equation 6: C(K2) = ((K2 - S0) / (K1 - S0))^(1 - alpha) * C(K1)
    S0=100, K1=120, K2=130, C_K1=5.0, alpha=3
    Expected: (30/20)^(1-3) * 5 = 1.5^(-2) * 5 = 5/2.25 = 2.2222...

    Use trading day of 03/20/2026 to price relatively QQQ otm call 
    on right tail
    """
    result = price_call(s0=581.73, k1=590, k2=600, c_k1=0.03, alpha=2.6)
    assert result == pytest.approx(0.00844, rel=1e-3)


def test_k2_equals_k1_returns_c_k1():
    # When K2 == K1, the ratio is 1, so C(K2) == C(K1)
    result = price_call(s0=100, k1=120, k2=120, c_k1=5.0, alpha=3)
    assert result == pytest.approx(5.0)


def test_alpha_must_be_greater_than_one():
    with pytest.raises(ValueError, match="alpha must be greater than 1"):
        price_call(s0=100, k1=120, k2=130, c_k1=5.0, alpha=1)
    with pytest.raises(ValueError, match="alpha must be greater than 1"):
        price_call(s0=100, k1=120, k2=130, c_k1=5.0, alpha=0.5)


def test_strikes_must_be_greater_than_s0():
    with pytest.raises(ValueError, match="k1 must be greater than s0"):
        price_call(s0=100, k1=100, k2=130, c_k1=5.0, alpha=3)
    with pytest.raises(ValueError, match="k2 must be greater than s0"):
        price_call(s0=100, k1=120, k2=90, c_k1=5.0, alpha=3)


def test_c_k1_must_be_positive():
    with pytest.raises(ValueError, match="c_k1 must be positive"):
        price_call(s0=100, k1=120, k2=130, c_k1=0, alpha=3)
    with pytest.raises(ValueError, match="c_k1 must be positive"):
        price_call(s0=100, k1=120, k2=130, c_k1=-1, alpha=3)


def test_higher_strike_means_lower_call_price():
    # For calls, as K2 increases (further OTM), the price should decrease
    c_at_130 = price_call(s0=100, k1=120, k2=130, c_k1=5.0, alpha=3)
    c_at_140 = price_call(s0=100, k1=120, k2=140, c_k1=5.0, alpha=3)
    c_at_150 = price_call(s0=100, k1=120, k2=150, c_k1=5.0, alpha=3)
    assert c_at_130 > c_at_140 > c_at_150 > 0


# ============================================================================
# CLI Integration Tests - Call Options
# ============================================================================

def test_cli_end_to_end(monkeypatch, capsys):
    """
    Test CLI interface produces expected output for call options.
    This tests the CLI presentation layer, not just calculation.
    """
    from src.option_pricer import main as cli_main
    # Simulate user typing: choice=1 (call), s0=100, k1=120, k2=130, c_k1=5.0, alpha=3
    inputs = iter(["1", "100", "120", "130", "5.0", "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    cli_main()
    captured = capsys.readouterr()
    # CLI outputs: "C(K2) = 2.222222"
    assert "2.2222" in captured.out


def test_main_cli_entry_point(monkeypatch, capsys):
    """
    Test main.py entry point provides CLI functionality for call options.
    """
    import importlib
    import main
    importlib.reload(main)  # Reload to ensure fresh import
    # Simulate user typing: choice=1 (call), s0=100, k1=120, k2=130, c_k1=5.0, alpha=3
    inputs = iter(["1", "100", "120", "130", "5.0", "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    main.main()
    captured = capsys.readouterr()
    assert "2.2222" in captured.out


# ============================================================================
# Calculation Accuracy Tests - Coupled to Pricing Formula
# ============================================================================

class TestCalculationAccuracy:
    """
    These tests are coupled to the pricing formula.
    If the formula changes, these tests must be updated.
    """
    
    def test_calculation_matches_expected_formula(self):
        """
        Verify calculation matches: ((K2 - S0) / (K1 - S0))^(1 - alpha) * C(K1)
        """
        s0, k1, k2, c_k1, alpha = 100, 120, 130, 5.0, 3
        
        expected = ((k2 - s0) / (k1 - s0)) ** (1 - alpha) * c_k1
        result = price_call(s0=s0, k1=k1, k2=k2, c_k1=c_k1, alpha=alpha)
        
        assert result == pytest.approx(expected)
    
    def test_specific_known_values(self):
        """
        Test with known values to catch formula changes.
        These are specific test cases with expected outputs.
        """
        # Test case 1
        result1 = price_call(s0=100, k1=120, k2=130, c_k1=5.0, alpha=3)
        assert result1 == pytest.approx(2.222222, rel=1e-5)
        
        # Test case 2
        result2 = price_call(s0=581.73, k1=590, k2=600, c_k1=0.03, alpha=2.6)
        assert result2 == pytest.approx(0.00844, rel=1e-3)
        
        # Test case 3: k2 == k1 should return c_k1
        result3 = price_call(s0=100, k1=120, k2=120, c_k1=5.0, alpha=3)
        assert result3 == pytest.approx(5.0)


# ============================================================================
# Power Law vs Black-Scholes Comparison Tests
# ============================================================================

def test_power_law_exceeds_bsm_for_far_otm_calls():
    """
    Test that power law heuristic prices far OTM calls higher than BSM.
    
    Rationale: BSM assumes normal distribution (thin tails), while power law 
    accounts for fat tails (Pareto distribution). For far OTM strikes, 
    the probability of extreme moves is much higher under power law,
    resulting in higher option prices that better reflect tail risk.
    
    This test verifies Taleb's critique that BSM underprices deep OTM options
    by ignoring fat-tail effects.
    """
    import math
    
    def black_scholes_call(S, K, T, r, sigma):
        """
        Simple Black-Scholes formula for European call option.
        Uses scipy-like cumulative normal distribution approximation.
        """
        def norm_cdf(x):
            """Approximation of the cumulative normal distribution function."""
            # Abramowitz and Stegun approximation (error < 7.5e-8)
            a1 = 0.254829592
            a2 = -0.284496736
            a3 = 1.421413741
            a4 = -1.453152027
            a5 = 1.061405429
            p = 0.3275911
            
            sign = 1 if x >= 0 else -1
            x = abs(x) / math.sqrt(2)
            
            t = 1.0 / (1.0 + p * x)
            y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
            
            return 0.5 * (1.0 + sign * y)
        
        if T <= 0 or sigma <= 0:
            return max(0, S - K) if T <= 0 else 0
        
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        call_price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
        return call_price
    
    # Market parameters
    s0 = 100.0  # Current underlying price
    k1 = 120.0  # Anchor strike (near ATM)
    c_k1 = 5.0  # Market price at K1 (used as anchor)
    k2 = 150.0  # Far OTM strike (30% OTM, deep tail)
    alpha = 2.5  # Tail index indicating fat tails
    
    # Power law price for far OTM call
    power_law_price = price_call(s0=s0, k1=k1, k2=k2, c_k1=c_k1, alpha=alpha)
    
    # BSM parameters (implied from anchor price or assumed)
    t = 0.25  # 3 months to expiration
    r = 0.05  # 5% risk-free rate
    sigma = 0.20  # 20% volatility (typical equity volatility)
    
    # BSM price for the same far OTM call
    bsm_price = black_scholes_call(s0, k2, t, r, sigma)

    # Power law should significantly exceed BSM for far OTM
    # This demonstrates the impact of fat tails vs normal distribution
    assert power_law_price > bsm_price, (
        f"Power law price ({power_law_price:.6f}) should exceed BSM price ({bsm_price:.6f}) "
        f"for far OTM calls. Ratio: {power_law_price/bsm_price:.1f}x"
    )


def test_bsm_cli_end_to_end(monkeypatch, capsys):
    """
    Test CLI interface for BSM option pricing.
    """
    from src.option_pricer import main as cli_main
    # Simulate user typing: choice=3 (BSM), c (call), S=100, K=100, T=0.25, r=0.05, sigma=0.20
    inputs = iter(["3", "c", "100", "100", "0.25", "0.05", "0.20"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    cli_main()
    captured = capsys.readouterr()
    # Should output BSM Call Price
    assert "BSM Call Price" in captured.out
    # Price should be around 4.61 for ATM call with these params
    assert "4." in captured.out or "5." in captured.out
