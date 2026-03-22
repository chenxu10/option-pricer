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
    """
    if alpha <= 1:
        raise ValueError("alpha must be greater than 1")
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


def main():
    print("Option Pricing - Power Law Tail Model")
    print("=====================================")
    print("1. Call Option Pricing (Equation 6)")
    print("2. Put Option Pricing (Equation 7)")
    choice = input("\nSelect option type (1 or 2): ").strip()
    
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
    else:
        print("Invalid choice. Please select 1 or 2.")


if __name__ == "__main__":
    main()
