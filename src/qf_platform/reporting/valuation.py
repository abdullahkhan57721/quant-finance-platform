"""Concrete tabular adapter for M2 valuation and Greek evidence."""

from __future__ import annotations

from qf_platform.application import M2WorkbenchAnalysis, M2WorkbenchRequest
from qf_platform.pricing import (
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    MonteCarloValuationResult,
)

from .model import ReportColumn, ReportField, ReportTable, ReportValue, TabularReport


def valuation_greeks_report(
    request: M2WorkbenchRequest,
    analysis: M2WorkbenchAnalysis,
) -> TabularReport:
    """Adapt existing M2 evidence without recalculating valuation or Greeks."""

    problem = request.composition.problem
    contract = problem.contract
    numeraire = problem.numeraire
    if not isinstance(contract, EuropeanOption):
        raise TypeError("M2 reporting requires a EuropeanOption contract")
    if not isinstance(numeraire, FlatMoneyMarketNumeraire):
        raise TypeError("M2 reporting requires a flat money-market numeraire")

    valuation_rows: list[tuple[ReportValue, ...]] = []
    for run in analysis.valuations:
        result = run.result
        standard_error = None
        ci_lower = None
        ci_upper = None
        paths = None
        seed = None
        if isinstance(result, MonteCarloValuationResult):
            standard_error = result.standard_error
            ci_lower, ci_upper = result.confidence_interval_95
            paths = result.paths
            seed = result.seed
        valuation_rows.append(
            (
                run.method.value,
                run.configuration,
                run.supported,
                result.present_value if result is not None else None,
                standard_error,
                ci_lower,
                ci_upper,
                paths,
                seed,
            )
        )

    greek_rows: list[tuple[ReportValue, ...]] = []
    for run in analysis.sensitivities:
        analytic = run.analytic_result
        finite_difference = run.finite_difference_result
        greek_rows.append(
            (
                run.sensitivity.value,
                analytic.value if analytic is not None else None,
                finite_difference.value if finite_difference is not None else None,
                run.sensitivity.units,
                run.analytic_supported,
                run.finite_difference_supported,
            )
        )

    return TabularReport(
        report_id="valuation_greeks",
        title="Black-Scholes valuation and Greeks comparison",
        metadata=(
            ReportField("valuation_date", problem.valuation_time.isoformat()),
            ReportField("spot", problem.current_state.value.spot, "spot units"),
            ReportField("strike", contract.strike, "spot units"),
            ReportField("expiry", contract.expiry.isoformat()),
            ReportField("option_right", contract.right.value),
            ReportField(
                "annualized_volatility",
                problem.parameters.annualized_volatility,
                "annual decimal",
            ),
            ReportField(
                "continuously_compounded_rate",
                numeraire.continuously_compounded_rate,
                "annual decimal",
            ),
            ReportField(
                "continuous_dividend_yield",
                problem.parameters.continuous_dividend_yield,
                "annual decimal",
            ),
            ReportField("pricing_measure", problem.pricing_measure.name),
            ReportField("day_count", "ACT/365F"),
            ReportField(
                "monte_carlo_seed",
                request.config.monte_carlo_seed,
                description="explicit production-owned RNG seed",
            ),
        ),
        tables=(
            ReportTable(
                "valuations",
                (
                    ReportColumn("method", "Method"),
                    ReportColumn("configuration", "Configuration"),
                    ReportColumn("supported", "Supported"),
                    ReportColumn("present_value", "Present value", "price units"),
                    ReportColumn("standard_error", "MC standard error", "price units"),
                    ReportColumn("ci95_lower", "MC 95% lower", "price units"),
                    ReportColumn("ci95_upper", "MC 95% upper", "price units"),
                    ReportColumn("paths", "MC paths", "count"),
                    ReportColumn("seed", "MC seed"),
                ),
                tuple(valuation_rows),
            ),
            ReportTable(
                "greeks",
                (
                    ReportColumn("greek", "Greek"),
                    ReportColumn("analytic", "Analytic value"),
                    ReportColumn("finite_difference", "Finite-difference value"),
                    ReportColumn("units", "Native units"),
                    ReportColumn("analytic_supported", "Analytic supported"),
                    ReportColumn("fd_supported", "Finite difference supported"),
                ),
                tuple(greek_rows),
            ),
            ReportTable(
                "crr_convergence",
                (
                    ReportColumn("steps", "CRR steps", "count"),
                    ReportColumn("supported", "Supported"),
                    ReportColumn("present_value", "Present value", "price units"),
                ),
                tuple(
                    (
                        point.steps,
                        point.supported,
                        point.result.present_value
                        if point.result is not None
                        else None,
                    )
                    for point in analysis.crr_convergence
                ),
            ),
            ReportTable(
                "mc_convergence",
                (
                    ReportColumn("paths", "Paths", "count"),
                    ReportColumn("present_value", "Present value", "price units"),
                    ReportColumn("standard_error", "Standard error", "price units"),
                    ReportColumn("ci95_lower", "95% lower", "price units"),
                    ReportColumn("ci95_upper", "95% upper", "price units"),
                    ReportColumn("seed", "Seed"),
                ),
                tuple(
                    (
                        point.paths,
                        point.result.present_value,
                        point.result.standard_error,
                        point.result.confidence_interval_95[0],
                        point.result.confidence_interval_95[1],
                        point.result.seed,
                    )
                    for point in analysis.monte_carlo_convergence
                ),
            ),
        ),
    )
