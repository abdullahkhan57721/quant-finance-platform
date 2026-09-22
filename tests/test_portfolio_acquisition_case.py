from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "docs" / "portfolio" / "acquisition_valuation_case"
NOTEBOOK_PATH = ROOT / "notebooks" / "04_acquisition_earnout_analysis.ipynb"


def test_acquisition_case_documentation_exists() -> None:
    readme = CASE_DIR / "README.md"
    assert readme.is_file()
    text = readme.read_text()
    assert "TargetCo acquisition valuation case" in text
    assert "BlackScholesClosedForm" in text
    assert "MonteCarloEuropeanOption" in text


def test_earnout_notebook_is_output_free_and_uses_platform_pricing() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text())
    source = "\n".join(
        "".join(cell.get("source", ""))
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )
    assert "BlackScholesClosedForm" in source
    assert "MonteCarloEuropeanOption" in source
    assert "PricingProblem" in source
    assert "def make_call_problem" in source

    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell["execution_count"] is None
            assert cell["outputs"] == []
