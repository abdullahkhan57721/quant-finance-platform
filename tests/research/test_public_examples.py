"""Consumer-level checks for the supported F1 research examples."""

from dataclasses import FrozenInstanceError, replace
from datetime import date

import pytest

from examples.research import (
    delta_hedging,
    heston_calibration,
    heston_forward,
    market_and_iv,
    pricing_and_greeks,
    validation_and_performance,
)
from qf_platform.application import (
    CRRConvergencePoint,
    GammaBumpPoint,
    GreekCurvePoint,
    MarketObservationStatus,
    MonteCarloConvergencePoint,
    SensitivityRun,
    ValuationRun,
)
from qf_platform.inference import (
    BisectionImpliedVolatility,
    BlackScholesImpliedVolatilityProblem,
    infer_implied_volatility,
)
from qf_platform.pricing import (
    BlackScholesParameters,
    FlatMoneyMarketNumeraire,
    MonteCarloEuropeanOption,
    PricingMeasureSemantics,
    evaluate,
)
from qf_platform.sensitivity import (
    AnalyticBlackScholesSensitivity,
    BlackScholesSensitivityProblem,
    evaluate_sensitivity,
)


def test_pricing_example_preserves_production_values_and_public_evidence_types() -> (
    None
):
    request = pricing_and_greeks.make_request()
    analysis = pricing_and_greeks.run_example()
    assert isinstance(analysis.selected_valuation, ValuationRun)
    assert isinstance(analysis.crr_convergence[0], CRRConvergencePoint)
    assert isinstance(analysis.monte_carlo_convergence[0], MonteCarloConvergencePoint)
    assert isinstance(analysis.sensitivities[0], SensitivityRun)
    assert isinstance(analysis.greek_curve[0], GreekCurvePoint)
    assert isinstance(analysis.gamma_bump_study[0], GammaBumpPoint)
    analytic = analysis.selected_valuation.result
    assert analytic == evaluate(request.composition.problem, request.composition.method)
    assert analytic is not None
    # Published M1 benchmark; rounded here to 10 decimal places.
    assert analytic.present_value == pytest.approx(10.4505835722, abs=5e-11)
    assert analysis.valuations[2].result == evaluate(
        request.composition.problem, MonteCarloEuropeanOption(paths=20_000, seed=1729)
    )
    for run in analysis.sensitivities:
        assert run.analytic_result == evaluate_sensitivity(
            BlackScholesSensitivityProblem(
                request.composition.problem, run.sensitivity
            ),
            AnalyticBlackScholesSensitivity(),
        )
    with pytest.raises(FrozenInstanceError):
        analytic.present_value = 0.0  # pyright: ignore[reportAttributeAccessIssue]
    # A custom numeric input changes the authoritative problem without text drafts.
    changed = replace(
        request.composition.problem,
        parameters=BlackScholesParameters(annualized_volatility=0.30),
    )
    assert (
        evaluate(changed, request.composition.method).present_value
        > analytic.present_value
    )


def test_hedging_example_retains_seed_cost_and_replication_semantics() -> None:
    analysis = delta_hedging.run_example()
    assert analysis.selected_result.seed == 1729
    assert tuple(row.seed for row in analysis.selected_replicates) == tuple(
        range(1729, 1737)
    )
    assert analysis.selected_summary.replicate_count == 8
    assert analysis.selected_result.total_transaction_cost > 0.0
    assert analysis == delta_hedging.run_example()


def test_market_example_infers_from_normalized_synthetic_observation() -> None:
    analysis = market_and_iv.run_example()
    outcome = analysis.outcomes[0]
    assert outcome.status is MarketObservationStatus.INFERRED
    assert outcome.normalized is not None
    assert outcome.normalized.target_price == pytest.approx(10.45)
    assert outcome.normalized.raw_quote is outcome.raw_quote
    assert outcome.raw_quote.provenance.provider == "synthetic:F1-example"
    numeraire = FlatMoneyMarketNumeraire(date(2026, 1, 1), 0.05)
    problem = BlackScholesImpliedVolatilityProblem(
        observation=outcome.normalized,
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^N", numeraire=numeraire),
    )
    assert outcome.result == infer_implied_volatility(
        problem,
        BisectionImpliedVolatility(
            price_tolerance=1e-10, volatility_tolerance=1e-10, max_iterations=200
        ),
    )
    assert analysis.empirical_evidence.underlying == "SPX"
    assert "raw rows are not redistributed" in analysis.empirical_evidence.license_note


def test_heston_example_uses_same_problem_and_production_methods() -> None:
    analysis = heston_forward.run_example()
    request = analysis.request
    assert analysis.fourier_result == evaluate(request.problem, request.fourier_method)
    assert analysis.monte_carlo_result == evaluate(
        request.problem, request.monte_carlo_method
    )
    assert analysis.monte_carlo_result.seed == 1729
    assert request.problem.current_state.value.instantaneous_variance == 0.04
    assert {point.intervals for point in analysis.fourier_stability} == {128, 256, 512}


def test_calibration_example_separates_recovery_from_nonidentification() -> None:
    recovery, thin = heston_calibration.run_example()
    for run in recovery.runs:
        # Synthetic same-method recovery tolerance from the M6 evidence scale.
        assert run.result.estimate.as_vector() == pytest.approx(
            recovery.truth.as_vector(), abs=1e-4, rel=1e-4
        )
        assert not run.result.conditioning.rank_deficient
    assert len(thin.problem.targets) == 3
    assert all(run.result.conditioning.rank_deficient for run in thin.runs)
    assert all(run.result.objective_value < 1e-8 for run in thin.runs)
    assert thin.runs[0].result.estimate != thin.runs[1].result.estimate


def test_validation_example_preserves_holdout_and_historical_performance() -> None:
    analysis, performance = validation_and_performance.run_example()
    evidence = analysis.evidence
    # Rounded committed M7 metrics; tolerance reflects the displayed precision.
    assert evidence.black_scholes_evaluation_metrics.root_mean_square_error == (
        pytest.approx(8.412, abs=0.0005)
    )
    assert evidence.heston_evaluation_metrics.root_mean_square_error == (
        pytest.approx(0.671, abs=0.0005)
    )
    assert not evidence.conclusion.temporal_out_of_sample_tested
    assert not evidence.conclusion.heston_hedge_comparison_supported
    assert len(analysis.workloads) == len(performance.workloads) == 6
    assert not performance.timings_are_ci_thresholds
    assert not performance.cpp_added
    assert performance.baseline_revision != performance.optimized_reference_revision
