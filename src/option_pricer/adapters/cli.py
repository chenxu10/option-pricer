"""Command-line adapter for the pricing model.

The CLI is a peer of the web UI: it parses arguments, builds a typed request,
calls the application use case, and formats the result.  It contains no
formulas and no validation rules of its own.
"""

import argparse
import sys
from collections.abc import Sequence
from typing import TextIO

from ..application.contract import serialize_result
from ..application.pricing import price_option
from ..application.requests import BlackScholesRequest, PowerLawRequest, PricingRequest
from ..domain.errors import PricingError
from ..domain.types import OptionType, PricingMethod
from ..version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="option-pricer",
        description="Price European options with power-law tail extrapolation or BSM.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    power_law = subparsers.add_parser(
        "powerlaw",
        help="Taleb-style power-law extrapolation from an anchor strike.",
    )
    power_law.add_argument("--option-type", choices=("call", "put"), required=True)
    power_law.add_argument("--spot", type=float, required=True, help="S0, the current underlying price")
    power_law.add_argument("--anchor-strike", type=float, required=True, help="K1")
    power_law.add_argument("--target-strike", type=float, required=True, help="K2")
    power_law.add_argument("--anchor-price", type=float, required=True, help="C(K1) or P(K1)")
    power_law.add_argument("--alpha", type=float, required=True, help="tail index, alpha > 1")
    power_law.add_argument("--json", action="store_true", help="print the v1 JSON response envelope")

    bsm = subparsers.add_parser("bsm", help="Black-Scholes-Merton European pricing.")
    bsm.add_argument("--option-type", choices=("call", "put"), required=True)
    bsm.add_argument("--spot", type=float, required=True, help="S, the current underlying price")
    bsm.add_argument("--strike", type=float, required=True, help="K")
    bsm.add_argument("--time", type=float, required=True, help="T, time to expiry in years")
    bsm.add_argument("--rate", type=float, required=True, help="r, continuously compounded risk-free rate")
    bsm.add_argument("--vol", type=float, required=True, help="sigma, annualised volatility")
    bsm.add_argument("--json", action="store_true", help="print the v1 JSON response envelope")

    return parser


def main(
    argv: Sequence[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the CLI.  Returns a process exit code (0 success, 2 user error)."""

    out = stdout if stdout is not None else sys.stdout
    err = stderr if stderr is not None else sys.stderr
    args = build_parser().parse_args(argv)

    option_type = OptionType(args.option_type)
    request: PricingRequest
    if args.command == "powerlaw":
        request = PowerLawRequest(
            option_type=option_type,
            spot=args.spot,
            anchor_strike=args.anchor_strike,
            target_strike=args.target_strike,
            anchor_price=args.anchor_price,
            alpha=args.alpha,
        )
    else:
        request = BlackScholesRequest(
            option_type=option_type,
            spot=args.spot,
            strike=args.strike,
            time_to_expiry=args.time,
            rate=args.rate,
            volatility=args.vol,
        )

    try:
        result = price_option(request)
    except PricingError as exc:
        print(f"error [{exc.code}]: {exc.message}", file=err)
        return 2

    if args.json:
        print(serialize_result(result), file=out)
    else:
        print(f"{_label(result.method, result.option_type)} = {result.price:.6f}", file=out)
    return 0


def _label(method: PricingMethod, option_type: OptionType) -> str:
    if method is PricingMethod.POWER_LAW:
        return "C(K2)" if option_type is OptionType.CALL else "P(K2)"
    return "BSM call" if option_type is OptionType.CALL else "BSM put"
