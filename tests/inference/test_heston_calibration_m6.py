from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from qf_platform.inference import (
    HestonCalibrationBounds,
    HestonCalibrationConvergenceError,
    HestonCalibrationCoordinates,
    HestonCalibrationProblem,
    HestonCalibrationTargetSource,
    HestonCalibrationWeighting,
    HestonPriceCalibrationTarget,
    InvalidHestonCalibrationInitialGuess,
    InvalidHestonCalibrationProblem,
    ScipyLeastSquaresHestonCalibration,
    calibrate_heston,
)
from qf_platform.market_data import (
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    RawOptionQuote,
    RawUnderlyingObservation,
    normalize_european_option_midpoint,
)
from qf_platform.pricing import (
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    HestonEquityState,
    HestonFourierEuropeanOption,
    HestonLaw,
    HestonParameters,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
    evaluate,
)

_VALUATION_DATE = date(2026, 1, 1)
_SPOT = 100.0
_RATE = 0.03
_Q = 0.01
_TRUTH = HestonCalibrationCoordinates(
    initial_variance=0.04,
    parameters=HestonParameters(
        mean_reversion_speed=2.0,
        long_run_variance=0.04,
        volatility_of_variance=0.5,
        correlation=-0.7,
        continuous_dividend_yield=_Q,
    ),
)
_BOUNDS = HestonCalibrationBounds(
    minimum_initial_variance=0.005,
    maximum_initial_variance=0.15,
    minimum_mean_reversion_speed=0.2,
    maximum_mean_reversion_speed=6.0,
    minimum_long_run_variance=0.005,
    maximum_long_run_variance=0.15,
    minimum_volatility_of_variance=0.1,
    maximum_volatility_of_variance=1.5,
    minimum_correlation=-0.95,
    maximum_correlation=-0.1,
)
_FORWARD = HestonFourierEuropeanOption(
    integration_upper_bound=80.0,
    intervals=128,
)
_START_A = HestonCalibrationCoordinates(
    initial_variance=0.06,
    parameters=HestonParameters(
        mean_reversion_speed=1.2,
        long_run_variance=0.06,
        volatility_of_variance=0.8,
        correlation=-0.4,
        continuous_dividend_yield=_Q,
    ),
)
_START_B = HestonCalibrationCoordinates(
    initial_variance=0.02,
    parameters=HestonParameters(
        mean_reversion_speed=5.0,
        long_run_variance=0.02,
        volatility_of_variance=0.3,
        correlation=-0.85,
        continuous_dividend_yield=_Q,
    ),
)


def _market_semantics() -> tuple[
    FlatMoneyMarketNumeraire,
    PricingMeasureSemantics[date],
]:
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=_RATE,
    )
    return numeraire, PricingMeasureSemantics(name="Q^N", numeraire=numeraire)


