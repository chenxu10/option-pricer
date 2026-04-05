# Polya's How to Solve It: Put Option Pricing Proof Exercises

## Introduction

> "If you can't solve a problem, then there is an easier problem you can't solve: find it."
> — George Pólya

This exercise follows Pólya's problem-solving methodology to guide you through proving the **Put Option Pricing Formula under Power Laws** from first principles. The formula states:

For two put strikes K1, K2 <= (1 - l)*S0 where S0 is the current underlying price and l is the Karamata constant:

P(K2) / P(K1) = [(K2 - S0)^(1-alpha) - S0^(1-alpha)*((alpha - 1)*K2 + S0)] / [(K1 - S0)^(1-alpha) - S0^(1-alpha)*((alpha - 1)*K1 + S0)]

The approach decomposes the proof into **10 mini-problems**, progressing from easy warm-ups to the final derivation. Work through each problem independently before checking solutions.

---

## Difficulty Legend
- 🟢 **Easy**: Warm-up, applying definitions
- 🟡 **Medium**: Combining multiple concepts, algebraic manipulation
- 🔴 **Hard**: Creative insights, putting it all together

---

## Problem 1: Understanding the Pareto Distribution 🟢

### Hypothesis
Let r be a random variable following a Pareto Type I distribution in the positive domain with tail index alpha > 1 and scale parameter l > 0. The survival function (complementary CDF) is given by:

P(r > x) = (l/x)^alpha    for x >= l

### Task
Derive the **probability density function (PDF)** f_r(r) for this Pareto distribution.

### Conclusion to Prove
Show that:
f_r(r) = alpha * l^alpha * r^(-alpha-1)    for r >= l

---

## Problem 2: Transforming the Random Variable 🟢

### Hypothesis
Let S0 be the current price of an underlying asset. Define the put return as:

r = (S0 - S) / S0

where S is the future asset price. This implies:
S = (1 - r)*S0

The return r follows the Pareto distribution from Problem 1, meaning r ∈ [l, infinity) for some l > 0.

### Task
Determine the **range of possible values** for the future asset price S.

### Conclusion to Prove
Show that S is bounded above and find the valid range:
S ∈ [0, (1-l)*S0]

---

## Problem 3: PDF Transformation Formula 🟡

### Hypothesis
We have a random variable r with PDF f_r(r), and a transformation S = g(r) = (1-r)*S0. The inverse transformation is r = h(S) = (S0 - S) / S0.

### Task
Apply the **change of variables formula** for probability densities:
f_S(S) = f_r(h(S)) * |dr/dS|

### Conclusion to Prove
Derive the PDF of S:
f_S(S) = (alpha * l^alpha / S0) * (S0 / (S0 - S))^(alpha+1)    for S ∈ [0, (1-l)*S0]

---

## Problem 4: Normalization Constant 🟡

### Hypothesis
The PDF f_S(S) derived above should integrate to 1 over its domain. However, we need to introduce a normalization constant lambda because the Pareto distribution only applies in the tail region r >= l (i.e., S <= (1-l)*S0).

Define the put option payoff PDF with normalization:
f_S(S) = lambda * (alpha * l^alpha / S0) * (S0 / (S0 - S))^(alpha+1)

where lambda = (-1)^(alpha+1) / (l^alpha - 1) ensures the density integrates to 1.

### Task
Verify that this normalization makes f_S(S) a valid probability density function over [0, (1-l)*S0].

### Conclusion to Prove
Show that:
integral from 0 to (1-l)*S0 of f_S(S) dS = 1

**Hint**: Consider the substitution u = (S0 - S) / S0 and use the fact that integral from l to 1 of alpha * l^alpha * u^(-alpha-1) du can be evaluated directly.

---

## Problem 5: Defining the Put Option Price 🟢

### Hypothesis
A European put option with strike K and underlying price S0 has payoff max(K - S, 0) at expiration. Under risk-neutral pricing, the put value is:

P(K) = E[max(K - S, 0)]

where E[.] denotes expectation.

### Task
Write the put option price as an integral over the relevant domain, using the PDF f_S(S) derived earlier.

### Conclusion to Prove
Show that:
P(K) = integral from 0 to min(K, (1-l)*S0) of (K - S) * f_S(S) dS

For strikes K <= (1-l)*S0 (deep out-of-the-money puts in the tail region), this becomes:
P(K) = lambda * (alpha * l^alpha / S0) * integral from 0 to K of (K - S) * (S0 / (S0 - S))^(alpha+1) dS

---

## Problem 6: Integral Decomposition 🟡

### Hypothesis
For K <= (1-l)*S0, the put price integral is:

P(K) = lambda * alpha * l^alpha * S0^alpha * integral from 0 to K of (K - S) / (S0 - S)^(alpha+1) dS

### Task
Decompose this integral into two simpler integrals by splitting (K - S) = K - S.

### Conclusion to Prove
Show that:
P(K) = lambda * alpha * l^alpha * S0^alpha * [ K * integral from 0 to K of 1/(S0 - S)^(alpha+1) dS - integral from 0 to K of S/(S0 - S)^(alpha+1) dS ]

---

## Problem 7: Evaluating the First Integral 🟡

