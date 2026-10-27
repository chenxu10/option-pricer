# ADR 0001: Run the Python model in the browser with Pyodide

## Context

The project is deployed to GitHub Pages, which serves static files only. The
model must remain Python, and there must be a single implementation of the
formulas. A server-side Python process is not available on Pages.

## Decision

Use Pyodide, CPython compiled to WebAssembly, as a static runtime. The browser
downloads the pinned runtime and a small pure-Python wheel, installs the wheel
with `micropip`, and calls a narrow bridge function.

The alternative — a Python API hosted elsewhere with the UI on Pages — was
rejected because it adds a second deployment, CORS, cold starts, and an
availability dependency for a two-formula calculator.

## Consequences

- The deployment remains static and serverless; the URL does not change.
- The first visit costs about 6 MB and a few seconds. The form renders
  immediately, the runtime is warmed in a worker, and the CDN caches it.
- The wheel must remain pure Python (no NumPy/SciPy/pandas). BSM uses
  `math.erfc`; `py_vollib` was removed.
- The Python version is tied to Pyodide (3.14 for 314.0.7). CI tests 3.12,
  3.13, and 3.14.
- A browser without WebAssembly or module workers cannot calculate; the page
  explains this and points to the CLI.