def _heston_price(
    contract: EuropeanOption,
    coordinates: HestonCalibrationCoordinates,
) -> float:
    numeraire, measure = _market_semantics()
    law = HestonLaw()
    problem = PricingProblem(
        current_state=ModeledState(
            time=_VALUATION_DATE,
            value=HestonEquityState(
                spot=_SPOT,
                instantaneous_variance=coordinates.initial_variance,
            ),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=coordinates.parameters,
        contract=contract,
        numeraire=numeraire,
        pricing_measure=measure,
    )
    return evaluate(problem, _FORWARD).present_value


def _synthetic_targets() -> tuple[HestonPriceCalibrationTarget, ...]:
    targets: list[HestonPriceCalibrationTarget] = []
    for days in (91, 182, 365, 548):
        expiry = _VALUATION_DATE + timedelta(days=days)
        for strike in (80.0, 90.0, 100.0, 110.0, 120.0):
            contract = EuropeanOption(
                expiry=expiry,
                strike=strike,
                right=OptionRight.CALL,
            )
            targets.append(
                HestonPriceCalibrationTarget.synthetic(
                    contract=contract,
                    target_price=_heston_price(contract, _TRUTH),
                    label=f"T{days}-K{strike:g}",
                )
            )
    return tuple(targets)


def _problem(
    targets: tuple[HestonPriceCalibrationTarget, ...],
    *,
    weighting: HestonCalibrationWeighting = HestonCalibrationWeighting.UNIFORM_PRICE,
) -> HestonCalibrationProblem:
    numeraire, measure = _market_semantics()
    return HestonCalibrationProblem(
        valuation_date=_VALUATION_DATE,
        spot=_SPOT,
        targets=targets,
        numeraire=numeraire,
        pricing_measure=measure,
        continuous_dividend_yield=_Q,
        bounds=_BOUNDS,
        weighting=weighting,
        forward_method=_FORWARD,
    )


def _method(
    initial_guess: HestonCalibrationCoordinates,
    *,
    max_function_evaluations: int = 250,
) -> ScipyLeastSquaresHestonCalibration:
    return ScipyLeastSquaresHestonCalibration(
        initial_guess=initial_guess,
        max_function_evaluations=max_function_evaluations,
    )


def _assert_recovers_truth(result: object) -> None:
    estimate = result.estimate  # type: ignore[attr-defined]
    assert estimate.initial_variance == pytest.approx(0.04, abs=2.0e-5)
    assert estimate.parameters.mean_reversion_speed == pytest.approx(2.0, abs=2.0e-3)
    assert estimate.parameters.long_run_variance == pytest.approx(0.04, abs=2.0e-5)
    assert estimate.parameters.volatility_of_variance == pytest.approx(0.5, abs=2.0e-3)
    assert estimate.parameters.correlation == pytest.approx(-0.7, abs=2.0e-3)


def _normalized_market_target(
    *,
    bid: float = 7.5,
    ask: float = 8.5,
) -> HestonPriceCalibrationTarget:
    provenance = ObservationProvenance(
        provider="fixture",
        source="M6 deterministic test",
        market_date=_VALUATION_DATE,
        retrieved_at=datetime(2026, 1, 2, tzinfo=UTC),
        license_notes="synthetic fixture",
    )
    underlying = RawUnderlyingObservation(
        underlying_id="TEST",
        value=_SPOT,
        provenance=provenance,
    )
    quote = RawOptionQuote(
        contract_id="TEST-20260702-C-100",
        underlying_id="TEST",
        expiry=_VALUATION_DATE + timedelta(days=182),
        strike=100.0,
        right=OptionRight.CALL,
        exercise_style=OptionExerciseStyle.EUROPEAN,
        provenance=provenance,
        bid=bid,
        ask=ask,
        settlement_time=OptionSettlementTime.PM,
    )
    observation = normalize_european_option_midpoint(quote, underlying)
    return HestonPriceCalibrationTarget.from_normalized_observation(observation)


def test_synthetic_and_market_targets_preserve_distinct_semantics() -> None:
    synthetic_contract = EuropeanOption(
        expiry=_VALUATION_DATE + timedelta(days=182),
        strike=100.0,
        right=OptionRight.CALL,
    )
    synthetic = HestonPriceCalibrationTarget.synthetic(
        contract=synthetic_contract,
        target_price=8.0,
    )
    market = _normalized_market_target()

    assert synthetic.source is HestonCalibrationTargetSource.SYNTHETIC_MODEL
    assert synthetic.observation is None
    assert market.source is HestonCalibrationTargetSource.NORMALIZED_MARKET
    assert market.observation is not None
    assert market.observation.raw_quote.bid == 7.5
    assert market.observation.raw_quote.ask == 8.5


def test_bid_ask_weighting_is_problem_semantics_and_uses_half_spread() -> None:
    target = _normalized_market_target(bid=7.0, ask=9.0)
    problem = _problem(
        (target,),
        weighting=HestonCalibrationWeighting.BID_ASK_HALF_SPREAD,
    )

    assert problem.residual_scale(target) == 1.0
    with pytest.raises(InvalidHestonCalibrationProblem, match="normalized market"):
        _problem(
            (
                HestonPriceCalibrationTarget.synthetic(
                    contract=target.contract,
                    target_price=8.0,
                ),
            ),
            weighting=HestonCalibrationWeighting.BID_ASK_HALF_SPREAD,
        )


def test_initial_guess_outside_financial_domain_is_not_optimizer_convergence() -> None:
    problem = _problem(_synthetic_targets()[:6])
    outside = HestonCalibrationCoordinates(
        initial_variance=0.20,
        parameters=_START_A.parameters,
    )

    with pytest.raises(InvalidHestonCalibrationInitialGuess, match="outside"):
        calibrate_heston(problem, _method(outside))


def test_optimizer_nonconvergence_has_deterministic_failure_semantics() -> None:
    problem = _problem(_synthetic_targets())

    with pytest.raises(HestonCalibrationConvergenceError, match="did not converge"):
        calibrate_heston(
            problem,
            _method(_START_A, max_function_evaluations=1),
        )


def test_noiseless_synthetic_surface_recovers_known_truth_from_multiple_starts() -> None:
    problem = _problem(_synthetic_targets())

    result_a = calibrate_heston(problem, _method(_START_A))
    result_b = calibrate_heston(problem, _method(_START_B))

    _assert_recovers_truth(result_a)
    _assert_recovers_truth(result_b)
    assert result_a.objective_value < 1.0e-8
    assert result_b.objective_value < 1.0e-8
    assert not result_a.conditioning.rank_deficient
    assert result_a.conditioning.condition_number is not None
    assert result_a.conditioning.condition_number > 1.0


def test_thin_slice_can_have_tiny_loss_but_materially_different_parameters() -> None:
    targets = _synthetic_targets()
    thin_problem = _problem((targets[7], targets[8], targets[9]))

    result_a = calibrate_heston(thin_problem, _method(_START_A))
    result_b = calibrate_heston(thin_problem, _method(_START_B))

    assert result_a.objective_value < 1.0e-10
    assert result_b.objective_value < 1.0e-10
    assert result_a.conditioning.rank_deficient
    assert result_b.conditioning.rank_deficient
    assert result_a.conditioning.condition_number is None
    assert result_b.conditioning.condition_number is None
    distance = max(
        abs(left - right)
        for left, right in zip(
            result_a.estimate.as_vector(),
            result_b.estimate.as_vector(),
            strict=True,
        )
    )
    assert distance > 0.1


def test_controlled_price_perturbation_moves_parameters_without_destroying_fit() -> None:
    baseline_targets = _synthetic_targets()
    perturbed = tuple(
        HestonPriceCalibrationTarget.synthetic(
            contract=target.contract,
            target_price=target.target_price + (0.02 if index % 2 == 0 else -0.02),
            label=target.label,
        )
        for index, target in enumerate(baseline_targets)
    )

    result = calibrate_heston(_problem(perturbed), _method(_START_A))

    assert result.objective_value < 0.02
    assert abs(result.estimate.initial_variance - _TRUTH.initial_variance) < 0.005
    assert (
        abs(
            result.estimate.parameters.correlation
            - _TRUTH.parameters.correlation
        )
        > 1.0e-4
    )
