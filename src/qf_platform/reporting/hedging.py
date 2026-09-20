"""Concrete tabular adapter for M3 dynamic-hedging evidence."""

from __future__ import annotations

from qf_platform.application import HedgeWorkbenchAnalysis, HedgeWorkbenchRequest
from qf_platform.control import ReplicationErrorSummary

from .model import ReportColumn, ReportField, ReportTable, ReportValue, TabularReport


def _summary_row(
    label: str,
    summary: ReplicationErrorSummary,
) -> tuple[ReportValue, ...]:
    return (
        label,
        summary.replicate_count,
        summary.generating_annualized_volatility,
        summary.hedging_annualized_volatility,
        summary.proportional_transaction_cost_rate,
        summary.mean_error,
        summary.median_error,
        summary.error_standard_deviation,
        summary.mean_absolute_error,
        summary.root_mean_square_error,
    )


def hedging_report(
    request: HedgeWorkbenchRequest,
    analysis: HedgeWorkbenchAnalysis,
) -> TabularReport:
    """Adapt model-generated replication evidence without rerunning a hedge."""

    config = request.config
    return TabularReport(
        report_id="dynamic_delta_hedging",
        title="Dynamic Black-Scholes Delta hedging evidence",
        metadata=(
            ReportField("evidence_kind", "model-generated replication experiment"),
            ReportField("historical_backtest", False),
            ReportField("pricing_measure_paths", True),
            ReportField(
                "generating_annualized_volatility",
                config.generating_volatility,
                "annual decimal",
            ),
            ReportField(
                "hedging_annualized_volatility",
                config.hedging_volatility,
                "annual decimal",
            ),
            ReportField("rebalance_day_interval", config.rebalance_day_interval, "days"),
            ReportField("seed", config.seed),
            ReportField("replicate_count", config.replicate_count, "count"),
            ReportField(
                "transaction_cost_rate",
                config.transaction_cost_rate,
                "proportion of stock-trade notional",
            ),
            ReportField(
                "non_claim",
                "not historical trading profitability or physical-measure forecasting",
            ),
        ),
        tables=(
            ReportTable(
                "summaries",
                (
                    ReportColumn("condition", "Condition"),
                    ReportColumn("replicates", "Replicates", "count"),
                    ReportColumn(
                        "generating_vol",
                        "Generating volatility",
                        "annual decimal",
                    ),
                    ReportColumn(
                        "hedging_vol",
                        "Hedging volatility",
                        "annual decimal",
                    ),
                    ReportColumn("cost_rate", "Transaction cost rate", "proportion"),
                    ReportColumn("mean_error", "Mean error", "price units"),
                    ReportColumn("median_error", "Median error", "price units"),
                    ReportColumn(
                        "error_std",
                        "Error standard deviation",
                        "price units",
                    ),
                    ReportColumn("mae", "Mean absolute error", "price units"),
                    ReportColumn("rmse", "Root mean square error", "price units"),
                ),
                (
                    _summary_row("selected", analysis.selected_summary),
                    _summary_row(
                        "correctly_specified",
                        analysis.correctly_specified_summary,
                    ),
                    _summary_row("frictionless", analysis.frictionless_summary),
                ),
            ),
            ReportTable(
                "replicates",
                (
                    ReportColumn("seed", "Seed"),
                    ReportColumn(
                        "replication_error",
                        "Terminal replication error",
                        "price units",
                    ),
                    ReportColumn(
                        "transaction_cost",
                        "Total transaction cost",
                        "price units",
                    ),
                ),
                tuple(
                    (item.seed, item.replication_error, item.total_transaction_cost)
                    for item in analysis.selected_replicates
                ),
            ),
            ReportTable(
                "frequency",
                (
                    ReportColumn("rebalance_days", "Rebalance interval", "days"),
                    ReportColumn("mean_error", "Mean error", "price units"),
                    ReportColumn("mae", "Mean absolute error", "price units"),
                    ReportColumn("rmse", "Root mean square error", "price units"),
                ),
                tuple(
                    (
                        item.rebalance_day_interval,
                        item.summary.mean_error,
                        item.summary.mean_absolute_error,
                        item.summary.root_mean_square_error,
                    )
                    for item in analysis.frequency_evidence
                ),
            ),
        ),
    )
