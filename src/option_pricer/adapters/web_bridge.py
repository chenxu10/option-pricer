"""Python side of the browser bridge.

The JavaScript worker imports this module and calls ``handle_request`` with a
JSON string.  This function is the only Python entry point the browser needs;
it never raises for bad user input, returning a v1 error envelope instead.
"""

import traceback

from ..application.contract import (
    CONTRACT_VERSION,
    parse_request,
    serialize_error,
    serialize_result,
)
from ..application.pricing import price_option
from ..domain.errors import ErrorCode, PricingError


def contract_version() -> str:
    """Expose the contract version to the worker for a startup sanity check."""

    return CONTRACT_VERSION


def handle_request(payload: str) -> str:
    """Price one JSON request and return a JSON response envelope."""

    try:
        request = parse_request(payload)
        result = price_option(request)
        return serialize_result(result)
    except PricingError as exc:
        return serialize_error(exc)
    except Exception:  # pragma: no cover - defensive boundary
        traceback.print_exc()
        return serialize_error(
            PricingError(
                ErrorCode.INTERNAL_ERROR,
                "An internal error occurred while pricing the option.",
            )
        )
