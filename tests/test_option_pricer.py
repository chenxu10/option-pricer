import pytest
from src.option_pricer import price_call


def test_basic_formula():
    # Equation 6: C(K2) = ((K2 - S0) / (K1 - S0))^(1 - alpha) * C(K1)
    # S0=100, K1=120, K2=130, C_K1=5.0, alpha=3
    # Expected: (30/20)^(1-3) * 5 = 1.5^(-2) * 5 = 5/2.25 = 2.2222...
    result = price_call(s0=100, k1=120, k2=130, c_k1=5.0, alpha=3)
    assert result == pytest.approx(2.2222222222, rel=1e-6)


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


def test_cli_end_to_end(monkeypatch, capsys):
    from src.option_pricer import main
    # Simulate user typing: s0=100, k1=120, k2=130, c_k1=5.0, alpha=3
    inputs = iter(["100", "120", "130", "5.0", "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    main()
    captured = capsys.readouterr()
    assert "2.2222" in captured.out
