"""Renderer-neutral UI5 presentation for merged M7 validation evidence."""

from __future__ import annotations

from dataclasses import dataclass

from qf_platform.application.ui5_validation import UI5ValidationAnalysis
from qf_platform.presentation.black_scholes import PresentationRow
from qf_platform.presentation.plotting import PlotData, PlotPoint, PlotSeries
from qf_platform.validation import (
    ModelResidualEvidence,
    ValidationModel,
    ValidationPartition,
)


@dataclass(frozen=True, slots=True)
class UI5ValidationPresentation:
    """Concrete validation/model-risk values for the native UI5 workspace."""

    summary_rows: tuple[PresentationRow, ...]
    training_metric_rows: tuple[PresentationRow, ...]
    evaluation_metric_rows: tuple[PresentationRow, ...]
    residual_rows: tuple[PresentationRow, ...]
    stability_rows: tuple[PresentationRow, ...]
    model_risk_rows: tuple[PresentationRow, ...]
    workload_rows: tuple[PresentationRow, ...]
    inspector_rows: tuple[PresentationRow, ...]
    residual_plot: PlotData
    held_out_error_plot: PlotData
    parameter_stability_plot: PlotData


def build_ui5_validation_presentation(
    analysis: UI5ValidationAnalysis,
) -> UI5ValidationPresentation:
    """Convert authoritative M7 evidence into renderer-neutral UI values."""

    return UI5ValidationPresentation(
        summary_rows=_summary_rows(analysis),
        training_metric_rows=_metric_rows(analysis, ValidationPartition.TRAINING),
        evaluation_metric_rows=_metric_rows(analysis, ValidationPartition.EVALUATION),
        residual_rows=_residual_rows(analysis),
        stability_rows=_stability_rows(analysis),
        model_risk_rows=_model_risk_rows(analysis),
        workload_rows=tuple(
            PresentationRow(
                workload.operation,
                workload.workload_id,
                workload.detail,
                "Profile in M8",
            )
            for workload in analysis.workloads
        ),
        inspector_rows=_inspector_rows(analysis),
        residual_plot=_residual_plot(analysis),
        held_out_error_plot=_held_out_error_plot(analysis),
        parameter_stability_plot=_parameter_stability_plot(analysis),
    )


def _summary_rows(analysis: UI5ValidationAnalysis) -> tuple[PresentationRow, ...]:
    evidence = analysis.evidence
    problem = evidence.problem
    return (
        PresentationRow(
            "Validation question",
            "Black-Scholes vs Heston on the same predeclared SPX holdout",
            "Both models fit the same training prices before held-out predictions are evaluated.",
            "M7 evidence",
        ),
        PresentationRow(
            "Partition",
            (
                f"{len(problem.training_contract_ids)} training · "
                f"{len(problem.evaluation_contract_ids)} held-out"
            ),
            "Same-date cross-sectional holdout; evaluation roles are fixed before fitting.",
            "Predeclared",
        ),
        PresentationRow(
            "Black-Scholes training fit",
            f"sigma = {evidence.black_scholes_fit.annualized_volatility:.5f}",
            "One constant annualized volatility fitted on TRAIN only.",
            "Frozen before evaluation",
        ),
        PresentationRow(
            "Bounded conclusion",
            evidence.conclusion.statement,
            "This conclusion is local to the explicit sample, conventions, objective, and holdout design.",
            "Do not overgeneralize",
        ),
    )


def _metric_rows(
    analysis: UI5ValidationAnalysis,
    partition: ValidationPartition,
) -> tuple[PresentationRow, ...]:
    evidence = analysis.evidence
    if partition is ValidationPartition.TRAINING:
        bs = evidence.black_scholes_training_metrics
        heston = evidence.heston_training_metrics
        label = "TRAINING"
    else:
        bs = evidence.black_scholes_evaluation_metrics
        heston = evidence.heston_evaluation_metrics
        label = "HELD-OUT EVALUATION"

    return (
        PresentationRow(
            f"{label} · price RMSE",
            f"Black-Scholes {bs.root_mean_square_error:.3f} · Heston {heston.root_mean_square_error:.3f}",
            "Option-price units. Lower is better for this metric only.",
            "Comparison",
        ),
        PresentationRow(
            f"{label} · half-spread standardized RMSE",
            (
                f"Black-Scholes {bs.standardized_root_mean_square_error:.3f} · "
                f"Heston {heston.standardized_root_mean_square_error:.3f}"
            ),
            "Residual divided by observed bid/ask half-spread; not a statistical variance estimate.",
            "Comparison",
        ),
        PresentationRow(
            f"{label} · relative MAE",
            (
                f"Black-Scholes {100.0 * bs.relative_mean_absolute_error:.2f}% · "
                f"Heston {100.0 * heston.relative_mean_absolute_error:.2f}%"
            ),
            "Mean absolute price error scaled by observed price.",
            "Comparison",
        ),
        PresentationRow(
            f"{label} · max |standardized residual|",
            (
                f"Black-Scholes {bs.maximum_absolute_standardized_residual:.3f} · "
                f"Heston {heston.maximum_absolute_standardized_residual:.3f}"
            ),
            "Largest contract-level miss after half-spread scaling.",
            "Diagnostic",
        ),
    )


