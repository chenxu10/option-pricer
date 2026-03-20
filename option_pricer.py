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


def main():
    s0 = float(input("Enter S0 (current underlying price): "))
    k1 = float(input("Enter K1 (anchor strike): "))
    k2 = float(input("Enter K2 (target strike): "))
    c_k1 = float(input("Enter C(K1) (price of call at K1): "))
    alpha = float(input("Enter alpha (tail index, must be > 1): "))
    result = price_call(s0, k1, k2, c_k1, alpha)
    print(f"C(K2) = {result:.6f}")


if __name__ == "__main__":
    main()
