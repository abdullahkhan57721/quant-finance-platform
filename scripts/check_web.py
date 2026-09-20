#!/usr/bin/env python3
"""Construct and smoke the F4 Dash application without Qt or network access."""

from __future__ import annotations

import builtins

_original_import = builtins.__import__


def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if (
        name == "PySide6"
        or name.startswith("PySide6.")
        or name == "qf_platform.desktop"
        or name.startswith("qf_platform.desktop.")
    ):
        raise ImportError(f"forbidden desktop import during web smoke: {name}")
    return _original_import(name, globals, locals, fromlist, level)


builtins.__import__ = _guarded_import

from qf_platform.web import create_dash_app  # noqa: E402


def main() -> None:
    app = create_dash_app()
    client = app.server.test_client()

    root = client.get("/")
    if root.status_code != 200:
        raise SystemExit(f"Dash root returned {root.status_code}")

    layout = client.get("/_dash-layout")
    if layout.status_code != 200 or b"workspace-tabs" not in layout.data:
        raise SystemExit("Dash layout smoke failed")

    if len(app.callback_map) != 6:
        raise SystemExit(f"expected 6 F4 callbacks, found {len(app.callback_map)}")

    print("F4 web smoke passed: 6 workspaces/callback groups, no Qt import.")


if __name__ == "__main__":
    main()
