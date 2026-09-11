from __future__ import annotations

from functools import lru_cache

import pytest

from qf_platform.application.ui5_validation import (
    UI5ValidationAnalysis,
    make_ui5_reference_validation_request,
    run_ui5_validation,
)
from qf_platform.presentation.ui5_validation import build_ui5_validation_presentation


@lru_cache(maxsize=1)
def _analysis() -> UI5ValidationAnalysis:
    return run_ui5_validation(make_ui5_reference_validation_request())


def test_ui5_reference_request_preserves_m7_predeclared_holdout() -> None:
    request = make_ui5_reference_validation_request()

    assert len(request.problem.observations) == 14
    assert len(request.problem.training_contract_ids) == 10
    assert len(request.problem.evaluation_contract_ids) == 4
    assert request.problem.evaluation_contract_ids == (
        "SPXW-2023-02-03-put-3850",
        "SPXW-2023-02-03-call-3970",
        "SPXW-2023-04-28-put-3800",
        "SPXW-2023-04-28-call-4075",
    )
    assert len(request.method.heston_initial_guesses) == 3


def test_ui5_validation_runs_real_m7_evidence_and_keeps_limits_explicit() -> None:
    analysis = _analysis()
    evidence = analysis.evidence

    assert evidence.black_scholes_fit.annualized_volatility == pytest.approx(
        0.209,
        abs=0.005,
    )
    assert evidence.heston_evaluation_metrics.root_mean_square_error < (
        0.25 * evidence.black_scholes_evaluation_metrics.root_mean_square_error
    )
    assert evidence.conclusion.heston_lower_evaluation_price_rmse
    assert not evidence.conclusion.temporal_out_of_sample_tested
    assert not evidence.conclusion.heston_hedge_comparison_supported
    assert evidence.heston_stability.training_jacobian_rank == 5
    assert evidence.heston_stability.training_condition_number is not None
    assert len(analysis.workloads) == 6
    assert all(
        "runtime" not in workload.detail.lower() for workload in analysis.workloads[:-1]
    )
    assert "not runtime" in analysis.workloads[-1].detail.lower()


def test_ui5_presentation_separates_training_evaluation_and_workload_structure() -> (
    None
):
    presentation = build_ui5_validation_presentation(_analysis())

    assert any("TRAINING" in row.label for row in presentation.training_metric_rows)
    assert any("HELD-OUT" in row.label for row in presentation.evaluation_metric_rows)
    assert len(presentation.residual_rows) == 14
    assert {row.status for row in presentation.residual_rows} == {"TRAIN", "HELD OUT"}
    assert any(
        row.label == "Heston hedging advantage" for row in presentation.model_risk_rows
    )
    assert all(row.status == "Profile in M8" for row in presentation.workload_rows)
    assert len(presentation.residual_plot.series) == 4
    assert len(presentation.held_out_error_plot.series) == 2
    assert len(presentation.parameter_stability_plot.series[0].points) == 5
