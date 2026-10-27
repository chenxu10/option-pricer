"""CLI adapter tests use injected streams, not monkeypatched globals."""

import io
import json

from option_pricer.adapters.cli import main


def _run(*args: str) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = main(list(args), stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


def test_power_law_call_output() -> None:
    code, out, err = _run(
        "powerlaw",
        "--option-type",
        "call",
        "--spot",
        "100",
        "--anchor-strike",
        "120",
        "--target-strike",
        "130",
        "--anchor-price",
        "5",
        "--alpha",
        "3",
    )
    assert code == 0
    assert "C(K2) = 2.222222" in out
    assert err == ""


def test_power_law_put_output() -> None:
    code, out, _ = _run(
        "powerlaw",
        "--option-type",
        "put",
        "--spot",
        "100",
        "--anchor-strike",
        "90",
        "--target-strike",
        "80",
        "--anchor-price",
        "2",
        "--alpha",
        "2.5",
    )
    assert code == 0
    assert "P(K2) = 0.613563" in out


def test_bsm_output() -> None:
    code, out, _ = _run(
        "bsm",
        "--option-type",
        "call",
        "--spot",
        "100",
        "--strike",
        "100",
        "--time",
        "0.25",
        "--rate",
        "0.05",
        "--vol",
        "0.2",
    )
    assert code == 0
    assert "BSM call = 4.614997" in out


def test_json_output_matches_the_contract() -> None:
    code, out, _ = _run(
        "bsm",
        "--option-type",
        "put",
        "--spot",
        "100",
        "--strike",
        "100",
        "--time",
        "0.25",
        "--rate",
        "0.05",
        "--vol",
        "0.2",
        "--json",
    )
    assert code == 0
    envelope = json.loads(out)
    assert envelope["ok"] is True
    assert envelope["version"] == "v1"
    assert envelope["price"] == 3.372777178991008
    assert envelope["method"] == "black_scholes"
    assert envelope["option_type"] == "put"


def test_domain_error_returns_exit_code_two() -> None:
    code, out, err = _run(
        "powerlaw",
        "--option-type",
        "call",
        "--spot",
        "100",
        "--anchor-strike",
        "90",
        "--target-strike",
        "130",
        "--anchor-price",
        "5",
        "--alpha",
        "3",
    )
    assert code == 2
    assert out == ""
    assert "STRIKE_DOMAIN" in err
    assert "K1 must be greater than S0" in err
