"""Static contracts for the F2 flagship research notebooks."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import cast

_ROOT = Path(__file__).resolve().parents[2]
_NOTEBOOK_DIR = _ROOT / "notebooks"
_EXPECTED = (
    "01_pricing_numerical_methods_and_greeks.ipynb",
    "02_dynamic_delta_hedging_and_model_risk.ipynb",
    "03_spx_heston_calibration_and_validation.ipynb",
)


def _load(path: Path) -> dict[str, object]:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return cast(dict[str, object], value)


def _cells(path: Path) -> list[dict[str, object]]:
    notebook = _load(path)
    raw_cells = cast(list[object], notebook["cells"])
    cells: list[dict[str, object]] = []
    for raw_cell in raw_cells:
        assert isinstance(raw_cell, dict)
        cells.append(cast(dict[str, object], raw_cell))
    return cells


def _source(cell: dict[str, object]) -> str:
    raw_source = cell.get("source", "")
    if isinstance(raw_source, str):
        return raw_source
    assert isinstance(raw_source, list)
    lines = cast(list[object], raw_source)
    assert all(isinstance(line, str) for line in lines)
    return "".join(cast(list[str], lines))


def test_exact_flagship_notebook_set_is_committed() -> None:
    names = tuple(path.name for path in sorted(_NOTEBOOK_DIR.glob("*.ipynb")))
    assert names == _EXPECTED


def test_committed_notebooks_are_output_free() -> None:
    for name in _EXPECTED:
        for cell in _cells(_NOTEBOOK_DIR / name):
            if cell.get("cell_type") != "code":
                continue
            assert cell.get("execution_count") is None
            assert cell.get("outputs") == []


def test_notebooks_use_only_public_platform_imports_and_no_network_clients() -> None:
    forbidden_roots = {
        "dash",
        "httpx",
        "plotly",
        "qf_platform.desktop",
        "requests",
        "socket",
        "urllib",
    }
    for name in _EXPECTED:
        for cell in _cells(_NOTEBOOK_DIR / name):
            if cell.get("cell_type") != "code":
                continue
            tree = ast.parse(_source(cell))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [item.name for item in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules = [node.module]
                    if node.module.startswith("qf_platform"):
                        assert node.module.count(".") == 1, (name, node.module)
                        assert all(not item.name.startswith("_") for item in node.names)
                for module in modules:
                    assert not any(
                        module == root or module.startswith(root + ".")
                        for root in forbidden_roots
                    ), (name, module)


def test_validation_notebook_keeps_m7_claims_bounded() -> None:
    path = _NOTEBOOK_DIR / "03_spx_heston_calibration_and_validation.ipynb"
    text = "\n".join(_source(cell) for cell in _cells(path)).lower()
    assert "same-date cross-sectional" in text
    assert "not temporal out-of-sample forecasting" in text
    assert "not a historical trading-profit result" in text
    assert "not evidence of heston hedge superiority" in text


def test_hedging_notebook_keeps_model_generated_boundary_visible() -> None:
    path = _NOTEBOOK_DIR / "02_dynamic_delta_hedging_and_model_risk.ipynb"
    text = "\n".join(_source(cell) for cell in _cells(path)).lower()
    assert "model-generated pricing-measure paths" in text
    assert "not a historical backtest" in text
    assert "not historical trading profitability" in text
