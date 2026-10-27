#!/usr/bin/env python3
"""Build the wheel and stage the static GitHub Pages artifact.

The repository root is directly deployable by GitHub Pages (the existing
publishing source).  This script also stages an identical site/ directory for
CI, local browser tests, or a future Actions-based deployment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PKG = ROOT / "pkg"
SITE = ROOT / "site"

WEB_FILES = (
    "index.html",
    "styles.css",
    "app.js",
    "gateway.js",
    "pyodide-worker.js",
    "favicon.svg",
)
EXTRA_SITE_FILES = ("README.md",)

PYODIDE_VERSION = "314.0.7"
PYODIDE_BASE = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/"
CONTRACT_VERSION = "v1"


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def _project_version() -> str:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    return str(pyproject["project"]["version"])


def _commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "dev"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_wheel() -> Path:
    DIST.mkdir(exist_ok=True)
    for old in DIST.glob("option_pricer-*.whl"):
        old.unlink()
    _run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(DIST),
        ]
    )
    wheels = sorted(DIST.glob("option_pricer-*.whl"), key=lambda path: path.stat().st_mtime)
    if not wheels:
        raise SystemExit("wheel build produced no artifact")
    wheel = wheels[-1]

    PKG.mkdir(exist_ok=True)
    for old in PKG.glob("option_pricer-*.whl"):
        old.unlink()
    destination = PKG / wheel.name
    shutil.copy2(wheel, destination)
    return destination


def write_build_info(wheel: Path) -> dict[str, object]:
    info: dict[str, object] = {
        "version": _project_version(),
        "commit": _commit(),
        "contract": CONTRACT_VERSION,
        "pyodide": {
            "version": PYODIDE_VERSION,
            "url": f"{PYODIDE_BASE}pyodide.mjs",
            "indexURL": PYODIDE_BASE,
        },
        "wheel": f"pkg/{wheel.name}",
        "wheel_sha256": _sha256(wheel),
        "built_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    text = json.dumps(info, indent=2) + "\n"
    (ROOT / "build-info.json").write_text(text)
    return info


def stage_site(info: dict[str, object]) -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    for name in WEB_FILES:
        shutil.copy2(ROOT / name, SITE / name)
    for name in EXTRA_SITE_FILES:
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, SITE / name)
    (SITE / "build-info.json").write_text(json.dumps(info, indent=2) + "\n")

    site_pkg = SITE / "pkg"
    site_pkg.mkdir()
    shutil.copy2(PKG / str(info["wheel"]).removeprefix("pkg/"), site_pkg)
    (SITE / ".nojekyll").write_text("")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-wheel",
        action="store_true",
        help="reuse the existing pkg/*.whl instead of rebuilding it",
    )
    args = parser.parse_args()

    if args.skip_wheel:
        wheels = sorted(PKG.glob("option_pricer-*.whl"), key=lambda path: path.stat().st_mtime)
        if not wheels:
            raise SystemExit("no pkg/option_pricer-*.whl to reuse")
        wheel = wheels[-1]
    else:
        wheel = build_wheel()

    info = write_build_info(wheel)
    stage_site(info)

    print(f"wheel: {PKG / wheel.name}")
    print(f"build-info: {ROOT / 'build-info.json'}")
    print(f"site: {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
