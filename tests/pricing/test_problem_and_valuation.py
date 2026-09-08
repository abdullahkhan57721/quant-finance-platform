from dataclasses import FrozenInstanceError
from typing import assert_type, cast

import pytest

from qf_platform.pricing import (
    ModeledState,
    PhysicalMeasureSemantics,
    PricingMeasureSemantics,
    PricingProblem,
    UnsupportedPricingProblem,
    ValuationResult,
    evaluate,
)
from tests.pricing._fixtures import (
    DeterministicLaw,
    DeterministicParameters,
    FixedPaymentContract,
    FixedPaymentValuation,
    LinearNumeraire,
    RejectingValuation,
    ScalarStateSpace,
    make_problem,
)


def test_pricing_problem_composes_the_question_without_choosing_a_method() -> None:
    problem = make_problem()

    assert problem.valuation_time == 0.0
    assert_type(problem.current_state.value, float)
    assert_type(problem.parameters, DeterministicParameters)
    assert isinstance(problem.contract, FixedPaymentContract)
    assert not hasattr(problem, "valuation_method")

    with pytest.raises(FrozenInstanceError):
        problem.parameters = DeterministicParameters(2.0)  # type: ignore[misc]


def test_pricing_problem_rejects_law_parameter_mismatch() -> None:
    state_space = ScalarStateSpace()
    numeraire = LinearNumeraire(1.0, 0.0)
    pricing_measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)

    with pytest.raises(TypeError, match="parameters are incompatible"):
        PricingProblem[float, float, DeterministicParameters](
            current_state=ModeledState(0.0, 1.0, state_space),
            stochastic_law=DeterministicLaw(state_space),
            parameters=DeterministicParameters(-1.0),
            contract=FixedPaymentContract(1.0, 1.0),
            numeraire=numeraire,
            pricing_measure=pricing_measure,
        )


def test_pricing_problem_rejects_numeraire_measure_mismatch() -> None:
    state_space = ScalarStateSpace()
    problem_numeraire = LinearNumeraire(1.0, 0.0)
    other_numeraire = LinearNumeraire(1.0, 0.0)
    pricing_measure = PricingMeasureSemantics(name="Q^N", numeraire=other_numeraire)

    with pytest.raises(ValueError, match="associated"):
        PricingProblem[float, float, DeterministicParameters](
            current_state=ModeledState(0.0, 1.0, state_space),
            stochastic_law=DeterministicLaw(state_space),
            parameters=DeterministicParameters(1.0),
            contract=FixedPaymentContract(1.0, 1.0),
            numeraire=problem_numeraire,
            pricing_measure=pricing_measure,
        )


def test_pricing_problem_rejects_physical_measure_semantics_at_runtime() -> None:
    state_space = ScalarStateSpace()
    numeraire = LinearNumeraire(1.0, 0.0)
    physical = cast(PricingMeasureSemantics[float], PhysicalMeasureSemantics())

    with pytest.raises(TypeError, match="pricing-measure"):
        PricingProblem[float, float, DeterministicParameters](
            current_state=ModeledState(0.0, 1.0, state_space),
            stochastic_law=DeterministicLaw(state_space),
            parameters=DeterministicParameters(1.0),
            contract=FixedPaymentContract(1.0, 1.0),
            numeraire=numeraire,
            pricing_measure=physical,
        )


def test_compatible_method_values_deterministic_discounted_cash_flow() -> None:
    result = evaluate(make_problem(), FixedPaymentValuation())

    assert result.present_value == pytest.approx(100.0)

    with pytest.raises(FrozenInstanceError):
        result.present_value = 101.0  # type: ignore[misc]


def test_unsupported_method_is_rejected_before_application() -> None:
    with pytest.raises(UnsupportedPricingProblem, match="does not support"):
        evaluate(make_problem(), RejectingValuation())


def test_valuation_result_is_narrow_and_rejects_non_finite_values() -> None:
    result = ValuationResult(3.5)

    assert result.present_value == 3.5
    assert not hasattr(result, "greeks")
    assert not hasattr(result, "confidence_interval")
    assert not hasattr(result, "calibration")

    with pytest.raises(ValueError, match="finite"):
        ValuationResult(float("nan"))
