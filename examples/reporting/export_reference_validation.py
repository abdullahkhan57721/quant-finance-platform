"""Generate the flagship validation report in XLSX, CSV, and JSON formats."""

from __future__ import annotations

import argparse
from pathlib import Path

from qf_platform.application import (
    canonical_m8_performance_reference,
    make_ui5_reference_validation_request,
    run_ui5_validation,
)
from qf_platform.reporting import export_report, validation_model_risk_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reporting_output"))
    args = parser.parse_args()

    request = make_ui5_reference_validation_request()
    analysis = run_ui5_validation(request)
    report = validation_model_risk_report(
        request,
        analysis,
        performance=canonical_m8_performance_reference(),
    )
    paths = export_report(report, args.output)
    print(paths.xlsx)
    print(paths.json)
    for path in paths.csv:
        print(path)


if __name__ == "__main__":
    main()
