"""Exercise installed public imports and scripts while rejecting frontend imports."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_EXAMPLES = _ROOT / "examples" / "research"

# AssertionError makes even an attempted optional import fail; this is stronger
# than checking sys.modules after imports or skipping if Qt is installed.
_PROBE = """
import importlib
import importlib.abc
import runpy
import sys

class RejectFrontend(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        roots = ('PySide6', 'qf_platform.desktop', 'dash', 'plotly',
                 'IPython', 'jupyter', 'openpyxl', 'pandas')
        if any(fullname == root or fullname.startswith(root + '.') for root in roots):
            raise AssertionError('Forbidden frontend import: ' + fullname)
        return None

sys.meta_path.insert(0, RejectFrontend())
for name in ('application', 'pricing', 'sensitivity', 'control', 'market_data',
             'inference', 'validation', 'presentation'):
    module = importlib.import_module('qf_platform.' + name)
    for public_name in module.__all__:
        assert hasattr(module, public_name), (name, public_name)
if sys.argv[1] == 'negative-control':
    importlib.import_module('PySide6')
else:
    runpy.run_path(sys.argv[1], run_name='__main__')
"""


@pytest.mark.parametrize("script", sorted(_EXAMPLES.glob("*.py")), ids=lambda p: p.stem)
def test_examples_run_without_frontend_imports_or_checkout_cwd(
    script: Path, tmp_path: Path
) -> None:
    completed = subprocess.run(
        [sys.executable, "-c", _PROBE, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip()


def test_probe_rejects_attempted_optional_import(tmp_path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, "-c", _PROBE, "negative-control"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode != 0
    assert "Forbidden frontend import: PySide6" in completed.stderr


def test_examples_use_package_public_imports_only() -> None:
    for script in _EXAMPLES.glob("*.py"):
        for node in ast.walk(ast.parse(script.read_text(encoding="utf-8"))):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith("qf_platform")
            ):
                assert node.module.count(".") == 1, (script, node.module)
                assert all(not item.name.startswith("_") for item in node.names)


def test_application_does_not_depend_on_presentation_or_downstream_clients() -> None:
    forbidden = ("qf_platform.presentation", "qf_platform.desktop", "examples")
    for path in (_ROOT / "src" / "qf_platform" / "application").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [item.name for item in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            for module in modules:
                assert not any(
                    module == prefix or module.startswith(prefix + ".")
                    for prefix in forbidden
                ), (path, module)
