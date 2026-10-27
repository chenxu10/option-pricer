# ADR 0002: Separate the domain, application, and adapters with a JSON contract

## Context

The original implementation had the formulas and validation in both
`script.js` and `src/option_pricer.py`. The CLI lived in the model module. The
deployed JavaScript was untested, and the two BSM implementations already
disagreed at the `1e-5` level because one used an `erf` approximation.

## Decision

Use three Python layers:

- `domain/` — pure formulas, invariants, typed errors, standard library only.
- `application/` — typed requests, dispatch, versioned JSON contract.
- `adapters/` — CLI and browser bridge.

The browser crosses the language boundary with JSON strings and a v1 envelope.
The CLI constructs typed requests directly. Both call `price_option`.

The contract is deliberately strict: unknown fields, duplicate keys, and
non-finite constants are rejected. Errors carry a stable code and field.

## Consequences

- A formula change touches the domain and its tests, not the UI.
- A layout change touches HTML/CSS/JS, not Python.
- A runtime swap (Pyodide to HTTP) touches `gateway.js` and the worker, not the
  model or the UI.
- The request shape exists on both sides of the boundary. That small
  duplication is accepted; the rules are not duplicated.
- Architecture tests enforce the dependency direction and forbid formulas in
  JavaScript.
