"""Renderer-neutral UI2 presentation from authoritative M2 execution evidence."""

from __future__ import annotations

from dataclasses import dataclass

from qf_platform.application.m2_workbench import (
    M2WorkbenchAnalysis,
    M2WorkbenchRequest,
    SensitivityRun,
    ValuationRun,
    WorkbenchValuationMethod,
)
from qf_platform.presentation.black_scholes import (
    PresentationRow,
    build_black_scholes_presentation,
)
from qf_platform.presentation.plotting import PlotData, PlotPoint, PlotSeries
from qf_platform.pricing import MonteCarloValuationResult
from qf_platform.sensitivity import BlackScholesSensitivity


@dataclass(frozen=True, slots=True)
class ValuationComparisonRow:
    """One row in the analytic/CRR/Monte Carlo comparison."""

    method: str
    configuration: str
    present_value: str
    difference: str
    evidence: str
    status: str


@dataclass(frozen=True, slots=True)
class GreekComparisonRow:
    """One row comparing analytic and finite-difference M2 sensitivity evidence."""

    greek: str
    analytic: str
    finite_difference: str
    difference: str
    units: str
    status: str


@dataclass(frozen=True, slots=True)
class M2WorkbenchPresentation:
    """Concrete UI2 presentation values; not quantitative authority."""

    compatibility_rows: tuple[PresentationRow, ...]
    result_rows: tuple[PresentationRow, ...]
    provenance_rows: tuple[PresentationRow, ...]
    valuation_rows: tuple[ValuationComparisonRow, ...]
    greek_rows: tuple[GreekComparisonRow, ...]
    finite_difference_rows: tuple[PresentationRow, ...]
    payoff_plot: PlotData
    crr_plot: PlotData
    monte_carlo_plot: PlotData
    greek_plot: PlotData


def build_m2_workbench_presentation(
    request: M2WorkbenchRequest,
    analysis: M2WorkbenchAnalysis,
) -> M2WorkbenchPresentation:
    """Convert completed M2 evidence into renderer-neutral UI values."""
    ui1 = build_black_scholes_presentation(request.composition)
    return M2WorkbenchPresentation(
        compatibility_rows=_compatibility_rows(request, analysis),
        result_rows=_result_rows(analysis.selected_valuation),
        provenance_rows=_provenance_rows(request),
        valuation_rows=_valuation_rows(analysis),
        greek_rows=_greek_rows(analysis),
        finite_difference_rows=_finite_difference_rows(request, analysis),
        payoff_plot=PlotData(
            title="Terminal payoff",
            x_label="Underlying at expiry",
            y_label="Payoff",
            series=(
                PlotSeries(
                    key="payoff",
                    label="Contract payoff",
                    points=tuple(
                        PlotPoint(point.underlying, point.payoff)
                        for point in ui1.payoff_points
                    ),
                ),
            ),
        ),
        crr_plot=_crr_plot(analysis),
        monte_carlo_plot=_monte_carlo_plot(analysis),
        greek_plot=_greek_plot(request, analysis),
    )


def _compatibility_rows(
    request: M2WorkbenchRequest,
    analysis: M2WorkbenchAnalysis,
) -> tuple[PresentationRow, ...]:
    selected = analysis.selected_valuation
    detail = "Capability is checked by the selected merged M2 method in Python."
    if selected.method is WorkbenchValuationMethod.CRR and not selected.supported:
        detail = (
            "Configured finite CRR tree is unsupported. M2 requires its "
            "one-step risk-neutral probability to satisfy 0 < p < 1."
        )
    return (
        PresentationRow(
            "Mathematically meaningful",
            "M1 Black-Scholes European-option pricing problem",
            (
                "The financial question is structurally composed before a method "
                "is chosen."
            ),
            "Ready",
        ),
        PresentationRow(
            "Implemented",
            "Analytic · CRR · Monte Carlo · five Black-Scholes Greeks",
            "Only capabilities already merged by M2 are exposed.",
            "Available",
        ),
        PresentationRow(
            "Selected method support",
            request.config.valuation_method.label,
            detail,
            "Supported" if selected.supported else "Unsupported",
        ),
        PresentationRow(
            "Validated",
            "M1 reference + M2 independent numerical/sensitivity evidence",
            "Discretization, sampling uncertainty, and finite-difference error differ.",
            "Reference evidence",
        ),
        PresentationRow(
            "Workbench exposed",
            "UI2 valuation comparison + sensitivity research surface",
            "Product exposure is not a claim of mathematical universality.",
            "Exposed",
        ),
    )


