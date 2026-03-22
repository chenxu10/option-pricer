# Option Pricer - Power Law Tail Pricing

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://yourusername.github.io/option-pricer/)

> **TLDR**: Calculate far out-of-the-money option prices using Taleb's power law formula. Runs entirely in your browser - no server needed.

[Live Demo](https://yourusername.github.io/option-pricer/)

## What This Tool Does

This tool estimates the price of a far out-of-the-money call option C(K2) given the known price C(K1) of a closer-to-the-money option, using the assumption that tail risk follows a power law distribution.

**Formula:** `C(K2) = ((K2 - S0) / (K1 - S0))^(1 - alpha) * C(K1)`

### Parameters
- **S0**: Current underlying price
- **K1**: Strike price where we know the option price (must be > S0)
- **K2**: Strike price we want to price (must be > S0)
- **C(K1)**: Known call option price at K1 (must be positive)
- **Alpha**: Tail index/power law exponent (must be > 1)

## Why Power Law?

Most financial models assume normal distributions, but extreme events (market crashes) happen more frequently than normal distributions predict. The power law distribution better captures "fat tails" - the probability of rare but extreme events.

This approach avoids two common traps:
1. **Pure theoretical models** (like Black-Scholes) that assume normality and ignore tail risk
2. **Pure empirical approaches** that assume "this time is different" but ignore the mathematical structure of extreme events

## Deployment to GitHub Pages

This is a **static website** - all calculations happen in your browser using JavaScript. No Python server required.

### Quick Deploy

1. Fork or clone this repository
2. Go to your forked repo on GitHub
3. Click **Settings** → **Pages** (in the left sidebar)
4. Under "Source", select **Deploy from a branch**
5. Select **main** branch and **/(root)** folder
6. Click **Save**
7. Wait 2-5 minutes
8. Your site will be live at: `https://yourusername.github.io/option-pricer/`

### Files Explained

- `index.html` - The web interface
- `script.js` - The pricing calculation (runs in browser)
- No server-side code needed!

## Local Development

To test locally, simply open `index.html` in your browser:

```bash
# Or use Python's built-in server
python -m http.server 8000
# Then open http://localhost:8000
```

## References

1. Taleb, N. N., et al. (2019). "Tail Option Pricing Under Power Laws". arXiv:1908.02347.

## License

MIT