def _residual_rows(analysis: UI5ValidationAnalysis) -> tuple[PresentationRow, ...]:
    paired: dict[
        tuple[str, ValidationPartition],
        dict[ValidationModel, ModelResidualEvidence],
    ] = {}
    for residual in analysis.evidence.residuals:
        paired.setdefault((residual.contract_id, residual.partition), {})[
            residual.model
        ] = residual

    rows: list[PresentationRow] = []
    for (contract_id, partition), models in paired.items():
        bs = models.get(ValidationModel.BLACK_SCHOLES)
        heston = models.get(ValidationModel.HESTON)
        if bs is None or heston is None:
            continue
        rows.append(
            PresentationRow(
                contract_id,
                (
                    f"observed {bs.observed_price:.3f} · "
                    f"BS {bs.model_price:.3f} · Heston {heston.model_price:.3f}"
                ),
                (
                    f"log-forward moneyness {bs.log_forward_moneyness:+.4f} · "
                    f"standardized residuals BS {bs.standardized_residual:+.3f}, "
                    f"Heston {heston.standardized_residual:+.3f}"
                ),
                "TRAIN" if partition is ValidationPartition.TRAINING else "HELD OUT",
            )
        )
    return tuple(rows)


def _stability_rows(analysis: UI5ValidationAnalysis) -> tuple[PresentationRow, ...]:
    evidence = analysis.evidence
    stability = evidence.heston_stability
    train = evidence.selected_heston_training_result
    full = evidence.selected_heston_full_sample_result
    names = ("v0", "kappa", "theta", "xi", "rho")
    training_vector = train.estimate.as_vector()
    full_vector = full.estimate.as_vector()
    rows = [
        PresentationRow(
            "Training optimizer starts",
            (
                f"{stability.successful_training_starts} successful · "
                f"{stability.failed_training_starts} failed"
            ),
            (
                "Maximum domain-scaled spread across successful training starts: "
                f"{stability.maximum_training_start_domain_scaled_spread:.3e}."
            ),
            "Local stability evidence",
        ),
        PresentationRow(
            "Training Jacobian",
            (
                f"rank {stability.training_jacobian_rank} · condition "
                f"{_format_optional(stability.training_condition_number)}"
            ),
            "Domain-scaled local Jacobian evidence; full rank is not proof of global identification.",
            "Conditioning",
        ),
        PresentationRow(
            "Full-sample stability Jacobian",
            (
                f"rank {stability.full_sample_jacobian_rank} · condition "
                f"{_format_optional(stability.full_sample_condition_number)}"
            ),
            "Computed only after held-out evaluation; it cannot feed back into held-out predictions.",
            "Post-evaluation evidence",
        ),
    ]
    for index, name in enumerate(names):
        rows.append(
            PresentationRow(
                f"{name}: training → full sample",
                f"{training_vector[index]:.6g} → {full_vector[index]:.6g}",
                (
                    "Domain-scaled movement "
                    f"{stability.train_to_full_domain_scaled_shifts[index]:.4f}."
                ),
                "Parameter stability",
            )
        )
    return tuple(rows)


def _model_risk_rows(analysis: UI5ValidationAnalysis) -> tuple[PresentationRow, ...]:
    conclusion = analysis.evidence.conclusion
    return (
        PresentationRow(
            "Held-out pricing",
            "Heston improves the predeclared held-out pricing metrics",
            "This is empirical evidence for this same-date sample, not a universal model ranking.",
            "Supported",
        ),
        PresentationRow(
            "Temporal generalization",
            "Not tested",
            "The holdout is cross-sectional on one market date, not future-date forecasting.",
            "Unsupported",
        ),
        PresentationRow(
            "Heston hedging advantage",
            "Not tested",
            "M3 paths are explicitly Black-Scholes/GBM and there is no authoritative Heston path + Delta + hedge-accounting composition.",
            "Unsupported",
        ),
        PresentationRow(
            "Parameter identification",
            "Locally full rank but nontrivially conditioned",
            "Read together with M6's deliberately rank-deficient low-loss counterexample; conditioning is not posterior uncertainty.",
            "Model risk",
        ),
        PresentationRow(
            "Validation statement",
            conclusion.statement,
            "Optimizer convergence, held-out fit, and model validity remain different questions.",
            "Bounded conclusion",
        ),
    )