def _result_rows(selected: ValuationRun) -> tuple[PresentationRow, ...]:
    if selected.result is None:
        return (
            PresentationRow(
                "Selected valuation",
                selected.method.label,
                selected.configuration,
                "Unsupported",
            ),
        )
    result = selected.result
    rows = [
        PresentationRow(
            "Present value",
            f"{result.present_value:.12g}",
            "Immutable present value returned by the selected production method.",
            "Complete",
        ),
        PresentationRow(
            "Valuation method",
            selected.method.label,
            selected.configuration,
            "Complete",
        ),
    ]
    if isinstance(result, MonteCarloValuationResult):
        lower, upper = result.confidence_interval_95
        rows.extend(
            (
                PresentationRow(
                    "Monte Carlo standard error",
                    f"{result.standard_error:.8g}",
                    "Sampling uncertainty of the discounted-payoff sample mean.",
                    "Sampling evidence",
                ),
                PresentationRow(
                    "95% normal-approximation interval",
                    f"[{lower:.8g}, {upper:.8g}]",
                    "Estimate ± 1.959963984540054 × standard error.",
                    "Sampling evidence",
                ),
                PresentationRow(
                    "RNG provenance",
                    f"paths={result.paths}; seed={result.seed}",
                    "Fresh local Python RNG per evaluation; no stream-identity claim.",
                    "Reproducible",
                ),
            )
        )
    return tuple(rows)


def _provenance_rows(
    request: M2WorkbenchRequest,
) -> tuple[PresentationRow, ...]:
    problem = request.composition.problem
    fd = request.config.finite_difference_method
    return (
        PresentationRow(
            "Pricing inputs",
            (
                f"spot={problem.current_state.value.spot:g}; "
                f"vol={problem.parameters.annualized_volatility:g}"
            ),
            "Authoritative modeled inputs normalized through the UI1 M1 composition.",
            "Committed",
        ),
        PresentationRow(
            "Selected valuation",
            request.config.valuation_method.label,
            request.config.method_configuration,
            "Configured",
        ),
        PresentationRow(
            "Monte Carlo RNG",
            (
                f"paths={request.config.monte_carlo_paths}; "
                f"seed={request.config.monte_carlo_seed}"
            ),
            "Seed is reproducibility configuration, not a financial model parameter.",
            "Configured",
        ),
        PresentationRow(
            "Sensitivity method",
            "Analytic + central finite differences",
            (
                f"spot={fd.spot_bump:g}; vol={fd.volatility_bump:g}; "
                f"rate={fd.rate_bump:g}; theta_days={fd.theta_day_bump}"
            ),
            "Configured",
        ),
        PresentationRow(
            "Evidence semantics",
            "CRR approximation · MC sampling · finite-difference error",
            "The Workbench keeps distinct error mechanisms separately labeled.",
            "Explicit",
        ),
        PresentationRow(
            "Market observations",
            "No market-data provenance in UI2",
            "Observed quotes and provider provenance belong to M4.",
            "Not applicable",
        ),
    )


def _valuation_rows(
    analysis: M2WorkbenchAnalysis,
) -> tuple[ValuationComparisonRow, ...]:
    reference = next(
        run
        for run in analysis.valuations
        if run.method is WorkbenchValuationMethod.ANALYTIC
    )
    reference_value = (
        reference.result.present_value if reference.result is not None else None
    )
    return tuple(_valuation_row(run, reference_value) for run in analysis.valuations)


def _valuation_row(
    run: ValuationRun,
    reference_value: float | None,
) -> ValuationComparisonRow:
    if run.result is None:
        return ValuationComparisonRow(
            run.method.label,
            run.configuration,
            "—",
            "—",
            "Configured method does not support this pricing problem.",
            "Unsupported",
        )
    difference = (
        run.result.present_value - reference_value
        if reference_value is not None
        else None
    )
    evidence = "Deterministic analytical reference"
    if run.method is WorkbenchValuationMethod.CRR:
        evidence = "Finite-tree approximation/discretization evidence"
    elif isinstance(run.result, MonteCarloValuationResult):
        lower, upper = run.result.confidence_interval_95
        evidence = (
            f"SE = {run.result.standard_error:.6g}; 95% CI = [{lower:.6g}, {upper:.6g}]"
        )
    return ValuationComparisonRow(
        method=run.method.label,
        configuration=run.configuration,
        present_value=f"{run.result.present_value:.10g}",
        difference="—" if difference is None else f"{difference:+.6g}",
        evidence=evidence,
        status="Complete",
    )


def _greek_rows(
    analysis: M2WorkbenchAnalysis,
) -> tuple[GreekComparisonRow, ...]:
    return tuple(_greek_row(run) for run in analysis.sensitivities)


