# Plan and status

## Principles

- One source of truth for the pricing math.
- Orthogonality: the model does not know about JSON, the DOM, the CLI, or
  Pyodide; the UI does not know the formulas.
- TDD by layer: characterization tests first, then domain, contract, adapter,
  and end-to-end tests.
- Keep the deployment static and the URL stable.

## Completed

- [x] Extract `src/option_pricer/domain` with typed errors and stdlib BSM.
- [x] Add the application layer and the versioned JSON v1 contract.
- [x] Move the CLI to `adapters/cli.py` with injected streams and subcommands.
- [x] Replace `py_vollib` (and its pandas/scipy/numpy chain) with
  `math.erfc`-based BSM.
- [x] Rebuild the web UI with semantic HTML, a form controller, a worker
  gateway, and a thin Pyodide bridge.
- [x] Add architecture, contract, CLI, property, and Playwright E2E tests.
- [x] Add wheel/site build tooling and CI workflows.
- [x] Document the model, architecture, deployment, and ADRs.

## Next

- [ ] Migrate Pages publishing to the manual Actions workflow (optional; see
  `docs/deployment.md`).
- [ ] Update the resume bullet after the deployed site has been measured.
- [ ] Consider self-hosting Pyodide if the CDN is unreliable for the audience.
