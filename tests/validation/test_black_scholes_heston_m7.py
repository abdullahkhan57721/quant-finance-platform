from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime
from pathlib import Path
from typing import TypedDict, cast

import pytest

from qf_platform.inference import HestonCalibrationCoordinates
from qf_platform.market_data import (
    NormalizedOptionObservation,
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    RawOptionQuote,
    RawUnderlyingObservation,
    normalize_european_option_midpoint,
)
from qf_platform.pricing import (
    FlatMoneyMarketNumeraire,
    HestonFourierEuropeanOption,
    OptionRight,
    PricingMeasureSemantics,
)
from qf_platform.validation import (
    BlackScholesHestonValidationProblem,
    CrossSectionalBlackScholesHestonValidation,
    InvalidBlackScholesHestonValidationProblem,
    ValidationModel,
    ValidationPartition,
    predeclared_every_third_evaluation_partition,
    validate_black_scholes_vs_heston,
)

_FIXTURE_PATH = (
    Path(__file__).parents[1] / "fixtures" / "m7_spx_validation_observations.json"
)


class _Point(TypedDict):
    expiry: str
    strike: float
    right: str
    midpoint: float
    half_spread: float


class _Fixture(TypedDict):
    fixture_kind: str
    valuation_date: str
    underlying: str
    spot: float
    continuously_compounded_rate: float
    continuous_dividend_yield: float
    points: list[_Point]


def _fixture() -> _Fixture:
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    return cast(_Fixture, payload)


def _observations(
    *,
    evaluation_shift: float = 0.0,
) -> tuple[NormalizedOptionObservation, ...]:
    fixture = _fixture()
    valuation_date = date.fromisoformat(fixture["valuation_date"])
    provenance = ObservationProvenance(
        provider="M7 deterministic fixture",
        source="derived from published M4 evidence; not raw market data",
        market_date=valuation_date,
        retrieved_at=datetime(2026, 9, 10, tzinfo=UTC),
        license_notes="derived CI fixture only",
    )
    underlying = RawUnderlyingObservation(
        underlying_id=fixture["underlying"],
        value=fixture["spot"],
        provenance=provenance,
    )
    observations: list[NormalizedOptionObservation] = []
    for index, point in enumerate(fixture["points"]):
        expiry = date.fromisoformat(point["expiry"])
        right = OptionRight(point["right"])
        midpoint = point["midpoint"]
        if index % 3 == 2:
            midpoint += evaluation_shift
        half_spread = point["half_spread"]
        quote = RawOptionQuote(
            contract_id=(
                f"SPXW-{expiry.isoformat()}-{right.value}-{point['strike']:g}"
            ),
            underlying_id="SPX",
            expiry=expiry,
            strike=point["strike"],
            right=right,
            exercise_style=OptionExerciseStyle.EUROPEAN,
            provenance=provenance,
            bid=midpoint - half_spread,
            ask=midpoint + half_spread,
            settlement_time=OptionSettlementTime.PM,
        )
        observations.append(normalize_european_option_midpoint(quote, underlying))
    return tuple(observations)


def _starts(q: float) -> tuple[HestonCalibrationCoordinates, ...]:
    vectors = (
        (0.04, 2.0, 0.04, 0.5, -0.7),
        (0.06, 1.0, 0.06, 0.8, -0.4),
        (0.02, 5.0, 0.02, 0.3, -0.85),
    )
    return tuple(
        HestonCalibrationCoordinates.from_vector(
            vector,
            continuous_dividend_yield=q,
        )
        for vector in vectors
    )


def _problem(
    observations: tuple[NormalizedOptionObservation, ...] | None = None,
) -> BlackScholesHestonValidationProblem:
    selected = _observations() if observations is None else observations
    fixture = _fixture()
    valuation_date = date.fromisoformat(fixture["valuation_date"])
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=valuation_date,
        continuously_compounded_rate=fixture["continuously_compounded_rate"],
    )
    training, evaluation = predeclared_every_third_evaluation_partition(selected)
    return BlackScholesHestonValidationProblem(
        observations=selected,
        training_contract_ids=training,
        evaluation_contract_ids=evaluation,
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^N", numeraire=numeraire),
        continuous_dividend_yield=fixture["continuous_dividend_yield"],
        heston_forward_method=HestonFourierEuropeanOption(
            integration_upper_bound=100.0,
            intervals=128,
        ),
    )


def _method(*, starts: int = 3) -> CrossSectionalBlackScholesHestonValidation:
    q = _fixture()["continuous_dividend_yield"]
    return CrossSectionalBlackScholesHestonValidation(
        black_scholes_initial_volatility=0.21,
        heston_initial_guesses=_starts(q)[:starts],
        max_function_evaluations=300,
    )


def test_predeclared_partition_is_deterministic_ten_train_four_evaluation() -> None:
    observations = _observations()
    training, evaluation = predeclared_every_third_evaluation_partition(observations)

    assert len(training) == 10
    assert len(evaluation) == 4
    assert evaluation == (
        "SPXW-2023-02-03-put-3850",
        "SPXW-2023-02-03-call-3970",
        "SPXW-2023-04-28-put-3800",
        "SPXW-2023-04-28-call-4075",
    )


