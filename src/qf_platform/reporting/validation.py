"""Flagship tabular adapter for M7 model-validation and M8 performance evidence."""

from __future__ import annotations

from qf_platform.application import (
    UI5PerformanceReference,
    UI5ValidationAnalysis,
    UI5ValidationRequest,
)
from qf_platform.market_data import NormalizedOptionObservation
from qf_platform.validation import HestonStartEvidence, ValidationMetrics

from .model import ReportColumn, ReportField, ReportTable, ReportValue, TabularReport

_PARAMETER_NAMES = ("v0", "kappa", "theta", "xi", "rho")


def _metrics_row(
    model: str,
    metrics: ValidationMetrics,
) -> tuple[ReportValue, ...]:
    return (
        model,
        metrics.observation_count,
        metrics.mean_residual,
        metrics.mean_absolute_error,
        metrics.root_mean_square_error,
        metrics.relative_mean_absolute_error,
        metrics.standardized_mean_absolute_error,
        metrics.standardized_root_mean_square_error,
        metrics.maximum_absolute_standardized_residual,
    )


def _metrics_table(
    name: str,
    black_scholes: ValidationMetrics,
    heston: ValidationMetrics,
) -> ReportTable:
    return ReportTable(
        name,
        (
            ReportColumn("model", "Model"),
            ReportColumn("observations", "Observations", "count"),
            ReportColumn("mean_residual", "Mean residual", "price units"),
            ReportColumn("mae", "Mean absolute error", "price units"),
            ReportColumn("rmse", "Root mean square error", "price units"),
            ReportColumn(
                "relative_mae",
                "Relative mean absolute error",
                "fraction",
            ),
            ReportColumn("std_mae", "Standardized mean absolute error"),
            ReportColumn("std_rmse", "Standardized root mean square error"),
            ReportColumn(
                "max_abs_std_residual",
                "Maximum absolute standardized residual",
            ),
        ),
        (
            _metrics_row("black_scholes", black_scholes),
            _metrics_row("heston", heston),
        ),
    )


def _contract_table(
    name: str,
    observations: tuple[NormalizedOptionObservation, ...],
) -> ReportTable:
    return ReportTable(
        name,
        (
            ReportColumn("contract_id", "Contract ID"),
            ReportColumn("expiry", "Expiry"),
            ReportColumn("strike", "Strike", "spot units"),
            ReportColumn("right", "Right"),
            ReportColumn("bid", "Bid", "price units"),
            ReportColumn("ask", "Ask", "price units"),
            ReportColumn(
                "target_price",
                "Normalized midpoint target",
                "price units",
            ),
            ReportColumn("spot", "Observed spot", "spot units"),
            ReportColumn("normalization_version", "Normalization version"),
        ),
        tuple(
            (
                observation.raw_quote.contract_id,
                observation.raw_quote.expiry.isoformat(),
                observation.raw_quote.strike,
                observation.raw_quote.right.value,
                observation.raw_quote.bid,
                observation.raw_quote.ask,
                observation.target_price,
                observation.spot,
                observation.normalization_version,
            )
            for observation in observations
        ),
    )


def _start_rows(
    phase: str,
    starts: tuple[HestonStartEvidence, ...],
) -> tuple[tuple[ReportValue, ...], ...]:
    rows = []
    for index, start in enumerate(starts, start=1):
        initial = start.initial_guess.as_vector()
        result = start.result
        estimate = result.estimate.as_vector() if result is not None else (None,) * 5
        rows.append(
            (
                phase,
                index,
                *initial,
                start.converged,
                result.objective_value if result is not None else None,
                *estimate,
                result.function_evaluations if result is not None else None,
                result.jacobian_evaluations if result is not None else None,
                start.failure_message,
            )
        )
    return tuple(rows)


