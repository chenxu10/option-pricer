"""The versioned JSON contract shared by Python and the browser.

The contract is deliberately strict: a small, explicit wire format is easier
to test and to keep in sync than a permissive one.  Parsing only checks the
shape and the JSON types; the domain remains the authority on numeric rules.
"""

import json
import math
from collections.abc import Mapping
from typing import Any

from ..domain.errors import ErrorCode, PricingError
from ..domain.types import OptionType, PricingMethod
from .pricing import PricingResult
from .requests import BlackScholesRequest, PowerLawRequest, PricingRequest

CONTRACT_VERSION = "v1"

_POWER_LAW_FIELDS = frozenset(
    {
        "version",
        "method",
        "option_type",
        "spot",
        "anchor_strike",
        "target_strike",
        "anchor_price",
        "alpha",
    }
)
_BLACK_SCHOLES_FIELDS = frozenset(
    {
        "version",
        "method",
        "option_type",
        "spot",
        "strike",
        "time_to_expiry",
        "rate",
        "volatility",
    }
)


def parse_request(payload: str | Mapping[str, Any]) -> PricingRequest:
    """Parse a v1 request from a JSON string or an already-decoded mapping."""

    data = _decode(payload)

    version = data.get("version")
    if version is None:
        raise PricingError(
            ErrorCode.INVALID_REQUEST,
            "version is required.",
            "version",
        )
    if version != CONTRACT_VERSION:
        raise PricingError(
            ErrorCode.UNSUPPORTED_VERSION,
            f"unsupported contract version: {version!r}; expected {CONTRACT_VERSION!r}.",
            "version",
        )

    method = _method(data.get("method"))
    option_type = _option_type(data.get("option_type"))

    if method is PricingMethod.POWER_LAW:
        _require_exact_fields(data, _POWER_LAW_FIELDS)
        return PowerLawRequest(
            option_type=option_type,
            spot=_number(data, "spot"),
            anchor_strike=_number(data, "anchor_strike"),
            target_strike=_number(data, "target_strike"),
            anchor_price=_number(data, "anchor_price"),
            alpha=_number(data, "alpha"),
        )

    _require_exact_fields(data, _BLACK_SCHOLES_FIELDS)
    return BlackScholesRequest(
        option_type=option_type,
        spot=_number(data, "spot"),
        strike=_number(data, "strike"),
        time_to_expiry=_number(data, "time_to_expiry"),
        rate=_number(data, "rate"),
        volatility=_number(data, "volatility"),
    )


def serialize_result(result: PricingResult) -> str:
    """Serialize a successful result envelope."""

    return json.dumps(
        {
            "version": CONTRACT_VERSION,
            "ok": True,
            "price": result.price,
            "method": result.method.value,
            "option_type": result.option_type.value,
        },
        allow_nan=False,
        separators=(",", ":"),
    )


def serialize_error(error: PricingError) -> str:
    """Serialize a failure envelope."""

    return json.dumps(
        {
            "version": CONTRACT_VERSION,
            "ok": False,
            "error": {
                "code": error.code.value,
                "field": error.field,
                "message": error.message,
            },
        },
        allow_nan=False,
        separators=(",", ":"),
    )


def _decode(payload: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(payload, Mapping):
        return dict(payload)
    if not isinstance(payload, str):
        raise PricingError(
            ErrorCode.INVALID_REQUEST,
            "request payload must be a JSON object string.",
        )

    try:
        decoded = json.loads(
            payload,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except PricingError:
        raise
    except json.JSONDecodeError as exc:
        raise PricingError(
            ErrorCode.INVALID_REQUEST,
            f"invalid JSON: {exc.msg}.",
        ) from exc

    if not isinstance(decoded, dict):
        raise PricingError(
            ErrorCode.INVALID_REQUEST,
            "request payload must be a JSON object.",
        )
    return decoded


def _reject_json_constant(value: str) -> None:
    raise PricingError(
        ErrorCode.INVALID_REQUEST,
        f"invalid JSON constant: {value}.",
    )


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PricingError(
                ErrorCode.INVALID_REQUEST,
                f"duplicate field: {key}.",
                key,
            )
        result[key] = value
    return result


def _method(value: Any) -> PricingMethod:
    if value is None:
        raise PricingError(
            ErrorCode.INVALID_REQUEST,
            "method is required.",
            "method",
        )
    try:
        return PricingMethod(value)
    except (TypeError, ValueError) as exc:
        raise PricingError(
            ErrorCode.UNKNOWN_METHOD,
            "method must be 'power_law' or 'black_scholes'.",
            "method",
        ) from exc


def _option_type(value: Any) -> OptionType:
    if value is None:
        raise PricingError(
            ErrorCode.INVALID_REQUEST,
            "option_type is required.",
            "option_type",
        )
    try:
        return OptionType(value)
    except (TypeError, ValueError) as exc:
        raise PricingError(
            ErrorCode.UNKNOWN_OPTION_TYPE,
            "option_type must be 'call' or 'put'.",
            "option_type",
        ) from exc


def _require_exact_fields(data: Mapping[str, Any], expected: frozenset[str]) -> None:
    unknown = sorted(set(data) - expected)
    if unknown:
        field = unknown[0]
        raise PricingError(
            ErrorCode.INVALID_REQUEST,
            f"unknown field: {field}.",
            field,
        )

    missing = sorted(expected - set(data))
    if missing:
        field = missing[0]
        raise PricingError(
            ErrorCode.INVALID_REQUEST,
            f"missing field: {field}.",
            field,
        )


def _number(data: Mapping[str, Any], field: str) -> float:
    value = data[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PricingError(
            ErrorCode.INVALID_NUMBER,
            f"{field} must be a number.",
            field,
        )
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:  # pragma: no cover - defensive
        raise PricingError(
            ErrorCode.INVALID_NUMBER,
            f"{field} must be a number.",
            field,
        ) from exc
    if not math.isfinite(number):
        raise PricingError(
            ErrorCode.NON_FINITE_INPUT,
            f"{field} must be finite.",
            field,
        )
    return number