def _inspector_rows(analysis: UI5ValidationAnalysis) -> tuple[PresentationRow, ...]:
    return (
        PresentationRow(
            "Observed quantities",
            "14 normalized SPX/SPXW option observations",
            "Midpoint targets retain source/provenance lineage from the M4/M6 research path.",
        ),
        PresentationRow(
            "Validation problem",
            "BlackScholesHestonValidationProblem",
            "Owns observations, predeclared partition, fixed rate/carry/spot semantics, and financial model domains.",
        ),
        PresentationRow(
            "Validation method",
            "CrossSectionalBlackScholesHestonValidation",
            "Owns the Black-Scholes starting volatility, Heston starts, tolerances, and numerical evaluation budget.",
        ),
        PresentationRow(
            "Training fits",
            "One-volatility Black-Scholes + five-coordinate Heston calibration",
            "Both fit TRAIN only before held-out evaluation.",
        ),
        PresentationRow(
            "Evidence",
            "BlackScholesHestonValidationEvidence",
            "Immutable residuals, metrics, start outcomes, stability/conditioning, computation structure, and bounded conclusion.",
        ),
        PresentationRow(
            "M8 handoff",
            f"{len(analysis.workloads)} representative workloads",
            "Workload definitions/counts are not measured runtime or proof that C++ is needed.",
        ),
    )


def _residual_plot(analysis: UI5ValidationAnalysis) -> PlotData:
    def points(
        model: ValidationModel,
        partition: ValidationPartition,
    ) -> tuple[PlotPoint, ...]:
        items = [
            item
            for item in analysis.evidence.residuals
            if item.model is model and item.partition is partition
        ]
        items.sort(key=lambda item: item.log_forward_moneyness)
        return tuple(
            PlotPoint(item.log_forward_moneyness, item.standardized_residual)
            for item in items
        )

    return PlotData(
        title="Residual structure by log-forward moneyness",
        x_label="log(K / forward)",
        y_label="price residual / bid-ask half-spread",
        series=(
            PlotSeries(
                "bs_train",
                "Black-Scholes · TRAIN",
                points(ValidationModel.BLACK_SCHOLES, ValidationPartition.TRAINING),
            ),
            PlotSeries(
                "heston_train",
                "Heston · TRAIN",
                points(ValidationModel.HESTON, ValidationPartition.TRAINING),
            ),
            PlotSeries(
                "bs_eval",
                "Black-Scholes · HELD OUT",
                points(ValidationModel.BLACK_SCHOLES, ValidationPartition.EVALUATION),
            ),
            PlotSeries(
                "heston_eval",
                "Heston · HELD OUT",
                points(ValidationModel.HESTON, ValidationPartition.EVALUATION),
            ),
        ),
    )


def _held_out_error_plot(analysis: UI5ValidationAnalysis) -> PlotData:
    evaluation_ids = analysis.evidence.problem.evaluation_contract_ids

    def points(model: ValidationModel) -> tuple[PlotPoint, ...]:
        by_id = {
            item.contract_id: item
            for item in analysis.evidence.residuals
            if item.model is model and item.partition is ValidationPartition.EVALUATION
        }
        return tuple(
            PlotPoint(float(index), abs(by_id[contract_id].residual))
            for index, contract_id in enumerate(evaluation_ids)
        )

    return PlotData(
        title="Held-out absolute pricing error",
        x_label="held-out contract index",
        y_label="absolute price error",
        series=(
            PlotSeries(
                "black_scholes",
                "Black-Scholes",
                points(ValidationModel.BLACK_SCHOLES),
            ),
            PlotSeries("heston", "Heston", points(ValidationModel.HESTON)),
        ),
    )


def _parameter_stability_plot(analysis: UI5ValidationAnalysis) -> PlotData:
    shifts = analysis.evidence.heston_stability.train_to_full_domain_scaled_shifts
    return PlotData(
        title="Heston train → full-sample parameter movement",
        x_label="parameter index (v0, kappa, theta, xi, rho)",
        y_label="movement / explicit domain width",
        series=(
            PlotSeries(
                "shift",
                "domain-scaled movement",
                tuple(
                    PlotPoint(float(index), shift) for index, shift in enumerate(shifts)
                ),
            ),
        ),
    )


def _format_optional(value: float | None) -> str:
    return "not finite / rank deficient" if value is None else f"{value:.1f}"


__all__ = ["UI5ValidationPresentation", "build_ui5_validation_presentation"]
