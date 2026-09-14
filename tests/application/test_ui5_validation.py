from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

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
    assert request.problem.heston_forward_method.integration_upper_bound == 100.0
    assert request.problem.heston_forward_method.intervals == 256
    assert len(request.method.heston_initial_guesses) == 3


def test_ui5_validation_matches_committed_m7_reference_evidence() -> None:
    evidence = _analysis().evidence
    artifact = json.loads(
        Path("docs/evidence/m7_spx_bs_vs_heston_validation_reference.json").read_text(
            encoding="utf-8"
        )
    )

    assert evidence.black_scholes_fit.annualized_volatility == pytest.approx(
        artifact["black_scholes_training_fit"]["annualized_volatility"],
        abs=1.0e-9,
    )
    metric_pairs = (
        (evidence.black_scholes_training_metrics, "black_scholes_training"),
        (evidence.black_scholes_evaluation_metrics, "black_scholes_evaluation"),
        (evidence.heston_training_metrics, "heston_training"),
        (evidence.heston_evaluation_metrics, "heston_evaluation"),
    )
    for metrics, key in metric_pairs:
        recorded = artifact["metrics"][key]
        assert metrics.root_mean_square_error == pytest.approx(
            recorded["root_mean_square_error"], abs=1.0e-8
        )
        assert metrics.standardized_root_mean_square_error == pytest.approx(
            recorded["standardized_root_mean_square_error"], abs=1.0e-8
        )
        assert metrics.relative_mean_absolute_error == pytest.approx(
            recorded["relative_mean_absolute_error"], abs=1.0e-8
        )

    expected_training = artifact["selected_heston_training_estimate"]
    training = evidence.selected_heston_training_result.estimate
    assert training.initial_variance == pytest.approx(
        expected_training["initial_variance"], abs=1.0e-8
    )
    assert training.mean_reversion_speed == pytest.approx(
        expected_training["mean_reversion_speed"], abs=1.0e-7
    )
    assert training.long_run_variance == pytest.approx(
        expected_training["long_run_variance"], abs=1.0e-8
    )
    assert training.volatility_of_variance == pytest.approx(
        expected_training["volatility_of_variance"], abs=1.0e-7
    )
    assert training.correlation == pytest.approx(
        expected_training["correlation"], abs=1.0e-7
    )


def test_ui5_validation_runs_real_m7_evidence_and_keeps_limits_explicit() -> None:
    analysis = _analysis()
    evidence = analysis.evidence

    assert evidence.conclusion.heston_lower_evaluation_price_rmse
    assert not evidence.conclusion.temporal_out_of_sample_tested
    assert not evidence.conclusion.heston_hedge_comparison_supported
    assert evidence.heston_stability.training_jacobian_rank == 5
    assert evidence.heston_stability.training_condition_number is not None
    assert evidence.computation.heston_fourier_intervals == 256
    assert len(analysis.workloads) == 6
    assert all(
        "runtime" not in workload.detail.lower() for workload in analysis.workloads
    )
    assert (
        "measured m8 result is presented separately"
        in analysis.workloads[-1].detail.lower()
    )


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
    assert all(
        row.status == "M8 workload lineage" for row in presentation.workload_rows
    )
    assert len(presentation.residual_plot.series) == 4
    assert len(presentation.held_out_error_plot.series) == 2
    assert len(presentation.parameter_stability_plot.series[0].points) == 5
