"""Backward-compatible entry point for the CLI."""

from option_pricer.adapters.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
