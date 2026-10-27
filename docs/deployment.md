# Deployment

## Current setup

The repository publishes the root of `main` through GitHub Pages:

```text
https://chenxu10.github.io/option-pricer/
```

That URL is stable. The page is static: HTML, CSS, JavaScript, an SVG favicon,
a small wheel, and `build-info.json`. The Python runtime itself is loaded from
the pinned Pyodide CDN and cached by the browser.

## Build the artifact

```bash
uv sync
uv run python scripts/build_site.py
```

For browser tests, include the `e2e` group and install Chromium:

```bash
uv sync --group e2e
uv run --group e2e playwright install chromium
```

The script:

1. builds `pkg/option_pricer-<version>-py3-none-any.whl`;
2. writes `build-info.json` (version, commit, contract, Pyodide version, wheel
   hash);
3. copies the wheel into `pkg/` for root deployment;
4. stages an identical `site/` directory for local preview or CI.

`site/` and `dist/` are ignored by git. `pkg/` and `build-info.json` are
committed because branch-based Pages deployment serves the repository directly.

## Preview locally

From the repository root:

```bash
python -m http.server 8000
```

Open `http://127.0.0.1:8000/`. The wheel URL in `build-info.json` is relative,
so it works at the root and under `/option-pricer/`.

For a subpath preview (the real deployment shape), stage the site under a
directory:

```bash
mkdir -p /tmp/preview
cp -r site /tmp/preview/option-pricer
cd /tmp/preview && python -m http.server 8000
# http://127.0.0.1:8000/option-pricer/
```

The Playwright E2E suite does exactly this and is the authoritative check.

## Optional migration to GitHub Actions

The manual workflow
[.github/workflows/pages-manual.yml](../.github/workflows/pages-manual.yml)
builds `site/` and deploys it with `actions/deploy-pages`. To use it:

1. Open **Settings → Pages → Build and deployment**.
2. Set **Source** to **GitHub Actions**.
3. Run the workflow manually (Actions → Deploy static site (manual) → Run).

This is intentionally manual: while the repository still publishes from the
branch root, an automatic Actions deployment would fail because Pages is not
configured for the Actions source.

## Caching and versioning

- Pyodide comes from `cdn.jsdelivr.net` with a one-year immutable cache and a
  pinned version (`314.0.7`).
- The wheel filename includes the package version; `build-info.json` is
  fetched with `cache: "no-store"`.
- The page checks the contract version at startup. If a stale HTML page pairs
  with a new wheel, the gateway shows a mismatch error instead of silently
  calling the wrong API.
- GitHub Pages serves HTML with a short cache (about 10 minutes). After a
  deploy, a hard refresh is occasionally needed in a warm browser.

## Limits and cost

GitHub Pages: 1 GB site size, 100 GB/month soft bandwidth, 10-minute deploy
timeout. This site is tens of kilobytes per visit because Pyodide is served by
the CDN. The public repository's Actions minutes are free.

## Rollback

The refactor baseline is tagged:

```bash
git tag --list 'v0.1.0-*'
```

To roll back, revert the deployment commit and push `main`; Pages republishes.
If the optional Actions workflow is enabled, re-run the workflow on the
previous commit.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `build-info.json is missing` | page opened from `file://` or build not run | run `scripts/build_site.py`, serve over HTTP |
| Wheel 404 | `pkg/` not deployed or wrong base path | use relative URLs; verify `/option-pricer/pkg/...` |
| Pyodide fails to load | CDN blocked or version wrong | check the pinned URL; consider self-hosting |
| Contract mismatch | stale HTML + new wheel | hard refresh; check `build-info.json` |
| Long first load | cold Pyodide download (~6 MB) | expected; the form renders immediately |
