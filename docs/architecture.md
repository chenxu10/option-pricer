# Architecture

The goal is orthogonality: a change to the model should not ripple into the
browser, and a change to the browser should not ripple into the model.

## Two layers, one seam

Conceptually there are two layers:

1. **Model** — the Python domain plus the application use case.
2. **Interface** — the CLI and the browser.

The application layer exists only as the seam between them. It owns typed
requests, dispatch, and the versioned JSON contract. It contains no formulas.

```text
domain/  ←  application/  ←  adapters/
  ↑              ↑
pure math     JSON v1
```

No arrow points back. The domain imports only the standard library. The
application never imports an adapter. The browser never imports Python source;
it installs a wheel and calls one function.

## Domain

`src/option_pricer/domain/`

- `power_law.py` — call and put extrapolation.
- `black_scholes.py` — European BSM with `math.erfc`.
- `validation.py` — finite/positive/numeric checks.
- `errors.py` — `PricingError` with a stable `ErrorCode` and optional field.
- `types.py` — `OptionType`, `PricingMethod`.

The functions are pure and keyword-only. They never print, read input, parse
JSON, or format numbers. The architecture test in
`tests/architecture/test_layers.py` enforces this.

## Application

`src/option_pricer/application/`

- `requests.py` — frozen dataclasses (`PowerLawRequest`, `BlackScholesRequest`).
- `pricing.py` — `price_option(request) -> PricingResult`, a thin dispatcher.
- `contract.py` — strict v1 parser and serializer.

The CLI constructs typed requests directly. The browser bridge parses JSON into
the same typed requests. Both reach the same use case.

### Contract

The wire format is deliberately small:

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

The response is an envelope with `ok`, `price`, `method`, and `option_type`, or
`ok: false` and an `error` object with `code`, `field`, and `message`. The
contract parser rejects duplicate keys, unknown fields, and non-finite
constants. The domain remains the authority on numeric rules.

## Browser adapters

- `app.js` — form state, request construction, result/error rendering. No math.
- `gateway.js` — worker lifecycle, build-info lookup, timeouts, restart.
- `pyodide-worker.js` — imports Pyodide, installs the wheel, imports
  `option_pricer.adapters.web_bridge`, forwards JSON strings.

The worker is a module worker. It is created on first use and warmed up in the
background after first paint. The gateway rejects pending requests if the
worker errors or is restarted.

JSON strings are used at the Pyodide boundary rather than PyProxy objects. This
keeps the seam explicit and avoids proxy lifetime bugs.

## Runtime sequence

1. `app.js` reads the form and builds a v1 request object.
2. `gateway.js` sends the request to the worker and waits for a response.
3. On the first request (or during warmup), the worker imports Pyodide, installs
   the wheel with `micropip`, imports the bridge, and checks the contract
   version.
4. `handle_request` parses the JSON, calls `price_option`, and returns a JSON
   envelope.
5. The gateway resolves the promise; `app.js` renders the price or the typed
   error.

## Testing

- Domain tests know nothing about the adapters.
- Contract tests pin the seam and the fixtures.
- CLI tests inject streams and assert exit codes.
- Architecture tests enforce import direction and forbid formula tokens in JS.
- One Playwright test runs the real built artifact at
  `/option-pricer/` with real Pyodide and the real wheel.

## Deliberate tradeoffs

- **Pyodide instead of a server.** Static GitHub Pages, no backend, real
  Python. Cost: ~6 MB first load, cached afterwards.
- **Thin JavaScript instead of PyScript.** The view stays native HTML/CSS; the
  JS is a transport and form controller, not a second model.
- **No framework.** One form and two formulas do not need React, a bundler, or
  a design system.
- **No JS fallback.** A second implementation of the math would defeat the
  purpose. If the runtime fails, the page says so and points to the CLI.

## Related documents

- [Model notes](model.md)
- [Deployment](deployment.md)
- [ADR 0001: Python in the browser](adr/0001-python-in-the-browser.md)
- [ADR 0002: Layers and contract](adr/0002-layers-and-contract.md)
- [ADR 0003: Static deployment](adr/0003-static-deployment.md)
