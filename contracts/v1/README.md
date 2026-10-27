# Contract v1

This is the only interface between the Python model and the browser. It is
versioned independently of the wheel version.

## Request

Every request is a JSON object with `version`, `method`, `option_type`, and the
fields for that method.

### `power_law`

| Field | Type | Notes |
|---|---|---|
| `version` | string | `"v1"` |
| `method` | string | `"power_law"` |
| `option_type` | string | `"call"` or `"put"` |
| `spot` | number | `S0 > 0` |
| `anchor_strike` | number | calls above spot, puts below spot |
| `target_strike` | number | calls above spot, puts below spot |
| `anchor_price` | number | observed `C(K1)` or `P(K1)`, `> 0` |
| `alpha` | number | tail index, `> 1` |

### `black_scholes`

| Field | Type | Notes |
|---|---|---|
| `version` | string | `"v1"` |
| `method` | string | `"black_scholes"` |
| `option_type` | string | `"call"` or `"put"` |
| `spot` | number | `S > 0` |
| `strike` | number | `K > 0` |
| `time_to_expiry` | number | `T > 0`, years |
| `rate` | number | continuously compounded, may be negative |
| `volatility` | number | `sigma > 0`, annualised decimal |

Unknown fields, missing fields, duplicate keys, `NaN`, and `Infinity` are
rejected. Numbers must be JSON numbers, not strings or booleans.

## Success envelope

```json
{
  "version": "v1",
  "ok": true,
  "price": 0.008440115585640976,
  "method": "power_law",
  "option_type": "call"
}
```

## Error envelope

```json
{
  "version": "v1",
  "ok": false,
  "error": {
    "code": "STRIKE_DOMAIN",
    "field": "anchor_strike",
    "message": "K1 must be greater than S0 for calls."
  }
}
```

`code` is stable; `message` is English prose and may change. `field` is the
wire field name so the UI can focus the offending input.

## Versioning

A breaking change to the shape or semantics gets a new version (`v2`). The
page, worker, and wheel deploy together, but a stale cached page can still meet
a new wheel; the gateway checks the contract version and fails visibly rather
than calling the wrong API.

## Fixtures

The files in [`examples/`](examples/) are used by the Python contract tests and
are intentionally human-readable. Add a fixture whenever a new request shape is
introduced.
