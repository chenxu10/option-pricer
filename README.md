# Option Pricer

[Live site](https://chenxu10.github.io/option-pricer/) ·
[CI](https://github.com/chenxu10/option-pricer/actions/workflows/ci.yml)

A tail-option pricing calculator with **one Python model** and two adapters:
a command-line interface and a static browser UI. The browser runs CPython
through [Pyodide](https://pyodide.org/), so the site remains a pure static
GitHub Pages deployment — no Python server, no duplicated JavaScript math.

The model implements Taleb's power-law extrapolation of far out-of-the-money
option prices from an observed anchor strike, alongside a
Black-Scholes-Merton benchmark.

## What it does

- **Power-law tail pricing.** Given `S0`, an anchor strike `K1`, a target
  strike `K2`, the observed option price at `K1`, and a tail index `α > 1`,
  estimate the price at `K2`.
- **Calls and puts.** Calls use the direct strike-space formula; puts use the
  return-space form `r = (S0 − K) / S0`, which keeps returns positive for
  out-of-the-money puts.
- **BSM benchmark.** European call and put prices with a standard-library
  implementation of Black-Scholes-Merton.
- **CLI and web parity.** Both adapters call the same application use case and
  the same domain functions.

## Why Python in the browser?

GitHub Pages serves static files only. Pyodide is CPython compiled to
WebAssembly: the browser downloads it as a static asset and runs it locally.
The first visit downloads about 6 MB (cached by the CDN); the form itself
renders immediately and the runtime warms up in the background. Subsequent
calculations are effectively instant.

This is a deliberate tradeoff. A 30-line JavaScript formula would load faster,
but it would recreate the problem this project exists to remove: two
implementations of the same math, with the deployed one untested. The model is
the product; the JavaScript is a thin transport layer.

Measured on a desktop Chrome session in October 2026: the form's DOM was ready
in under a second, the Python runtime was ready in about 6–7 seconds on a cold
cache, and the priced result followed immediately. Repeat visits benefit from
the CDN's immutable cache.

## Architecture

```text
Browser (static GitHub Pages)
┌──────────────────────────────────────────────────────────────┐
│  index.html + styles.css        view                          │
│  app.js                         form controller               │
│        │  JSON request/response                               │
│        ▼                                                      │
│  gateway.js                     worker + timeout lifecycle    │
│        │                                                      │
│  pyodide-worker.js              transport only                │
│        │                                                      │
│  Pyodide (CPython 3.14 → WASM)                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  adapters/web_bridge.py     JSON v1 ↔ typed request    │   │
│  │        │                                               │   │
│  │        ▼                                               │   │
│  │  application/pricing.py     price_option(request)      │   │
│  │        │                                               │   │
│  │        ▼                                               │   │
│  │  domain/                    power law + BSM            │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
          ▲ same wheel
CLI ──────┘  `option-pricer ...`
```

| Layer | Responsibility | Must not know |
|---|---|---|
| `domain/` | Formulas, invariants, typed numeric errors | JSON, DOM, CLI, Pyodide |
| `application/` | Typed requests, dispatch, v1 JSON contract | DOM, labels, Pyodide |
| `adapters/` | CLI and browser bridge | Formulas |
| `app.js` / `gateway.js` | Form state, worker transport | Pricing math |
| `pyodide-worker.js` | Load runtime and wheel, forward JSON | Pricing math |

The dependency rule is one-directional: **domain ← application ← adapters**.
An AST-based architecture test enforces it.

More detail: [architecture](docs/architecture.md) and the
[ADRs](docs/adr/).

## Model

Call, strike space:

```text
C(K2) = C(K1) × [(K2 − S0) / (K1 − S0)]^(1−α)
```

Put, return space (`r = (S0 − K) / S0`):

```text
P(K2) = P(K1) × [α − r2^(1−α) − (α−1)r2]
                / [α − r1^(1−α) − (α−1)r1]
```

BSM uses the standard normal CDF evaluated with `math.erfc`, which avoids
cancellation in the far tail. There are no runtime dependencies.

See [docs/model.md](docs/model.md) for assumptions, validation rules, and
numerical notes.

## Quick start

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync

# Power-law call
uv run option-pricer powerlaw \
  --option-type call --spot 581.73 \
  --anchor-strike 590 --target-strike 600 \
  --anchor-price 0.03 --alpha 2.6

# BSM put, machine-readable
uv run option-pricer bsm \
  --option-type put --spot 100 --strike 100 \
  --time 0.25 --rate 0.05 --vol 0.2 --json
```

Build the wheel and the local static artifact:

```bash
uv run python scripts/build_site.py
```

The repository root is directly deployable. To preview locally with the wheel
and build metadata:

```bash
python -m http.server 8000
# open http://127.0.0.1:8000/
```

## Tests

```bash
uv run pytest -m "not e2e"   # fast: domain, contract, CLI, architecture

# browser test: needs the e2e group and a browser
uv sync --group e2e
uv run --group e2e playwright install chromium
uv run --group e2e pytest -m e2e   # real Chromium + real Pyodide + wheel
```

`uv run` installs the default `dev` dependency group, so `uv run pytest` works
in a fresh clone. If it reports collection errors or an old `pytest 6.x`, the
local `.venv` predates the dependency-group change; rebuild it with
`uv sync --reinstall` (or delete `.venv` and rerun).

The suite includes:

- golden values and Hypothesis property tests for the formulas;
- BSM put-call parity and bounds;
- strict v1 contract tests (malformed JSON, NaN, unknown fields, error codes);
- CLI tests with injected streams;
- architecture tests that forbid formulas in JavaScript and I/O in the domain;
- a Playwright end-to-end test of the built artifact at the real
  `/option-pricer/` subpath.

CI runs Python 3.12, 3.13, and 3.14, plus a browser job and a wheel job. See
[.github/workflows/ci.yml](.github/workflows/ci.yml).

## Deployment

The current GitHub Pages publishing source is the repository root of `main`.
`scripts/build_site.py` writes the versioned wheel to `pkg/`, the build
metadata to `build-info.json`, and stages an identical `site/` directory for
CI or an Actions-based deployment.

To migrate to Actions, set **Settings → Pages → Source** to **GitHub Actions**
and run the [manual deployment workflow](.github/workflows/pages-manual.yml).
The live URL does not change. See [docs/deployment.md](docs/deployment.md).

## Contract

The Python/JavaScript seam is a small, versioned JSON envelope. Example:

```json
{
  "version": "v1",
  "method": "power_law",
  "option_type": "call",
  "spot": 581.73,
  "anchor_strike": 590,
  "target_strike": 600,
  "anchor_price": 0.03,
  "alpha": 2.6
}
```

Success:

```json
{"version":"v1","ok":true,"price":0.00844,"method":"power_law","option_type":"call"}
```

Failure:

```json
{"version":"v1","ok":false,"error":{"code":"STRIKE_DOMAIN","field":"anchor_strike","message":"K1 must be greater than S0 for calls."}}
```

Fixtures live in [contracts/v1/examples](contracts/v1/examples). The Python
side rejects malformed JSON, duplicate keys, unknown fields, and non-finite
numbers; errors carry a stable code and field for the UI to map.

## Project layout

```text
src/option_pricer/
  domain/            pure formulas and typed errors
  application/       typed requests, use case, v1 contract
  adapters/          CLI and web bridge
index.html           view
styles.css
app.js               form controller
gateway.js           worker transport
pyodide-worker.js    Pyodide loader
scripts/build_site.py
tests/               domain, application, adapters, architecture, e2e
contracts/v1/        JSON fixtures
docs/                architecture, model, ADRs, deployment
pkg/                 built wheel (small, committed for root deployment)
```

## Design notes

The refactor follows the orthogonality principle from *The Pragmatic
Programmer*: eliminate effects between unrelated things. Concretely:

- changing a validation rule touches one domain file, not the UI;
- changing the BSM implementation does not touch the browser;
- changing the layout does not touch Python;
- swapping Pyodide for an HTTP API means replacing `gateway.js` and the worker,
  not the model;
- the only duplicated shape is the JSON contract, and it is tested at the seam.

## Limitations

The power-law model is a relative tail-pricing heuristic, not a no-arbitrage
model. It assumes a constant tail index between the two strikes. BSM assumes
European exercise, no dividends, constant volatility, and a constant rate.
This is an educational project, not investment advice.

## Motivation and references

The original essay — on Bayesian inference, language, and the two traps of pure
experience and pure theory — is preserved in
[docs/motivation.md](docs/motivation.md).

1. Taleb, N. N., Yarckin, B., Mann, C., Delic, D., & Spitznagel, M. (2019).
   *Tail Option Pricing Under Power Laws.* arXiv:1908.02347.
2. The paper copy is in
   [Literature/2023-12-31-nnt-tail_option_under_power_law.pdf](Literature/2023-12-31-nnt-tail_option_under_power_law.pdf).
