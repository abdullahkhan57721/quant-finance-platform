"""Dependency-direction contracts for the F3 reporting layer."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_REPORTING = _ROOT / "src" / "qf_platform" / "reporting"
_FORBIDDEN_ROOTS = (
    "dash",
    "matplotlib",
    "numpy",
    "plotly",
    "qf_platform.desktop",
    "qf_platform.presentation",
    "scipy",
)
_FORBIDDEN_CALCULATION_IMPORTS = {
    "calibrate_heston",
    "evaluate",
    "evaluate_sensitivity",
    "infer_implied_volatility",
    "run_delta_hedge",
    "run_hedge_workbench",
    "run_heston_calibration",
    "run_heston_pricing",
    "run_m2_workbench",
    "run_market_workbench",
    "run_ui5_validation",
}


def test_reporting_stays_downstream_of_authoritative_results() -> None:
    for path in sorted(_REPORTING.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = tuple(item.name for item in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = (node.module,)
                if node.module.startswith("qf_platform"):
                    assert not (
                        {item.name for item in node.names}
                        & _FORBIDDEN_CALCULATION_IMPORTS
                    ), path
            else:
                continue
            assert not any(
                module == root or module.startswith(root + ".")
                for module in modules
                for root in _FORBIDDEN_ROOTS
            ), (path, modules)


def test_base_reporting_import_does_not_require_openpyxl() -> None:
    code = r"""
import builtins
from pathlib import Path
from tempfile import TemporaryDirectory

original_import = builtins.__import__


def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "openpyxl" or name.startswith("openpyxl."):
        raise ImportError("openpyxl intentionally unavailable")
    return original_import(name, globals, locals, fromlist, level)


builtins.__import__ = guarded_import
from qf_platform.reporting import (
    ReportColumn,
    ReportField,
    ReportTable,
    TabularReport,
    write_csv_report,
    write_json_report,
)

report = TabularReport(
    report_id="probe",
    title="probe",
    metadata=(ReportField("source", "test"),),
    tables=(
        ReportTable(
            "values",
            (ReportColumn("value", "Value"),),
            ((1.0,),),
        ),
    ),
)
with TemporaryDirectory() as raw_directory:
    directory = Path(raw_directory)
    write_json_report(report, directory / "probe.json")
    write_csv_report(report, directory / "csv")
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