### Hypothesis
Consider the integral:
I1 = integral from 0 to K of 1/(S0 - S)^(alpha+1) dS

where alpha > 1, K < S0, and S0 > 0.

### Task
Evaluate this integral using the substitution u = S0 - S.

### Conclusion to Prove
Show that:
I1 = (1/alpha) * [ 1/(S0 - K)^alpha - 1/S0^alpha ]

**Hint**: Note that du = -dS, so the limits transform as: when S=0, u=S0; when S=K, u=S0-K.

---

## Problem 8: Evaluating the Second Integral 🔴

### Hypothesis
Consider the integral:
I2 = integral from 0 to K of S/(S0 - S)^(alpha+1) dS

where alpha > 1, K < S0, and S0 > 0.

### Task
Evaluate this integral. **Hint**: Use the substitution u = S0 - S (so S = S0 - u) and then split the integral.

### Conclusion to Prove
Show that:
I2 = (1/((alpha-1)*alpha)) * [ (alpha-1)*S0 * (1/(S0-K)^alpha - 1/S0^alpha) - alpha*(1/(S0-K)^(alpha-1) - 1/S0^(alpha-1)) ]

Or equivalently:
I2 = (S0/alpha) * [ 1/(S0 - K)^alpha - 1/S0^alpha ] - (1/(alpha-1)) * [ 1/(S0 - K)^(alpha-1) - 1/S0^(alpha-1) ]

---

## Problem 9: Combining Results 🔴

### Hypothesis
Using the results from Problems 6, 7, and 8, we have:

P(K) = lambda * alpha * l^alpha * S0^alpha * [ K * I1 - I2 ]

Substitute the expressions for I1 and I2 from Problems 7 and 8.

### Task
Simplify the expression K * I1 - I2 and then multiply by the prefactors.

### Conclusion to Prove
Show that for K <= (1-l)*S0:

P(K) = lambda * l^alpha * S0^alpha * [ (1/(alpha-1))*(1/(S0 - K)^(alpha-1) - 1/S0^(alpha-1)) - K/S0^alpha ]

Or in a cleaner form:

P(K) = lambda * l^alpha * [ (S0^alpha/(alpha-1))*(1/(S0 - K)^(alpha-1) - 1/S0^(alpha-1)) - K/S0 ]

---

## Problem 10: The Final Ratio - Relative Put Pricing 🔴

### Hypothesis
Let K1, K2 <= (1-l)*S0 be two put strikes in the tail region. From Problem 9, we have:

P(K) = C * [ (S0^alpha/(alpha-1))*(1/(S0 - K)^(alpha-1) - 1/S0^(alpha-1)) - K/S0 ]

where C = lambda * l^alpha is a constant independent of K.

### Task
Derive the ratio P(K2)/P(K1) and simplify the expression by algebraic manipulation. Note that the constant C cancels out, as does the term involving S0^(alpha-1) in a specific way.

### Conclusion to Prove
Show that:

P(K2) / P(K1) = [(K2 - S0)^(1-alpha) - S0^(1-alpha)*((alpha - 1)*K2 + S0)] / [(K1 - S0)^(1-alpha) - S0^(1-alpha)*((alpha - 1)*K1 + S0)]

Or equivalently (multiplying numerator and denominator by -1 to present in the paper's form):

P(K2) / P(K1) = [(K2 - S0)^(1-alpha) - S0^(1-alpha)*((alpha-1)*K2 + S0)] / [(K1 - S0)^(1-alpha) - S0^(1-alpha)*((alpha-1)*K1 + S0)]

**Key Insight**: This remarkable formula shows that **relative put pricing in the tail region depends only on the strikes, the current price, and the tail index alpha** — not on any other parameters like volatility, drift, or the Karamata constant l!

---

## Pólya's Problem-Solving Checklist

As you work through these problems, ask yourself:

1. **Understand the problem**: Can I restate the problem in my own words? Do I know what I'm trying to find?

2. **Devise a plan**: Have I seen this before? Can I use a similar problem's solution? Can I break it into smaller steps?

3. **Carry out the plan**: Am I checking each step? Can I clearly see that each step is correct?

4. **Look back**: Can I verify the result? Does it make sense dimensionally? Can I derive it differently?

---

## Additional Challenge Problems

Once you've completed the main proof, consider these extensions:

### Challenge A: Call-Put Parity
Can you derive the corresponding formula for call options in the right tail (K >= (1+l)*S0)? How does put-call parity relate the two formulas?

### Challenge B: Limit Behavior
What happens to the put pricing formula as alpha approaches infinity? Does it converge to the Black-Scholes behavior? Prove your claim.

### Challenge C: Sensitivity Analysis
Compute the partial derivative of P(K) with respect to alpha. How does the put price change as the tail becomes fatter (smaller alpha) vs. thinner (larger alpha)?

---

## References

- Taleb, N.N., et al. (2023). "Tail Option Pricing Under Power Laws"
- Pólya, G. (1945). "How to Solve It"
- Mandelbrot, B. (1963). "The Variation of Certain Speculative Prices"

---

*"Mathematics is the art of giving the same name to different things."* — Henri Poincaré

*"The goal is to teach students to find proofs independently by themselves."* — George Pólya
