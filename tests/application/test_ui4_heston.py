from __future__ import annotations

import json
from pathlib import Path

import pytest

from qf_platform.application import (
    HestonCalibrationDraft,
    HestonPricingDraft,
    canonical_m6_market_reference,
    make_heston_calibration_request,
    make_heston_pricing_request,
    run_heston_calibration,
    run_heston_pricing,
)
from qf_platform.pricing import (
    EuropeanOption,
    HestonEquityState,
    HestonFourierValuationResult,
    HestonLaw,
    HestonMonteCarloValuationResult,
    HestonParameters,
)


def test_heston_pricing_request_preserves_model_method_and_result_boundaries() -> None:
    request = make_heston_pricing_request(
        HestonPricingDraft(
            fourier_intervals="64",
            monte_carlo_paths="256",
            monte_carlo_time_steps="16",
            monte_carlo_seed="19",
        )
    )

    problem = request.problem
    assert isinstance(problem.current_state.value, HestonEquityState)
    assert problem.current_state.value.instantaneous_variance == pytest.approx(0.04)
    assert isinstance(problem.stochastic_law, HestonLaw)
    assert isinstance(problem.parameters, HestonParameters)
    assert isinstance(problem.contract, EuropeanOption)

    analysis = run_heston_pricing(request)

    assert analysis.request.problem is problem
    assert isinstance(analysis.fourier_result, HestonFourierValuationResult)
    assert isinstance(analysis.monte_carlo_result, HestonMonteCarloValuationResult)
    assert analysis.fourier_result.intervals == 64
    assert analysis.monte_carlo_result.paths == 256
    assert analysis.monte_carlo_result.time_steps == 16
    assert analysis.monte_carlo_result.seed == 19
    assert {point.intervals for point in analysis.fourier_stability} == {32, 64, 128}


def test_thin_calibration_exposes_small_fit_with_rank_deficiency() -> None:
    request = make_heston_calibration_request(
        "thin",
        HestonCalibrationDraft(fourier_intervals="64"),
    )

    analysis = run_heston_calibration(request)

    assert analysis.mode == "thin"
    assert len(analysis.problem.targets) == 3
    assert len(analysis.runs) == 2
    assert all(run.result.conditioning.rank_deficient for run in analysis.runs)
    assert all(run.result.objective_value < 1.0e-8 for run in analysis.runs)
    distance = max(
        abs(left - right)
        for left, right in zip(
            analysis.runs[0].result.estimate.as_vector(),
            analysis.runs[1].result.estimate.as_vector(),
            strict=True,
        )
    )
    assert distance > 0.05


def test_packaged_m6_market_reference_matches_committed_derived_evidence() -> None:
    reference = canonical_m6_market_reference()
    path = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "evidence"
        / "m6_spx_heston_calibration_reference.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert reference.source_repository == payload["source_lineage"]["repository"]
    assert reference.source_commit == payload["source_lineage"]["commit"]
    assert reference.source_path == payload["source_lineage"]["path"]
    assert reference.source_git_blob_sha1 == payload["source_lineage"]["git_blob_sha1"]
    assert reference.quote_date == payload["market_snapshot"]["quote_date"]
    assert reference.observed_spot == payload["market_snapshot"]["observed_spot"]
    assert reference.target_count == payload["market_snapshot"]["target_count"]
    assert tuple(reference.best_estimate) == pytest.approx(
        (
            payload["best_reference_result"]["initial_variance"],
            payload["best_reference_result"]["mean_reversion_speed"],
            payload["best_reference_result"]["long_run_variance"],
            payload["best_reference_result"]["volatility_of_variance"],
            payload["best_reference_result"]["correlation"],
        )
    )
    assert reference.best_objective_value == pytest.approx(
        payload["best_reference_result"]["objective_value"]
    )
    assert reference.condition_number == pytest.approx(
        payload["best_reference_result"]["condition_number_domain_scaled"]
    )
    assert reference.standardized_residuals == pytest.approx(
        payload["standardized_residuals_in_pinned_contract_order"]
    )
    assert tuple(start.objective_value for start in reference.starts) == pytest.approx(
        tuple(item["objective_value"] for item in payload["multiple_start_results"])
    )
