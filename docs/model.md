# Model notes

The model is deliberately small and dependency-free. It answers one question:
given an observed out-of-the-money option price at an anchor strike, what
should a further strike cost if the tail decays like a power law?

## Inputs

| Name | Wire field | Constraint |
|---|---|---|
| Spot | `spot` | finite, `> 0` |
| Anchor strike | `anchor_strike` | finite; calls `> spot`, puts `< spot` |
| Target strike | `target_strike` | finite; calls `> spot`, puts `< spot` |
| Anchor price | `anchor_price` | finite, `> 0` |
| Tail index | `alpha` | finite, `> 1` |
| Strike (BSM) | `strike` | finite, `> 0` |
| Time to expiry | `time_to_expiry` | finite, `> 0` (years) |
| Rate | `rate` | finite; may be negative |
| Volatility | `volatility` | finite, `> 0` |

The anchor price is an observed input, not a model output. Calls and puts use
different domains because the anchor must be out of the money: calls above
spot, puts below spot.

## Power-law calls

Equation 6 of Taleb et al. (2019):

```text
C(K2) = C(K1) * ((K2 - S0) / (K1 - S0)) ** (1 - alpha)
```

`K1` and `K2` must be greater than `S0`. `K2 == K1` returns `C(K1)`; `K2 > K1`
gives a lower price for `alpha > 1`.

## Power-law puts

The put formula is applied in return space:

```text
r = (S0 - K) / S0
```

For out-of-the-money puts (`K < S0`), `r > 0`. Substituting `K = S0(1 - r)`
into the tail relationship gives:

```text
P(K2) = P(K1) * [alpha - r2^(1-alpha) - (alpha-1)*r2]
                / [alpha - r1^(1-alpha) - (alpha-1)*r1]
```

The denominator is checked against a small absolute tolerance (`1e-15`) and a
`NUMERICAL_SINGULARITY` error is raised if it collapses.

## Black-Scholes-Merton

```text
d1 = (ln(S/K) + (r + sigma^2 / 2) * T) / (sigma * sqrt(T))
d2 = d1 - sigma * sqrt(T)

C = S * N(d1) - K * exp(-rT) * N(d2)
P = K * exp(-rT) * N(-d2) - S * N(-d1)
```

The normal CDF is implemented as:

```python
0.5 * math.erfc(-x / math.sqrt(2.0))
```

Using `erfc` directly avoids the cancellation in `0.5 * (1 + erf(...))` for
large negative `x`, which matters for deep out-of-the-money options. No
dividend yield is modelled (`q = 0`). European exercise only.

## Numerical policy

- All inputs are converted to finite floats before calculation.
- Non-finite inputs raise `NON_FINITE_INPUT`; they never reach the formulas.
- Overflow and division failures are translated to typed errors.
- A computed price must be finite and non-negative. A BSM value within
  `1e-12` of zero is clamped to zero to absorb cancellation noise.
- Results are serialized with `json.dumps(..., allow_nan=False)`.

## Error taxonomy

| Code | Meaning |
|---|---|
| `INVALID_REQUEST` | Malformed JSON, missing/extra field, duplicate key |
| `UNSUPPORTED_VERSION` | Contract version is not `v1` |
| `UNKNOWN_METHOD` | Not `power_law` or `black_scholes` |
| `UNKNOWN_OPTION_TYPE` | Not `call` or `put` |
| `INVALID_NUMBER` | Wire value is not a JSON number |
| `NON_FINITE_INPUT` | `NaN` / `Infinity` |
| `SPOT_NOT_POSITIVE` | Spot must be positive |
| `STRIKE_NOT_POSITIVE` | BSM strike must be positive |
| `ANCHOR_PRICE_NOT_POSITIVE` | Anchor price must be positive |
| `ALPHA_OUT_OF_RANGE` | `alpha <= 1` |
| `STRIKE_DOMAIN` | Anchor/target on the wrong side of spot |
| `TIME_NOT_POSITIVE` | BSM time to expiry must be positive |
| `VOLATILITY_NOT_POSITIVE` | BSM volatility must be positive |
| `NUMERICAL_SINGULARITY` | Put denominator is too close to zero |
| `NUMERICAL_OVERFLOW` | Overflow or non-finite result |
| `NUMERICAL_ERROR` | Negative price from numerical failure |
| `INTERNAL_ERROR` | Unexpected failure at the bridge boundary |

## What the model does not claim

The power-law relation is a relative-pricing heuristic. It assumes the tail
index is constant between the anchor and target strikes, and it does not
enforce no-arbitrage conditions across the whole strike surface. The BSM tab is
a conventional comparison, not a claim that lognormal returns are correct.
This is an educational project, not investment advice.

## References

1. Taleb, N. N., Yarckin, B., Mann, C., Delic, D., & Spitznagel, M. (2019).
   *Tail Option Pricing Under Power Laws.* arXiv:1908.02347.
2. Paper copy:
   [Literature/2023-12-31-nnt-tail_option_under_power_law.pdf](../Literature/2023-12-31-nnt-tail_option_under_power_law.pdf).
