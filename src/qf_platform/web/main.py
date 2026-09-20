"""Local entry point for the F4 Dash analytics workbench."""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false

from __future__ import annotations

import argparse

from .app import create_dash_app


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the local quant-finance Dash workbench."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    app = create_dash_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
