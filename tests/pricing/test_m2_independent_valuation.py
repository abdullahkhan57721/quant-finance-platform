from __future__ import annotations

from datetime import date
from math import exp

import pytest

from qf_platform.pricing.black_scholes import BlackScholesLaw, BlackScholesParameters
from qf_platform.pricing.black_scholes_valuation import BlackScholesClosedForm
from qf_platform.pricing.crr import CoxRossRubinstein
from qf_platform.pricing.equity import (
    EquityState,
    EquityStateSpace,
    EuropeanOption,
    OptionRight,
)
from qf_platform.pricing.measures import PricingMeasureSemantics
from qf_platform.pricing.monte_carlo import (
    MonteCarloEuropeanOption,
    MonteCarloValuationResult,
)
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState
from qf_platform.pricing.valuation import UnsupportedPricingProblem, evaluate

VALUATION_DATE = date(2026, 1, 1)
ONE_YEAR = date(2027, 1, 1)


def make_problem(
    right: OptionRight = OptionRight.CALL,
    *,
    spot: float = 100.0,
    strike: float = 100.0,
    rate: float = 0.05,
    dividend_yield: float = 0.0,
    volatility: float = 0.20,
    valuation_date: date = VALUATION_DATE,
    expiry: date = ONE_YEAR,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    state_space = EquityStateSpace()
    law = BlackScholesLaw(state_space=state_space)
    parameters = BlackScholesParameters(
        annualized_volatility=volatility,
        continuous_dividend_yield=dividend_yield,
    )
    current_state = ModeledState(
        time=valuation_date,
        value=EquityState(spot),
        state_space=state_space,
    )
    contract = EuropeanOption(expiry=expiry, strike=strike, right=right)
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=valuation_date,
        continuously_compounded_rate=rate,
    )
    pricing_measure = PricingMeasureSemantics(name="Q^B", numeraire=numeraire)
    return PricingProblem(
        current_state=current_state,
        stochastic_law=law,
        parameters=parameters,
        contract=contract,
        numeraire=numeraire,
        pricing_measure=pricing_measure,
    )


@pytest.mark.parametrize("steps", [0, -1])
def test_crr_requires_positive_steps(steps: int) -> None:
    with pytest.raises(ValueError):
        CoxRossRubinstein(steps)


def test_crr_rejects_noninteger_steps() -> None:
    with pytest.raises(TypeError):
        CoxRossRubinstein(10.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        CoxRossRubinstein(True)


def test_crr_converges_toward_black_scholes_reference() -> None:
    problem = make_problem()
    reference = evaluate(problem, BlackScholesClosedForm()).present_value
    step_counts = (50, 100, 200, 400, 800, 1600)
    errors = [
        abs(evaluate(problem, CoxRossRubinstein(steps)).present_value - reference)
        for steps in step_counts
    ]

    assert errors[-1] < 0.0013
    assert errors[-1] < errors[0] / 25.0
    assert all(
        later < earlier
        for earlier, later in zip(errors, errors[1:], strict=False)
    )


def test_crr_support_boundary_exposes_discrete_no_arbitrage_condition() -> None:
    problem = make_problem(rate=0.50, volatility=0.01)
    method = CoxRossRubinstein(steps=1)

    assert evaluate(problem, BlackScholesClosedForm()).present_value > 0.0
    assert not method.supports(problem)
    with pytest.raises(UnsupportedPricingProblem, match="does not support"):
        evaluate(problem, method)


def test_crr_expiry_and_zero_volatility_limits_are_deterministic() -> None:
    expiry_problem = make_problem(spot=120.0, expiry=VALUATION_DATE)
    assert evaluate(expiry_problem, CoxRossRubinstein(20)).present_value == 20.0

    deterministic = make_problem(
        spot=100.0,
        strike=95.0,
        rate=0.05,
        dividend_yield=0.02,
        volatility=0.0,
    )
    expected = max(100.0 * exp(-0.02) - 95.0 * exp(-0.05), 0.0)
    assert evaluate(
        deterministic,
        CoxRossRubinstein(100),
    ).present_value == pytest.approx(expected, abs=2e-13)


def test_monte_carlo_requires_explicit_valid_path_count_and_seed() -> None:
    with pytest.raises(ValueError):
        MonteCarloEuropeanOption(paths=1, seed=7)
    with pytest.raises(TypeError):
        MonteCarloEuropeanOption(paths=1000.0, seed=7)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        MonteCarloEuropeanOption(paths=1000, seed=True)


def test_monte_carlo_result_preserves_sampling_evidence_and_concrete_type() -> None:
    problem = make_problem()
    method = MonteCarloEuropeanOption(paths=50_000, seed=1729)

    result: MonteCarloValuationResult = evaluate(problem, method)
    repeated = evaluate(problem, method)

    assert result == repeated
    assert result.paths == 50_000
    assert result.seed == 1729
    assert result.standard_error > 0.0
    lower, upper = result.confidence_interval_95
    assert lower < result.present_value < upper
    assert upper - result.present_value == pytest.approx(
        1.959963984540054 * result.standard_error,
        rel=1e-13,
    )


def test_monte_carlo_reference_is_consistent_with_reported_sampling_uncertainty() -> None:
    problem = make_problem()
    analytic = evaluate(problem, BlackScholesClosedForm()).present_value
    result = evaluate(problem, MonteCarloEuropeanOption(paths=50_000, seed=1729))

    lower, upper = result.confidence_interval_95
    assert lower < analytic < upper
    assert abs(result.present_value - analytic) < 2.0 * result.standard_error


def test_monte_carlo_standard_error_has_inverse_square_root_path_scaling() -> None:
    problem = make_problem()
    small = evaluate(problem, MonteCarloEuropeanOption(paths=10_000, seed=1729))
    large = evaluate(problem, MonteCarloEuropeanOption(paths=40_000, seed=1729))

    ratio = large.standard_error / small.standard_error
    assert ratio == pytest.approx(0.5, abs=0.03)


def test_monte_carlo_zero_volatility_has_zero_sampling_uncertainty() -> None:
    problem = make_problem(volatility=0.0, strike=95.0, dividend_yield=0.02)
    result = evaluate(problem, MonteCarloEuropeanOption(paths=1000, seed=12))
    analytic = evaluate(problem, BlackScholesClosedForm()).present_value

    assert result.present_value == pytest.approx(analytic, abs=2e-13)
    assert result.standard_error == 0.0
    assert result.confidence_interval_95 == (
        result.present_value,
        result.present_value,
    )