def test_validation_problem_rejects_overlap_and_unassigned_observations() -> None:
    problem = _problem()
    with pytest.raises(InvalidBlackScholesHestonValidationProblem, match="overlap"):
        BlackScholesHestonValidationProblem(
            observations=problem.observations,
            training_contract_ids=problem.training_contract_ids,
            evaluation_contract_ids=(problem.training_contract_ids[0],),
            numeraire=problem.numeraire,
            pricing_measure=problem.pricing_measure,
            continuous_dividend_yield=problem.continuous_dividend_yield,
        )

    with pytest.raises(InvalidBlackScholesHestonValidationProblem, match="assigned"):
        BlackScholesHestonValidationProblem(
            observations=problem.observations,
            training_contract_ids=problem.training_contract_ids[:-1],
            evaluation_contract_ids=problem.evaluation_contract_ids,
            numeraire=problem.numeraire,
            pricing_measure=problem.pricing_measure,
            continuous_dividend_yield=problem.continuous_dividend_yield,
        )


def test_spx_cross_section_heston_improves_predeclared_held_out_evidence() -> None:
    evidence = validate_black_scholes_vs_heston(_problem(), _method())

    assert evidence.black_scholes_fit.annualized_volatility == pytest.approx(
        0.209,
        abs=0.005,
    )
    assert evidence.black_scholes_training_metrics.observation_count == 10
    assert evidence.black_scholes_evaluation_metrics.observation_count == 4
    assert evidence.heston_training_metrics.observation_count == 10
    assert evidence.heston_evaluation_metrics.observation_count == 4
    assert (
        evidence.heston_evaluation_metrics.root_mean_square_error
        < 0.25 * evidence.black_scholes_evaluation_metrics.root_mean_square_error
    )
    assert (
        evidence.heston_evaluation_metrics.standardized_root_mean_square_error
        < 0.25
        * evidence.black_scholes_evaluation_metrics.standardized_root_mean_square_error
    )
    assert evidence.conclusion.heston_lower_training_price_rmse
    assert evidence.conclusion.heston_lower_evaluation_price_rmse
    assert evidence.conclusion.heston_lower_evaluation_standardized_rmse
    assert not evidence.conclusion.temporal_out_of_sample_tested
    assert not evidence.conclusion.heston_hedge_comparison_supported
    assert evidence.heston_stability.successful_training_starts == 3
    assert evidence.heston_stability.training_jacobian_rank == 5
    assert evidence.heston_stability.training_condition_number is not None
    assert evidence.heston_stability.training_condition_number > 50.0
    assert evidence.heston_stability.maximum_train_to_full_domain_scaled_shift < 0.1
    assert evidence.computation.heston_training_target_count == 10
    assert evidence.computation.heston_full_sample_target_count == 14


def test_evaluation_quotes_cannot_change_training_fitted_models() -> None:
    baseline = validate_black_scholes_vs_heston(_problem(), _method(starts=1))
    shifted = validate_black_scholes_vs_heston(
        _problem(_observations(evaluation_shift=2.0)),
        _method(starts=1),
    )

    assert shifted.black_scholes_fit.annualized_volatility == pytest.approx(
        baseline.black_scholes_fit.annualized_volatility,
        abs=1.0e-12,
    )
    assert (
        shifted.selected_heston_training_result.estimate.as_vector()
        == pytest.approx(
            baseline.selected_heston_training_result.estimate.as_vector(),
            abs=1.0e-10,
        )
    )
    baseline_eval_prices = {
        (item.contract_id, item.model): item.model_price
        for item in baseline.residuals
        if item.partition is ValidationPartition.EVALUATION
    }
    shifted_eval_prices = {
        (item.contract_id, item.model): item.model_price
        for item in shifted.residuals
        if item.partition is ValidationPartition.EVALUATION
    }
    assert shifted_eval_prices.keys() == baseline_eval_prices.keys()
    for key, baseline_price in baseline_eval_prices.items():
        assert shifted_eval_prices[key] == pytest.approx(baseline_price, abs=1.0e-10)
    assert (
        shifted.heston_evaluation_metrics.root_mean_square_error
        != baseline.heston_evaluation_metrics.root_mean_square_error
    )
    assert (
        shifted.selected_heston_full_sample_result.estimate.as_vector()
        != pytest.approx(
            baseline.selected_heston_full_sample_result.estimate.as_vector(),
            abs=1.0e-8,
        )
    )


def test_validation_evidence_is_immutable_and_retains_contract_structure() -> None:
    evidence = validate_black_scholes_vs_heston(_problem(), _method(starts=1))

    assert len(evidence.residuals) == 28
    assert {item.model for item in evidence.residuals} == {
        ValidationModel.BLACK_SCHOLES,
        ValidationModel.HESTON,
    }
    assert {item.partition for item in evidence.residuals} == {
        ValidationPartition.TRAINING,
        ValidationPartition.EVALUATION,
    }
    with pytest.raises(FrozenInstanceError):
        evidence.black_scholes_fit.annualized_volatility = 0.5  # pyright: ignore[reportAttributeAccessIssue]
