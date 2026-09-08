"""Renderer-neutral UI3 presentation for merged M3 dynamic-hedging evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from qf_platform.application.ui3_hedging import (
    HedgeWorkbenchAnalysis,
    HedgeWorkbenchRequest,
)
from qf_platform.presentation.black_scholes import PresentationRow
from qf_platform.presentation.plotting import PlotData, PlotPoint, PlotSeries


@dataclass(frozen=True, slots=True)
class HedgeStepRow:
    """One authoritative rebalance row for native synchronized inspection."""

    time: str
    spot: str
    option_value: str
    stock_units: str
    trade_units: str
    cash_account: str
    hedge_value: str
    transaction_cost: str


@dataclass(frozen=True, slots=True)
class HedgeFrequencyRow:
    """Aggregate terminal-error evidence for one rebalance cadence."""

    cadence: str
    replicates: str
    mean_error: str
    error_standard_deviation: str
    mean_absolute_error: str
    root_mean_square_error: str


@dataclass(frozen=True, slots=True)
class HedgeWorkbenchPresentation:
    """Concrete UI3 hedging values; no control/accounting authority lives here."""

    inspector_rows: tuple[PresentationRow, ...]
    result_rows: tuple[PresentationRow, ...]
    aggregate_rows: tuple[PresentationRow, ...]
    provenance_rows: tuple[PresentationRow, ...]
    step_rows: tuple[HedgeStepRow, ...]
    frequency_rows: tuple[HedgeFrequencyRow, ...]
    underlying_plot: PlotData
    hedge_value_plot: PlotData
    delta_plot: PlotData
    cash_plot: PlotData
    frequency_plot: PlotData
    replicate_error_plot: PlotData


def build_hedge_workbench_presentation(
    request: HedgeWorkbenchRequest,
    analysis: HedgeWorkbenchAnalysis,
) -> HedgeWorkbenchPresentation:
    """Prepare display values from immutable M3 path-level and aggregate results."""

    result = analysis.selected_result
    terminal = result.terminal
    config = request.config
    frequency_rows = tuple(
        HedgeFrequencyRow(
            cadence=f"Every {point.rebalance_day_interval} day(s)",
            replicates=str(point.summary.replicate_count),
            mean_error=_number(point.summary.mean_error),
            error_standard_deviation=_number(point.summary.error_standard_deviation),
            mean_absolute_error=_number(point.summary.mean_absolute_error),
            root_mean_square_error=_number(point.summary.root_mean_square_error),
        )
        for point in analysis.frequency_evidence
    )
    return HedgeWorkbenchPresentation(
        inspector_rows=_inspector_rows(request, analysis),
        result_rows=(
            PresentationRow(
                "Terminal replication error",
                _number(terminal.replication_error),
                "Hedge value minus the terminal payoff of one short European option.",
                "Path evidence",
            ),
            PresentationRow(
                "Terminal hedge value",
                _number(terminal.hedge_value),
                "Terminal stock mark plus financed cash account.",
                "Path evidence",
            ),
            PresentationRow(
                "Terminal option payoff",
                _number(terminal.option_payoff),
                "Authoritative payoff from the existing European-option contract.",
                "Path evidence",
            ),
            PresentationRow(
                "Total transaction cost",
                _number(result.total_transaction_cost),
                "Explicit proportional stock-trade costs deducted from cash.",
                "Path evidence",
            ),
        ),
        aggregate_rows=_aggregate_rows(request, analysis),
        provenance_rows=(
            PresentationRow(
                "Selected path seed",
                str(result.seed),
                "M3 uses a fresh local RNG for exact-transition GBM sampling.",
                "Reproducible",
            ),
            PresentationRow(
                "Replicate seeds",
                ", ".join(str(seed) for seed in analysis.selected_summary.seeds),
                "Distinct seeds under one identical hedge study condition.",
                "Aggregate evidence",
            ),
            PresentationRow(
                "Observation grid",
                f"{analysis.selected_summary.path_observation_count} daily points",
                "Path observations are distinct from hedge rebalance dates.",
                "Configured",
            ),
            PresentationRow(
                "Generating / hedging volatility",
                f"{config.generating_volatility:g} / {config.hedging_volatility:g}",
                "Generating and hedge-assumed model parameters remain separate.",
                "Configured",
            ),
        ),
        step_rows=tuple(_step_row(step) for step in result.steps),
        frequency_rows=frequency_rows,
        underlying_plot=_underlying_plot(result.path.points[0].time, analysis),
        hedge_value_plot=_hedge_value_plot(result.path.points[0].time, analysis),
        delta_plot=_delta_plot(result.path.points[0].time, analysis),
        cash_plot=_cash_plot(result.path.points[0].time, analysis),
        frequency_plot=_frequency_plot(analysis),
        replicate_error_plot=_replicate_error_plot(analysis),
    )


def hedge_step_detail_rows(
    presentation: HedgeWorkbenchPresentation,
    index: int,
) -> tuple[PresentationRow, ...]:
    """Return already-presented values for one selected rebalance row."""

    if not 0 <= index < len(presentation.step_rows):
        return ()
    row = presentation.step_rows[index]
    return (
        PresentationRow("Date", row.time, "Selected rebalance date.", "Rebalance"),
        PresentationRow("Underlying", row.spot, "Modeled spot at this date.", "State"),
        PresentationRow(
            "Option value",
            row.option_value,
            "Black-Scholes value used by the authoritative M3 hedge evidence.",
            "Pricing",
        ),
        PresentationRow(
            "Target / realized stock units",
            row.stock_units,
            "M2 analytic Delta mapped through the M3 hedge policy.",
            "Control",
        ),
        PresentationRow(
            "Stock trade",
            row.trade_units,
            "Realized change in stock units at this rebalance.",
            "Action",
        ),
        PresentationRow(
            "Cash after rebalance",
            row.cash_account,
            "Money-market cash after financing, trade notional, and cost.",
            "Accounting",
        ),
        PresentationRow(
            "Hedge value after rebalance",
            row.hedge_value,
            "Stock plus cash after the realized action.",
            "Accounting",
        ),
        PresentationRow(
            "Transaction cost",
            row.transaction_cost,
            "Explicit cost for this stock trade.",
            "Cost",
        ),
    )


def _inspector_rows(
    request: HedgeWorkbenchRequest,
    analysis: HedgeWorkbenchAnalysis,
) -> tuple[PresentationRow, ...]:
    result = analysis.selected_result
    problem = result.problem
    return (
        PresentationRow(
            "State",
            "Equity spot along one model-generated path",
            "The selected path is modeled evidence, not an observed market history.",
            "M3",
        ),
        PresentationRow(
            "Generating law",
            "Exact-transition Black-Scholes GBM under Q^B",
            f"annualized volatility = {request.config.generating_volatility:g}",
            "M3",
        ),
        PresentationRow(
            "Sensitivity source",
            "M2 analytic Delta",
            "Delta is a sensitivity consumed by the policy; it is not the policy itself.",
            "M2 -> M3",
        ),
        PresentationRow(
            "Control policy",
            "Target underlying units = current analytic Delta",
            "The policy maps current modeled state to a target stock holding.",
            "M3",
        ),
        PresentationRow(
            "Rebalance schedule",
            f"{len(problem.rebalance_dates)} dates; every {request.config.rebalance_day_interval} day(s)",
            "Rebalance dates are a strict subset of the daily observation grid.",
            "M3",
        ),
        PresentationRow(
            "Financing / cost convention",
            f"money-market cash; kappa={request.config.transaction_cost_rate:g}",
            "M3 supports proportional stock-trade costs and zero continuous dividend yield.",
            "M3",
        ),
        PresentationRow(
            "Objective / error",
            "replication error = hedge value - option payoff",
            "One short European option; positive terminal error is surplus after settlement.",
            "M3",
        ),
    )


def _aggregate_rows(
    request: HedgeWorkbenchRequest,
    analysis: HedgeWorkbenchAnalysis,
) -> tuple[PresentationRow, ...]:
    selected = analysis.selected_summary
    correct = analysis.correctly_specified_summary
    frictionless = analysis.frictionless_summary
    return (
        PresentationRow(
            "Selected-condition RMSE",
            _number(selected.root_mean_square_error),
            f"{selected.replicate_count} distinct seeded paths; not one selected trajectory.",
            "Replicate evidence",
        ),
        PresentationRow(
            "Selected-condition mean absolute error",
            _number(selected.mean_absolute_error),
            "Aggregate absolute terminal replication discrepancy.",
            "Replicate evidence",
        ),
        PresentationRow(
            "Correct-volatility RMSE",
            _number(correct.root_mean_square_error),
            f"Generating and hedging volatility both {request.config.generating_volatility:g}; all else held fixed.",
            "Misspecification comparison",
        ),
        PresentationRow(
            "Frictionless RMSE",
            _number(frictionless.root_mean_square_error),
            "Same generating paths and hedge assumptions with transaction-cost rate set to zero.",
            "Cost comparison",
        ),
    )


def _step_row(step) -> HedgeStepRow:
    action = step.action
    return HedgeStepRow(
        time=step.time.isoformat(),
        spot=_number(step.spot),
        option_value=_number(step.option_value),
        stock_units=_number(action.target_underlying_units),
        trade_units=_number(action.trade_underlying_units),
        cash_account=_number(step.cash_after_rebalance),
        hedge_value=_number(step.portfolio_value_after_rebalance),
        transaction_cost=_number(action.transaction_cost),
    )


def _underlying_plot(origin: date, analysis: HedgeWorkbenchAnalysis) -> PlotData:
    points = tuple(
        PlotPoint(float((point.time - origin).days), point.spot)
        for point in analysis.selected_result.path.points
    )
    return PlotData(
        "Selected model-generated underlying path",
        "Days from valuation",
        "Spot",
        (PlotSeries("spot", "Underlying S_t", points),),
    )


def _hedge_value_plot(origin: date, analysis: HedgeWorkbenchAnalysis) -> PlotData:
    result = analysis.selected_result
    hedge_points = tuple(
        PlotPoint(
            float((step.time - origin).days),
            step.portfolio_value_after_rebalance,
        )
        for step in result.steps
    ) + (
        PlotPoint(
            float((result.terminal.time - origin).days),
            result.terminal.hedge_value,
        ),
    )
    option_points = tuple(
        PlotPoint(float((step.time - origin).days), step.option_value)
        for step in result.steps
    ) + (
        PlotPoint(
            float((result.terminal.time - origin).days),
            result.terminal.option_payoff,
        ),
    )
    return PlotData(
        "Hedge value vs option value/payoff",
        "Days from valuation",
        "Value",
        (
            PlotSeries("hedge", "Hedge portfolio", hedge_points),
            PlotSeries("option", "Option value / terminal payoff", option_points),
        ),
    )


def _delta_plot(origin: date, analysis: HedgeWorkbenchAnalysis) -> PlotData:
    points = tuple(
        PlotPoint(
            float((step.time - origin).days),
            step.action.target_underlying_units,
        )
        for step in analysis.selected_result.steps
    )
    return PlotData(
        "Delta hedge target / realized stock units",
        "Days from valuation",
        "Stock units",
        (PlotSeries("delta", "Target stock units", points),),
    )


def _cash_plot(origin: date, analysis: HedgeWorkbenchAnalysis) -> PlotData:
    result = analysis.selected_result
    points = tuple(
        PlotPoint(float((step.time - origin).days), step.cash_after_rebalance)
        for step in result.steps
    ) + (
        PlotPoint(
            float((result.terminal.time - origin).days),
            result.terminal.cash_account,
        ),
    )
    return PlotData(
        "Financed cash account",
        "Days from valuation",
        "Cash",
        (PlotSeries("cash", "Cash account", points),),
    )


def _frequency_plot(analysis: HedgeWorkbenchAnalysis) -> PlotData:
    ordered = sorted(
        analysis.frequency_evidence,
        key=lambda evidence: evidence.rebalance_day_interval,
    )
    return PlotData(
        "Replication error by rebalance cadence",
        "Days between rebalances",
        "Terminal error magnitude",
        (
            PlotSeries(
                "rmse",
                "RMSE",
                tuple(
                    PlotPoint(
                        float(point.rebalance_day_interval),
                        point.summary.root_mean_square_error,
                    )
                    for point in ordered
                ),
            ),
            PlotSeries(
                "mae",
                "Mean absolute error",
                tuple(
                    PlotPoint(
                        float(point.rebalance_day_interval),
                        point.summary.mean_absolute_error,
                    )
                    for point in ordered
                ),
            ),
        ),
    )


def _replicate_error_plot(analysis: HedgeWorkbenchAnalysis) -> PlotData:
    return PlotData(
        "Terminal replication errors across selected-condition replicates",
        "Seed",
        "Replication error",
        (
            PlotSeries(
                "replication_error",
                "Terminal error",
                tuple(
                    PlotPoint(float(point.seed), point.replication_error)
                    for point in analysis.selected_replicates
                ),
            ),
        ),
    )


def _number(value: float) -> str:
    return f"{value:.10g}"