def _greek_row(run: SensitivityRun) -> GreekComparisonRow:
    analytic = run.analytic_result
    finite_difference = run.finite_difference_result
    difference = (
        finite_difference.value - analytic.value
        if analytic is not None and finite_difference is not None
        else None
    )
    metadata = analytic or finite_difference
    units = metadata.units if metadata is not None else run.sensitivity.units
    status = (
        "Compared"
        if analytic is not None and finite_difference is not None
        else "Partially supported"
    )
    return GreekComparisonRow(
        greek=run.sensitivity.value.title(),
        analytic="—" if analytic is None else f"{analytic.value:.10g}",
        finite_difference=(
            "—" if finite_difference is None else f"{finite_difference.value:.10g}"
        ),
        difference="—" if difference is None else f"{difference:+.6g}",
        units=units,
        status=status,
    )


def _finite_difference_rows(
    request: M2WorkbenchRequest,
    analysis: M2WorkbenchAnalysis,
) -> tuple[PresentationRow, ...]:
    fd = request.config.finite_difference_method
    rows: list[PresentationRow] = [
        PresentationRow(
            "Finite-difference bumps",
            (
                f"spot={fd.spot_bump:g}; vol={fd.volatility_bump:g}; "
                f"rate={fd.rate_bump:g}; theta_days={fd.theta_day_bump}"
            ),
            "Central differences use native M2 units; domain-crossing bumps reject.",
            "Configured",
        )
    ]
    gamma = next(
        run
        for run in analysis.sensitivities
        if run.sensitivity is BlackScholesSensitivity.GAMMA
    )
    analytic = gamma.analytic_result
    for point in analysis.gamma_bump_study:
        if point.result is None:
            rows.append(
                PresentationRow(
                    f"Gamma bump {point.spot_bump:g}",
                    "Unsupported",
                    "Configured central bump cannot be applied to this problem.",
                    "Unsupported",
                )
            )
            continue
        error = (
            abs(point.result.value - analytic.value) if analytic is not None else None
        )
        rows.append(
            PresentationRow(
                f"Gamma bump {point.spot_bump:g}",
                f"Gamma = {point.result.value:.10g}",
                (
                    "absolute error vs analytic = "
                    + ("—" if error is None else f"{error:.6g}")
                ),
                "Diagnostic",
            )
        )
    return tuple(rows)


def _crr_plot(analysis: M2WorkbenchAnalysis) -> PlotData:
    reference = next(
        run
        for run in analysis.valuations
        if run.method is WorkbenchValuationMethod.ANALYTIC
    )
    series: list[PlotSeries] = []
    crr_points = tuple(
        PlotPoint(float(point.steps), point.result.present_value)
        for point in analysis.crr_convergence
        if point.result is not None
    )
    if crr_points:
        series.append(PlotSeries("crr", "CRR", crr_points))
    if reference.result is not None and crr_points:
        value = reference.result.present_value
        series.append(
            PlotSeries(
                "analytic",
                "Analytic reference",
                tuple(PlotPoint(point.x, value) for point in crr_points),
            )
        )
    return PlotData("CRR convergence", "Tree steps", "Present value", tuple(series))


def _monte_carlo_plot(analysis: M2WorkbenchAnalysis) -> PlotData:
    points = tuple(
        PlotPoint(
            float(point.paths),
            point.result.present_value,
            lower=point.result.confidence_interval_95[0],
            upper=point.result.confidence_interval_95[1],
        )
        for point in analysis.monte_carlo_convergence
    )
    return PlotData(
        "Monte Carlo convergence and uncertainty",
        "Paths",
        "Present value",
        (PlotSeries("monte_carlo", "Monte Carlo 95% CI", points),),
    )


def _greek_plot(
    request: M2WorkbenchRequest,
    analysis: M2WorkbenchAnalysis,
) -> PlotData:
    analytic_points = tuple(
        PlotPoint(point.spot, point.analytic_result.value)
        for point in analysis.greek_curve
        if point.analytic_result is not None
    )
    fd_points = tuple(
        PlotPoint(point.spot, point.finite_difference_result.value)
        for point in analysis.greek_curve
        if point.finite_difference_result is not None
    )
    series: list[PlotSeries] = []
    if analytic_points:
        series.append(PlotSeries("analytic", "Analytic", analytic_points))
    if fd_points:
        series.append(PlotSeries("finite_difference", "Finite difference", fd_points))
    return PlotData(
        f"{request.config.selected_greek.value.title()} vs spot",
        "Spot",
        request.config.selected_greek.units,
        tuple(series),
    )
