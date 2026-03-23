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
    Equation 7 (Result 3): Put Pricing
    P(K2) = P(K1) * [numerator] / [denominator]
    
    Note: For real-valued results, alpha must be an integer.
    When alpha is fractional, negative base raised to fractional power produces complex numbers.
    """
    if alpha <= 1:
        raise ValueError("alpha must be greater than 1")
    if not isinstance(alpha, int) and not alpha.is_integer():
        raise ValueError("alpha must be an integer for put pricing to produce real-valued results")
    if k1 >= s0:
        raise ValueError("k1 must be less than s0")
    if k2 >= s0:
        raise ValueError("k2 must be less than s0")
    if p_k1 <= 0:
        raise ValueError("p_k1 must be positive")
    
    # Calculate numerator: (K2 - S0)^(1-α) - S0^(1-α)*((α-1)K2 + S0)
    numerator = (k2 - s0) ** (1 - alpha) - (s0 ** (1 - alpha)) * ((alpha - 1) * k2 + s0)
    
    # Calculate denominator: (K1 - S0)^(1-α) - S0^(1-α)*((α-1)K1 + S0)
    denominator = (k1 - s0) ** (1 - alpha) - (s0 ** (1 - alpha)) * ((alpha - 1) * k1 + s0)
    
    return p_k1 * numerator / denominator


import math

def bsm_call_price(S, K, T, r, sigma):
    """
    Calculate the Black-Scholes-Merton price for a European call option.
    
    Args:
        S: Current underlying price
        K: Strike price
        T: Time to expiration in years
        r: Risk-free interest rate
        sigma: Volatility
    
    Returns:
        Call option price
    """
    if T <= 0 or sigma <= 0:
        return max(0, S - K) if T <= 0 else 0
    
    def norm_cdf(x):
        """Abramowitz and Stegun approximation of cumulative normal distribution."""
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911
        
        sign = 1 if x >= 0 else -1
        x_abs = abs(x) / math.sqrt(2)
        
        t = 1.0 / (1.0 + p * x_abs)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x_abs * x_abs)
        
        return 0.5 * (1.0 + sign * y)
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)


def bsm_put_price(S, K, T, r, sigma):
    """
    Calculate the Black-Scholes-Merton price for a European put option.
    Uses put-call parity: P = C - S + K*exp(-rT)
    
    Args:
        S: Current underlying price
        K: Strike price
        T: Time to expiration in years
        r: Risk-free interest rate
        sigma: Volatility
    
    Returns:
        Put option price
    """
    call_price = bsm_call_price(S, K, T, r, sigma)
    return call_price - S + K * math.exp(-r * T)


def main():
    print("Option Pricing Calculator")
    print("=========================")
    print("1. Call Option Pricing - Power Law (Equation 6)")
    print("2. Put Option Pricing - Power Law (Equation 7)")
    print("3. Black-Scholes-Merton (BSM) Pricing")
    choice = input("\nSelect option type (1, 2, or 3): ").strip()
    
    if choice == "1":
        s0 = float(input("Enter S0 (current underlying price): "))
        k1 = float(input("Enter K1 (anchor strike): "))
        k2 = float(input("Enter K2 (target strike): "))
        c_k1 = float(input("Enter C(K1) (price of call at K1): "))
        alpha = float(input("Enter alpha (tail index, must be > 1): "))
        result = price_call(s0, k1, k2, c_k1, alpha)
        print(f"C(K2) = {result:.6f}")
    elif choice == "2":
        s0 = float(input("Enter S0 (current underlying price): "))
        k1 = float(input("Enter K1 (anchor strike): "))
        k2 = float(input("Enter K2 (target strike): "))
        p_k1 = float(input("Enter P(K1) (price of put at K1): "))
        alpha = float(input("Enter alpha (tail index, must be > 1): "))
        result = price_put(s0, k1, k2, p_k1, alpha)
        print(f"P(K2) = {result:.6f}")
    elif choice == "3":
        print("\nBSM Pricing:")
        option_type = input("Call (c) or Put (p)? ").strip().lower()
        S = float(input("Enter S (current underlying price): "))
        K = float(input("Enter K (strike price): "))
        T = float(input("Enter T (time to expiration in years, e.g., 0.25 for 3 months): "))
        r = float(input("Enter r (risk-free interest rate, e.g., 0.05 for 5%): "))
        sigma = float(input("Enter sigma (volatility, e.g., 0.20 for 20%): "))
        
        if option_type == 'c' or option_type == 'call':
            result = bsm_call_price(S, K, T, r, sigma)
            print(f"BSM Call Price = {result:.6f}")
        elif option_type == 'p' or option_type == 'put':
            result = bsm_put_price(S, K, T, r, sigma)
            print(f"BSM Put Price = {result:.6f}")
        else:
            print("Invalid option type. Please enter 'c' for call or 'p' for put.")
    else:
        print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
