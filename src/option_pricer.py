def price_call(s0, k1, k2, c_k1, alpha):
    if alpha <= 1:
        raise ValueError("alpha must be greater than 1")
    if k1 <= s0:
        raise ValueError("k1 must be greater than s0")
    if k2 <= s0:
        raise ValueError("k2 must be greater than s0")
    if c_k1 <= 0:
        raise ValueError("c_k1 must be positive")
    return ((k2 - s0) / (k1 - s0)) ** (1 - alpha) * c_k1


def price_put(s0, k1, k2, p_k1, alpha):
    """
    Calculate put option price at strike K2 using power law formula (Equation 7).
    
    The formula is derived for returns r = (S0 - K) / S0, not absolute strikes.
    We transform to return space where r > 0 for OTM puts (K < S0).
    
    Formula in return space:
    P(K2) = P(K1) * [r2^(1-α) - (α-1)*r2 + 1] / [r1^(1-α) - (α-1)*r1 + 1]
    where r = (S0 - K) / S0
    
    Args:
        s0: Current underlying price
        k1: Anchor strike price (must be < s0)
        k2: Target strike price (must be < s0)
        p_k1: Price of put option at K1
        alpha: Tail index (must be > 1, any real number)
    
    Returns:
        Put option price at K2
    """
    if alpha <= 1:
        raise ValueError("alpha must be greater than 1")
    if k1 >= s0:
        raise ValueError("k1 must be less than s0")
    if k2 >= s0:
        raise ValueError("k2 must be less than s0")
    if p_k1 <= 0:
        raise ValueError("p_k1 must be positive")
    
    # Transform strikes to returns: r = (S0 - K) / S0
    # This gives positive returns for OTM puts (K < S0)
    r1 = (s0 - k1) / s0  # return at K1
    r2 = (s0 - k2) / s0  # return at K2
    
    # Apply the power law formula in return space
    # P(K2) = P(K1) * [r2^(1-α) - (α-1)*r2 + 1] / [r1^(1-α) - (α-1)*r1 + 1]
    numerator = r2 ** (1 - alpha) - (alpha - 1) * r2 + 1
    denominator = r1 ** (1 - alpha) - (alpha - 1) * r1 + 1
    
    if abs(denominator) < 1e-15:
        raise ValueError("Invalid parameters: denominator is too close to zero")
    
    return p_k1 * numerator / denominator


import math
from py_vollib.ref_python.black_scholes_merton import black_scholes_merton

def bsm_call_price(S, K, T, r, sigma):
    """
    Calculate the Black-Scholes-Merton price for a European call option using py_vollib.
    
    Args:
        S: Current underlying price
        K: Strike price
        T: Time to expiration in years
        r: Risk-free interest rate
        sigma: Volatility
    
    Returns:
        Call option price
    """
    return black_scholes_merton('c', S, K, T, r, sigma, 0.0)


def bsm_put_price(S, K, T, r, sigma):
    """
    Calculate the Black-Scholes-Merton price for a European put option using py_vollib.
    
    Args:
        S: Current underlying price
        K: Strike price
        T: Time to expiration in years
        r: Risk-free interest rate
        sigma: Volatility
    
    Returns:
        Put option price
    """
    return black_scholes_merton('p', S, K, T, r, sigma, 0.0)


def _display_menu():
    """Display the main menu options."""
    print("Option Pricing Calculator")
    print("=========================")
    print("1. Call Option Pricing - Power Law (Equation 6)")
    print("2. Put Option Pricing - Power Law (Equation 7)")
    print("3. Black-Scholes-Merton (BSM) Pricing")


def _get_float_input(prompt: str) -> float:
    """Get a float input from the user with the given prompt."""
    return float(input(prompt))


def _handle_call_option():
    """Handle call option pricing input and calculation."""
    s0 = _get_float_input("Enter S0 (current underlying price): ")
    k1 = _get_float_input("Enter K1 (anchor strike): ")
    k2 = _get_float_input("Enter K2 (target strike): ")
    c_k1 = _get_float_input("Enter C(K1) (price of call at K1): ")
    alpha = _get_float_input("Enter alpha (tail index, must be > 1): ")
    result = price_call(s0, k1, k2, c_k1, alpha)
    print(f"C(K2) = {result:.6f}")


def _handle_put_option():
    """Handle put option pricing input and calculation."""
    s0 = _get_float_input("Enter S0 (current underlying price): ")
    k1 = _get_float_input("Enter K1 (anchor strike): ")
    k2 = _get_float_input("Enter K2 (target strike): ")
    p_k1 = _get_float_input("Enter P(K1) (price of put at K1): ")
    alpha = _get_float_input("Enter alpha (tail index, must be > 1): ")
    result = price_put(s0, k1, k2, p_k1, alpha)
    print(f"P(K2) = {result:.6f}")


def _handle_bsm_pricing():
    """Handle BSM option pricing input and calculation."""
    print("\nBSM Pricing:")
    option_type = input("Call (c) or Put (p)? ").strip().lower()
    S = _get_float_input("Enter S (current underlying price): ")
    K = _get_float_input("Enter K (strike price): ")
    T = _get_float_input("Enter T (time to expiration in years, e.g., 0.25 for 3 months): ")
    r = _get_float_input("Enter r (risk-free interest rate, e.g., 0.05 for 5%): ")
    sigma = _get_float_input("Enter sigma (volatility, e.g., 0.20 for 20%): ")
    
    if option_type in ('c', 'call'):
        result = bsm_call_price(S, K, T, r, sigma)
        print(f"BSM Call Price = {result:.6f}")
    elif option_type in ('p', 'put'):
        result = bsm_put_price(S, K, T, r, sigma)
        print(f"BSM Put Price = {result:.6f}")
    else:
        print("Invalid option type. Please enter 'c' for call or 'p' for put.")


def main():
    """Main entry point for the option pricing calculator."""
    _display_menu()
    choice = input("\nSelect option type (1, 2, or 3): ").strip()
    
    handlers = {
        '1': _handle_call_option,
        '2': _handle_put_option,
        '3': _handle_bsm_pricing,
    }
    
    handler = handlers.get(choice)
    if handler:
        handler()
    else:
        print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