def validation_model_risk_report(
    request: UI5ValidationRequest,
    analysis: UI5ValidationAnalysis,
    *,
    performance: UI5PerformanceReference | None = None,
) -> TabularReport:
    """Build the flagship validation report from immutable M7/M8 evidence only."""

    evidence = analysis.evidence
    problem = request.problem
    provenance = problem.observations[0].raw_quote.provenance
    training = problem.training_observations
    held_out = problem.evaluation_observations
    training_estimate = evidence.selected_heston_training_result.estimate.as_vector()
    full_estimate = evidence.selected_heston_full_sample_result.estimate.as_vector()

    tables: list[ReportTable] = [
        ReportTable(
            "summary",
            (
                ReportColumn("item", "Item"),
                ReportColumn("value", "Value"),
            ),
            (
                (
                    "design",
                    "same-date cross-sectional 10-training / 4-held-out validation",
                ),
                (
                    "black_scholes_training_volatility",
                    evidence.black_scholes_fit.annualized_volatility,
                ),
                (
                    "heston_lower_training_price_rmse",
                    evidence.conclusion.heston_lower_training_price_rmse,
                ),
                (
                    "heston_lower_heldout_price_rmse",
                    evidence.conclusion.heston_lower_evaluation_price_rmse,
                ),
                (
                    "heston_lower_heldout_standardized_rmse",
                    evidence.conclusion.heston_lower_evaluation_standardized_rmse,
                ),
                ("conclusion", evidence.conclusion.statement),
            ),
        ),
        _metrics_table(
            "training_metrics",
            evidence.black_scholes_training_metrics,
            evidence.heston_training_metrics,
        ),
        _metrics_table(
            "heldout_metrics",
            evidence.black_scholes_evaluation_metrics,
            evidence.heston_evaluation_metrics,
        ),
        _contract_table("training_contracts", training),
        _contract_table("heldout_contracts", held_out),
        ReportTable(
            "residuals",
            (
                ReportColumn("contract_id", "Contract ID"),
                ReportColumn("model", "Model"),
                ReportColumn("partition", "Partition"),
                ReportColumn("expiry", "Expiry"),
                ReportColumn("strike", "Strike", "spot units"),
                ReportColumn("right", "Right"),
                ReportColumn(
                    "log_forward_moneyness",
                    "Log forward moneyness",
                ),
                ReportColumn(
                    "observed_price",
                    "Observed price",
                    "price units",
                ),
                ReportColumn("model_price", "Model price", "price units"),
                ReportColumn("residual", "Model - observed", "price units"),
                ReportColumn(
                    "half_spread",
                    "Bid/ask half spread",
                    "price units",
                ),
                ReportColumn(
                    "standardized_residual",
                    "Standardized residual",
                ),
                ReportColumn(
                    "relative_absolute_error",
                    "Relative absolute error",
                    "fraction",
                ),
            ),
            tuple(
                (
                    item.contract_id,
                    item.model.value,
                    item.partition.value,
                    item.expiry.isoformat(),
                    item.strike,
                    item.right,
                    item.log_forward_moneyness,
                    item.observed_price,
                    item.model_price,
                    item.residual,
                    item.half_spread,
                    item.standardized_residual,
                    item.relative_absolute_error,
                )
                for item in evidence.residuals
            ),
        ),
        ReportTable(
            "calibrated_parameters",
            (
                ReportColumn("parameter", "Parameter"),
                ReportColumn("training_estimate", "Training estimate"),
                ReportColumn(
                    "full_sample_estimate",
                    "Full-sample stability estimate",
                ),
                ReportColumn(
                    "domain_scaled_shift",
                    "Train-to-full domain-scaled shift",
                ),
            ),
            tuple(
                (name, training_value, full_value, shift)
                for name, training_value, full_value, shift in zip(
                    _PARAMETER_NAMES,
                    training_estimate,
                    full_estimate,
                    evidence.heston_stability.train_to_full_domain_scaled_shifts,
                    strict=True,
                )
            ),
        ),
        ReportTable(
            "calibration_starts",
            (
                ReportColumn("phase", "Calibration phase"),
                ReportColumn("start_index", "Start index", "count"),
                *(
                    ReportColumn(f"start_{name}", f"Initial {name}")
                    for name in _PARAMETER_NAMES
                ),
                ReportColumn("converged", "Converged"),
                ReportColumn("objective", "Objective value"),
                *(
                    ReportColumn(f"estimate_{name}", f"Estimate {name}")
                    for name in _PARAMETER_NAMES
                ),
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
                ReportColumn("failure", "Failure message"),
            ),
            _start_rows("training", evidence.heston_training_starts)
            + _start_rows(
                "full_sample_stability",
                evidence.heston_full_sample_starts,
            ),
        ),
        ReportTable(
            "stability",
            (
                ReportColumn("metric", "Metric"),
                ReportColumn("value", "Value"),
            ),
            (
                (
                    "successful_training_starts",
                    evidence.heston_stability.successful_training_starts,
                ),
                (
                    "failed_training_starts",
                    evidence.heston_stability.failed_training_starts,
                ),
                (
                    "maximum_training_start_domain_scaled_spread",
                    evidence.heston_stability.maximum_training_start_domain_scaled_spread,
                ),
                (
                    "maximum_train_to_full_domain_scaled_shift",
                    evidence.heston_stability.maximum_train_to_full_domain_scaled_shift,
                ),
            ),
        ),
        ReportTable(
            "conditioning",
            (
                ReportColumn("phase", "Calibration phase"),
                ReportColumn("jacobian_rank", "Jacobian rank", "count"),
                ReportColumn("parameter_count", "Parameter count", "count"),
                ReportColumn("target_count", "Target count", "count"),
                ReportColumn("rank_deficient", "Rank deficient"),
                ReportColumn("condition_number", "Condition number"),
                ReportColumn("singular_values", "Singular values"),
            ),
            tuple(
                (
                    phase,
                    result.conditioning.jacobian_rank,
                    result.conditioning.parameter_count,
                    result.conditioning.target_count,
                    result.conditioning.rank_deficient,
                    result.conditioning.condition_number,
                    ", ".join(
                        str(value) for value in result.conditioning.singular_values
                    ),
                )
                for phase, result in (
                    ("training", evidence.selected_heston_training_result),
                    (
                        "full_sample_stability",
                        evidence.selected_heston_full_sample_result,
                    ),
                )
            ),
        ),
        ReportTable(
            "assumptions",
            (
                ReportColumn("item", "Assumption / non-claim"),
                ReportColumn("value", "Value"),
            ),
            (
                ("valuation_date", problem.valuation_date.isoformat()),
                ("pricing_measure", problem.pricing_measure.name),
                ("day_count", "ACT/365F"),
                (
                    "rate",
                    problem.numeraire.continuously_compounded_rate,
                ),
                (
                    "continuous_dividend_yield",
                    problem.continuous_dividend_yield,
                ),
                ("training_contract_count", len(training)),
                ("heldout_contract_count", len(held_out)),
                (
                    "temporal_out_of_sample_tested",
                    evidence.conclusion.temporal_out_of_sample_tested,
                ),
                (
                    "heston_hedge_comparison_supported",
                    evidence.conclusion.heston_hedge_comparison_supported,
                ),
                ("historical_trading_profit_result", False),
                ("global_heston_identification_proven", False),
            ),
        ),
        ReportTable(
            "provenance",
            (
                ReportColumn("field", "Field"),
                ReportColumn("value", "Value"),
            ),
            (
                ("provider", provenance.provider),
                ("source", provenance.source),
                ("market_date", provenance.market_date.isoformat()),
                ("retrieved_at", provenance.retrieved_at.isoformat()),
                ("raw_artifact_sha256", provenance.raw_artifact_sha256),
                ("license_notes", provenance.license_notes),
            ),
        ),
    ]

    if performance is not None:
        tables.append(
            ReportTable(
                "performance",
                (
                    ReportColumn("workload_id", "Workload ID"),
                    ReportColumn("label", "Label"),
                    ReportColumn(
                        "baseline_seconds",
                        "Baseline median",
                        "seconds",
                    ),
                    ReportColumn(
                        "optimized_seconds",
                        "Optimized median",
                        "seconds",
                    ),
                    ReportColumn("speedup_x", "Speedup", "x"),
                    ReportColumn("heavy_workload", "Heavy workload"),
                    ReportColumn("detail", "Detail"),
                ),
                tuple(
                    (
                        item.workload_id,
                        item.label,
                        item.baseline_median_seconds,
                        item.optimized_median_seconds,
                        item.speedup_x,
                        item.heavy_workload,
                        item.detail,
                    )
                    for item in performance.workloads
                ),
            )
        )

    metadata = [
        ReportField("valuation_date", problem.valuation_date.isoformat()),
        ReportField(
            "underlying",
            problem.observations[0].raw_underlying.underlying_id,
        ),
        ReportField("spot", problem.spot, "spot units"),
        ReportField("design", "same-date cross-sectional holdout"),
        ReportField("training_contracts", len(training), "count"),
        ReportField("heldout_contracts", len(held_out), "count"),
        ReportField(
            "conclusion_scope",
            "selected observations and stated conventions only; "
            "no universal model ranking",
        ),
    ]
    if performance is not None:
        metadata.extend(
            (
                ReportField("performance_evidence_kind", performance.evidence_kind),
                ReportField(
                    "performance_source_artifact",
                    performance.source_artifact_path,
                ),
                ReportField(
                    "performance_baseline_revision",
                    performance.baseline_revision,
                ),
                ReportField(
                    "performance_optimized_revision",
                    performance.optimized_reference_revision,
                ),
                ReportField(
                    "performance_workflow_run_id",
                    performance.workflow_run_id,
                ),
                ReportField(
                    "performance_timings_are_ci_thresholds",
                    performance.timings_are_ci_thresholds,
                ),
            )
        )

    return TabularReport(
        report_id="bs_heston_validation",
        title="Black-Scholes versus Heston model-validation evidence",
        metadata=tuple(metadata),
        tables=tuple(tables),
    )
