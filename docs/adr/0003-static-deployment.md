# ADR 0003: Keep branch-based static deployment, with an Actions migration path

## Context

The existing GitHub Pages site publishes the root of `main`. Changing the Pages
source to GitHub Actions is a repository-setting change and cannot be done from
the code alone. The live URL must remain
`https://chenxu10.github.io/option-pricer/`.

## Decision

Keep the root of `main` deployable:

- the view files live at the root;
- `scripts/build_site.py` writes `pkg/*.whl` and `build-info.json`;
- the same script stages `site/` for CI and browser tests;
- an optional manual workflow builds `site/` and deploys it once the repository
  owner switches Pages to the Actions source.

## Consequences

- A normal `git push` to `main` updates the live site without a settings
  change.
- The built wheel and `build-info.json` are committed. The wheel is small
  (~16 KB) and has no runtime dependencies.
- CI verifies the wheel, the model, and the real browser artifact before the
  push.
- The migration to Actions is a documented, reversible switch rather than a
  hidden dependency.
