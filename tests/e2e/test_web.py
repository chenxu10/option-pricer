"""End-to-end test of the real static artifact and the real Pyodide runtime.

This is deliberately slow and network-dependent; run it with ``pytest -m e2e``.
It is the only test that proves the deployed wiring, not just the Python model.
"""

from __future__ import annotations

import functools
import http.server
import subprocess
import sys
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import Page, sync_playwright  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="session")
def staged_site(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_site.py")],
        cwd=ROOT,
        check=True,
    )
    if not (SITE / "index.html").exists():
        pytest.fail("build_site.py did not stage site/index.html")

    www = tmp_path_factory.mktemp("www")
    target = www / "option-pricer"
    target.mkdir()
    for item in SITE.iterdir():
        if item.is_dir():
            (target / item.name).mkdir()
            for child in item.iterdir():
                (target / item.name / child.name).write_bytes(child.read_bytes())
        else:
            (target / item.name).write_bytes(item.read_bytes())

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=str(www),
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        yield f"http://127.0.0.1:{port}/option-pricer/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
        except Exception:
            try:
                browser = playwright.chromium.launch(headless=True)
            except Exception as exc:  # pragma: no cover - environment dependent
                pytest.skip(f"no Chromium available for Playwright: {exc}")
        yield browser
        browser.close()


@pytest.fixture()
def page(browser, staged_site: str) -> Iterator[Page]:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.set_default_timeout(30_000)
    page.goto(staged_site, wait_until="domcontentloaded")
    page.wait_for_function(
        "document.querySelector('#runtime-status')?.dataset.state === 'ready'",
        timeout=120_000,
    )
    try:
        yield page
    finally:
        page.close()


def _fill_power_law_call(page: Page) -> None:
    page.fill("#spot", "581.73")
    page.fill("#anchor_strike", "590")
    page.fill("#target_strike", "600")
    page.fill("#anchor_price", "0.03")
    page.fill("#alpha", "2.6")


def test_power_law_call_end_to_end(page: Page) -> None:
    _fill_power_law_call(page)
    page.click("#calculate")
    page.wait_for_function("document.querySelector('#result').textContent.includes('0.008440')")
    assert page.text_content("#result-label") == "C(K2)"
    assert page.text_content("#error") == ""


def test_black_scholes_call_end_to_end(page: Page) -> None:
    page.check('input[name="method"][value="black_scholes"]')
    page.fill("#spot", "100")
    page.fill("#strike", "100")
    page.fill("#time_to_expiry", "0.25")
    page.fill("#rate", "0.05")
    page.fill("#volatility", "0.2")
    page.click("#calculate")
    page.wait_for_function("document.querySelector('#result').textContent.includes('4.614997')")
    assert page.text_content("#result-label") == "BSM call"


def test_domain_error_is_rendered_and_field_is_focused(page: Page) -> None:
    _fill_power_law_call(page)
    page.fill("#anchor_strike", "90")
    page.click("#calculate")
    page.wait_for_selector("#error:not([hidden])")
    assert "K1 must be greater than S0" in page.text_content("#error")
    assert page.get_attribute("#anchor_strike", "aria-invalid") == "true"


def test_switching_method_hides_irrelevant_fields(page: Page) -> None:
    assert not page.locator("#power-law-fields").is_hidden()
    page.check('input[name="method"][value="black_scholes"]')
    assert page.locator("#power-law-fields").is_hidden()
    assert not page.locator("#bsm-fields").is_hidden()
    assert page.locator("#bsm-formula").is_visible()


def test_page_reports_the_build_metadata(page: Page) -> None:
    page.wait_for_function("document.querySelector('#build-version').textContent !== 'dev'")
    assert "0.2.0" in page.text_content("#build-version")
