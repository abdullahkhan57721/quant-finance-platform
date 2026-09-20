"""Concrete tabular adapter for M6 Heston calibration evidence."""

from __future__ import annotations

from qf_platform.application import (
    HestonCalibrationWorkbenchAnalysis,
    HestonCalibrationWorkbenchRequest,
)

from .model import ReportColumn, ReportField, ReportTable, TabularReport

_PARAMETER_NAMES = ("v0", "kappa", "theta", "xi", "rho")


def heston_calibration_report(
    request: HestonCalibrationWorkbenchRequest,
    analysis: HestonCalibrationWorkbenchAnalysis,
) -> TabularReport:
    """Adapt completed M6 calibration/conditioning evidence without optimization."""

    run_rows = []
    residual_rows = []
    conditioning_rows = []
    for run in analysis.runs:
        result = run.result
        estimate = result.estimate.as_vector()
        start = run.initial_guess.as_vector()
        run_rows.append(
            (
                run.label,
                *start,
                *estimate,
                result.objective_value,
                result.function_evaluations,
                result.jacobian_evaluations,
                result.termination_status,
                result.optimizer_name,
            )
        )
        for residual in result.residuals:
            contract = residual.target.contract
            residual_rows.append(
                (
                    run.label,
                    residual.target.label,
                    contract.expiry.isoformat(),
                    contract.strike,
                    contract.right.value,
                    residual.target.target_price,
                    residual.model_price,
                    residual.residual,
                    residual.residual_scale,
                    residual.standardized_residual,
                )
            )
        conditioning = result.conditioning
        conditioning_rows.append(
            (
                run.label,
                conditioning.jacobian_rank,
                conditioning.parameter_count,
                conditioning.target_count,
                conditioning.rank_deficient,
                conditioning.condition_number,
                ", ".join(str(value) for value in conditioning.singular_values),
            )
        )

    truth = analysis.truth.as_vector()
    return TabularReport(
        report_id="heston_calibration",
        title="Heston calibration and local identifiability evidence",
        metadata=(
            ReportField("mode", analysis.mode),
            ReportField("valuation_date", analysis.problem.valuation_date.isoformat()),
            ReportField("spot", analysis.problem.spot, "spot units"),
            ReportField("weighting", analysis.problem.weighting.value),
            ReportField("target_count", len(analysis.problem.targets), "count"),
            ReportField(
                "max_function_evaluations",
                request.max_function_evaluations,
                "count",
            ),
            ReportField("fourier_intervals", request.fourier_intervals, "count"),
            ReportField(
                "calibration_interpretation",
                "optimizer convergence and low loss do not imply parameter identification",
            ),
        ),
        tables=(
            ReportTable(
                "truth",
                (
                    ReportColumn("parameter", "Parameter"),
                    ReportColumn("value", "Truth value"),
                ),
                tuple(zip(_PARAMETER_NAMES, truth, strict=True)),
            ),
            ReportTable(
                "calibration_runs",
                (
                    ReportColumn("label", "Start label"),
                    *(
                        ReportColumn(f"start_{name}", f"Start {name}")
                        for name in _PARAMETER_NAMES
                    ),
                    *(
                        ReportColumn(f"estimate_{name}", f"Estimate {name}")
                        for name in _PARAMETER_NAMES
                    ),
                    ReportColumn("objective", "Objective value"),
                    ReportColumn(
                        "function_evaluations",
                        "Function evaluations",
                        "count",
                    ),
                    ReportColumn(
                        "jacobian_evaluations",
                        "Jacobian evaluations",
                        "count",
                    ),
                    ReportColumn("termination_status", "Termination status"),
                    ReportColumn("optimizer", "Optimizer"),
                ),
                tuple(run_rows),
            ),
            ReportTable(
                "residuals",
                (
                    ReportColumn("run", "Run"),
                    ReportColumn("target", "Target"),
                    ReportColumn("expiry", "Expiry"),
                    ReportColumn("strike", "Strike", "spot units"),
                    ReportColumn("right", "Right"),
                    ReportColumn("target_price", "Target price", "price units"),
                    ReportColumn("model_price", "Model price", "price units"),
                    ReportColumn("residual", "Residual", "price units"),
                    ReportColumn("residual_scale", "Residual scale", "price units"),
                    ReportColumn(
                        "standardized_residual",
                        "Standardized residual",
                    ),
                ),
                tuple(residual_rows),
            ),
            ReportTable(
                "conditioning",
                (
                    ReportColumn("run", "Run"),
                    ReportColumn("jacobian_rank", "Jacobian rank", "count"),
                    ReportColumn("parameter_count", "Parameter count", "count"),
                    ReportColumn("target_count", "Target count", "count"),
                    ReportColumn("rank_deficient", "Rank deficient"),
                    ReportColumn("condition_number", "Condition number"),
                    ReportColumn("singular_values", "Singular values"),
                ),
                tuple(conditioning_rows),
            ),
        ),
    )
