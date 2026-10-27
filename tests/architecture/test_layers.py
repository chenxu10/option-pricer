"""Orthogonality is enforced, not just documented.

If the model starts importing JSON, the web bridge starts containing formulas,
or the UI starts knowing the math, these tests fail.
"""

import ast
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "option_pricer"
WEB = ROOT


def _absolute_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.append(node.module)
    return modules


def _relative_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level > 0 and node.module:
            modules.append(node.module)
    return modules


def test_domain_imports_only_the_standard_library() -> None:
    forbidden = {
        "json",
        "os",
        "sys",
        "traceback",
        "flask",
        "pyodide",
        "js",
        "option_pricer.application",
        "option_pricer.adapters",
    }
    for path in (SRC / "domain").glob("*.py"):
        for module in _absolute_imports(path):
            root = module.split(".")[0]
            if root in {"option_pricer"}:
                assert not module.startswith("option_pricer.application")
                assert not module.startswith("option_pricer.adapters")
            else:
                assert root not in forbidden, f"{path.name} imports {module}"
        for module in _relative_imports(path):
            assert module not in {"application", "adapters"}, f"{path.name} imports {module}"


def test_domain_has_no_io_or_printing() -> None:
    for path in (SRC / "domain").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"print", "input"}, f"{path.name} calls {node.func.id}"


def test_application_does_not_import_adapters() -> None:
    for path in (SRC / "application").glob("*.py"):
        for module in _absolute_imports(path):
            assert not module.startswith("option_pricer.adapters"), f"{path.name} imports {module}"
        for module in _relative_imports(path):
            assert module != "adapters", f"{path.name} imports adapters"


def test_adapters_do_not_import_web_frameworks() -> None:
    for path in (SRC / "adapters").glob("*.py"):
        for module in _absolute_imports(path):
            assert module.split(".")[0] not in {"flask", "pyodide", "js"}


def test_public_package_import_does_not_pull_in_the_cli() -> None:
    code = (
        "import option_pricer, sys; "
        "assert 'option_pricer.adapters.cli' not in sys.modules; "
        "print(option_pricer.__version__)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "0.2.0"


def test_javascript_contains_no_pricing_formulas() -> None:
    forbidden = ("priceCall", "pricePut", "normalCDF", "Math.pow", "Math.erf", "bsmCall", "bsmPut")
    for name in ("app.js", "gateway.js", "pyodide-worker.js"):
        path = WEB / name
        assert path.exists(), f"missing {name}"
        source = path.read_text()
        for token in forbidden:
            assert token not in source, f"{name} contains formula token {token!r}"


def test_runtime_has_no_third_party_dependencies() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert pyproject["project"]["dependencies"] == []
    assert "flask" not in (ROOT / "pyproject.toml").read_text().lower()
    assert "py-vollib" not in (ROOT / "pyproject.toml").read_text().lower()
