"""The v1 JSON contract is the only seam between Python and JavaScript."""

import json
from pathlib import Path
from typing import Any

import pytest

from option_pricer.adapters.web_bridge import contract_version, handle_request
from option_pricer.application.contract import (
    CONTRACT_VERSION,
    parse_request,
    serialize_error,
    serialize_result,
)
from option_pricer.application.pricing import price_option
from option_pricer.application.requests import BlackScholesRequest, PowerLawRequest
from option_pricer.domain.errors import ErrorCode, PricingError
from option_pricer.domain.types import OptionType

EXAMPLES = Path(__file__).resolve().parents[2] / "contracts" / "v1" / "examples"


def _valid_power_law_payload() -> dict[str, Any]:
    return {
        "version": "v1",
        "method": "power_law",
        "option_type": "call",
        "spot": 100.0,
        "anchor_strike": 120.0,
        "target_strike": 130.0,
        "anchor_price": 5.0,
        "alpha": 3.0,
    }


def _valid_bsm_payload() -> dict[str, Any]:
    return {
        "version": "v1",
        "method": "black_scholes",
        "option_type": "put",
        "spot": 100.0,
        "strike": 100.0,
        "time_to_expiry": 0.25,
        "rate": 0.05,
        "volatility": 0.2,
    }


def test_contract_version_matches_bridge() -> None:
    assert CONTRACT_VERSION == "v1"
    assert contract_version() == CONTRACT_VERSION


def test_parse_power_law_request() -> None:
    request = parse_request(json.dumps(_valid_power_law_payload()))
    assert isinstance(request, PowerLawRequest)
    assert request.option_type is OptionType.CALL
    assert request.alpha == 3.0


def test_parse_black_scholes_request() -> None:
    request = parse_request(_valid_bsm_payload())
    assert isinstance(request, BlackScholesRequest)
    assert request.option_type is OptionType.PUT


def test_fixture_round_trips() -> None:
    for fixture in sorted(EXAMPLES.glob("*.request.json")):
        payload = fixture.read_text()
        request = parse_request(payload)
        result = price_option(request)
        envelope = json.loads(serialize_result(result))
        assert envelope["ok"] is True
        assert envelope["version"] == CONTRACT_VERSION
        assert envelope["price"] == pytest.approx(result.price)


def test_valid_request_envelope_is_compact_json() -> None:
    envelope = json.loads(handle_request(json.dumps(_valid_power_law_payload())))
    assert envelope == {
        "version": "v1",
        "ok": True,
        "price": pytest.approx(2.2222222222222223),
        "method": "power_law",
        "option_type": "call",
    }


def test_domain_error_is_returned_as_an_envelope() -> None:
    payload = _valid_power_law_payload()
    payload["anchor_strike"] = 90.0
    envelope = json.loads(handle_request(json.dumps(payload)))
    assert envelope["ok"] is False
    assert envelope["error"]["code"] == "STRIKE_DOMAIN"
    assert envelope["error"]["field"] == "anchor_strike"
    assert envelope["error"]["message"]


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        ("", ErrorCode.INVALID_REQUEST),
        ("not json", ErrorCode.INVALID_REQUEST),
        ("[]", ErrorCode.INVALID_REQUEST),
        ("null", ErrorCode.INVALID_REQUEST),
        ('{"version":"v2"}', ErrorCode.UNSUPPORTED_VERSION),
        ('{"version":"v1"}', ErrorCode.INVALID_REQUEST),
        ('{"version":"v1","method":"bogus"}', ErrorCode.UNKNOWN_METHOD),
        (
            '{"version":"v1","method":"power_law","option_type":"bogus"}',
            ErrorCode.UNKNOWN_OPTION_TYPE,
        ),
        (
            '{"version":"v1","method":"power_law","option_type":"call",'
            '"spot":100,"anchor_strike":120,"target_strike":130,'
            '"anchor_price":5,"alpha":3,"extra":1}',
            ErrorCode.INVALID_REQUEST,
        ),
        (
            '{"version":"v1","method":"power_law","option_type":"call",'
            '"spot":100,"anchor_strike":120,"target_strike":130,'
            '"anchor_price":5,"alpha":3,"alpha":4}',
            ErrorCode.INVALID_REQUEST,
        ),
        (
            '{"version":"v1","method":"power_law","option_type":"call",'
            '"spot":100,"anchor_strike":120,"target_strike":130,'
            '"anchor_price":5,"alpha":NaN}',
            ErrorCode.INVALID_REQUEST,
        ),
        (
            '{"version":"v1","method":"power_law","option_type":"call",'
            '"spot":100,"anchor_strike":120,"target_strike":130,'
            '"anchor_price":5,"alpha":Infinity}',
            ErrorCode.INVALID_REQUEST,
        ),
        (
            '{"version":"v1","method":"power_law","option_type":"call",'
            '"spot":100,"anchor_strike":120,"target_strike":130,'
            '"anchor_price":5,"alpha":"3"}',
            ErrorCode.INVALID_NUMBER,
        ),
        (
            '{"version":"v1","method":"power_law","option_type":"call",'
            '"spot":100,"anchor_strike":120,"target_strike":130,'
            '"anchor_price":5,"alpha":true}',
            ErrorCode.INVALID_NUMBER,
        ),
        (
            '{"version":"v1","method":"power_law","option_type":"call",'
            '"spot":100,"anchor_strike":120,"target_strike":130,'
            '"alpha":3}',
            ErrorCode.INVALID_REQUEST,
        ),
        (
            '{"version":"v1","method":"black_scholes","option_type":"call",'
            '"spot":100,"strike":100,"time_to_expiry":0.25,"rate":0.05,'
            '"volatility":0.2,"anchor_strike":120}',
            ErrorCode.INVALID_REQUEST,
        ),
    ],
)
def test_invalid_payloads_return_typed_errors(payload: str, code: ErrorCode) -> None:
    envelope = json.loads(handle_request(payload))
    assert envelope["ok"] is False
    assert envelope["error"]["code"] == code.value


def test_serialize_error_includes_field_and_code() -> None:
    envelope = json.loads(
        serialize_error(PricingError(ErrorCode.ALPHA_OUT_OF_RANGE, "alpha must be greater than 1.", "alpha"))
    )
    assert envelope["error"]["field"] == "alpha"
    assert envelope["error"]["code"] == "ALPHA_OUT_OF_RANGE"


def test_parse_accepts_integers_as_numbers() -> None:
    payload = _valid_power_law_payload()
    payload["spot"] = 100
    payload["alpha"] = 3
    request = parse_request(payload)
    assert isinstance(request, PowerLawRequest)
    assert request.spot == 100.0
    assert request.alpha == 3.0
