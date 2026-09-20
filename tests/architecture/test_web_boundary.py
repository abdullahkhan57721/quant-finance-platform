"""Dependency contracts for the F4 Dash/Plotly sibling client."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_WEB = _ROOT / "src" / "qf_platform" / "web"
_FORBIDDEN_IMPORT_ROOTS = (
    "PySide6",
    "httpx",
    "qf_platform.control",
    "qf_platform.desktop",
    "qf_platform.inference",
    "qf_platform.market_data",
    "qf_platform.pricing",
    "qf_platform.sensitivity",
    "qf_platform.validation",
    "requests",
    "socket",
    "urllib",
)


def test_web_layer_stays_downstream_of_application_and_presentation() -> None:
    for path in sorted(_WEB.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = tuple(item.name for item in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = (node.module,)
            else:
                continue
            assert not any(
                module == root or module.startswith(root + ".")
                for module in modules
                for root in _FORBIDDEN_IMPORT_ROOTS
            ), (path, modules)


def test_services_do_not_import_renderer_frameworks() -> None:
    tree = ast.parse((_WEB / "services.py").read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(item.name for item in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    assert not any(
        module == root or module.startswith(root + ".")
        for module in modules
        for root in ("dash", "flask", "plotly")
    )


def test_base_application_import_does_not_require_web_dependencies() -> None:
    code = r"""
import builtins

original_import = builtins.__import__


def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "dash" or name.startswith("dash.") or name == "plotly" or name.startswith("plotly."):
        raise ImportError("web dependency intentionally unavailable")
    return original_import(name, globals, locals, fromlist, level)


builtins.__import__ = guarded_import
import qf_platform.application
import qf_platform.reporting
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
