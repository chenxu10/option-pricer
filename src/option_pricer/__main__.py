"""Allow ``python -m option_pricer ...``."""

from .adapters.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
