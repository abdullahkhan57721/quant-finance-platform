from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from qf_platform.pricing.black_scholes import BlackScholesLaw, BlackScholesParameters
from qf_platform.pricing.equity import (
    EquityState,
    EquityStateSpace,
    EuropeanOption,
    OptionRight,
)
from qf_platform.pricing.measures import PricingMeasureSemantics
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState
from qf_platform.sensitivity.black_scholes import (
    AnalyticBlackScholesSensitivity,
    BlackScholesSensitivity,
    BlackScholesSensitivityProblem,
    BlackScholesSensitivityResult,
    BlackScholesVariable,
    FiniteDifferenceBlackScholesSensitivity,
    UnsupportedSensitivityProblem,
    evaluate_sensitivity,
)

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


def sensitivity_value(
    sensitivity: BlackScholesSensitivity,
    *,
    right: OptionRight = OptionRight.CALL,
    method: AnalyticBlackScholesSensitivity
    | FiniteDifferenceBlackScholesSensitivity
    | None = None,
    **problem_kwargs: float | date,
) -> float:
    problem = BlackScholesSensitivityProblem(
        pricing_problem=make_problem(right, **problem_kwargs),  # type: ignore[arg-type]
        sensitivity=sensitivity,
    )
    selected_method = method or AnalyticBlackScholesSensitivity()
    return evaluate_sensitivity(problem, selected_method).value


@pytest.mark.parametrize(
    ("right", "sensitivity", "expected"),
    [
        (OptionRight.CALL, BlackScholesSensitivity.DELTA, 0.6368306511756191),
        (OptionRight.PUT, BlackScholesSensitivity.DELTA, -0.3631693488243809),
        (OptionRight.CALL, BlackScholesSensitivity.GAMMA, 0.018762017345846895),
        (OptionRight.PUT, BlackScholesSensitivity.GAMMA, 0.018762017345846895),
        (OptionRight.CALL, BlackScholesSensitivity.VEGA, 37.52403469169379),
        (OptionRight.PUT, BlackScholesSensitivity.VEGA, 37.52403469169379),
        (OptionRight.CALL, BlackScholesSensitivity.THETA, -6.414027546438197),
        (OptionRight.PUT, BlackScholesSensitivity.THETA, -1.657880423934626),
        (OptionRight.CALL, BlackScholesSensitivity.RHO, 53.232481545376345),
        (OptionRight.PUT, BlackScholesSensitivity.RHO, -41.89046090469506),
    ],
)
def test_analytic_greeks_match_reference_values(
    right: OptionRight,
    sensitivity: BlackScholesSensitivity,
    expected: float,
) -> None:
    assert sensitivity_value(sensitivity, right=right) == pytest.approx(
        expected,
        rel=0.0,
        abs=2e-12,
    )


def test_sensitivity_metadata_makes_variable_order_and_units_explicit() -> None:
    gamma = BlackScholesSensitivityResult(BlackScholesSensitivity.GAMMA, 0.02)
    vega = BlackScholesSensitivityResult(BlackScholesSensitivity.VEGA, 40.0)
    theta = BlackScholesSensitivityResult(BlackScholesSensitivity.THETA, -5.0)
    rho = BlackScholesSensitivityResult(BlackScholesSensitivity.RHO, 50.0)

    assert gamma.variable is BlackScholesVariable.SPOT
    assert gamma.derivative_order == 2
    assert "squared" in gamma.units
    assert vega.derivative_order == 1
    assert "1.00 annualized volatility decimal" in vega.units
    assert "ACT/365F model year" in theta.units
    assert "1.00 continuously compounded rate decimal" in rho.units


def test_problem_method_and_result_are_distinct_immutable_responsibilities() -> None:
    problem = BlackScholesSensitivityProblem(
        make_problem(),
        BlackScholesSensitivity.DELTA,
    )
    method = AnalyticBlackScholesSensitivity()
    result = evaluate_sensitivity(problem, method)

    assert isinstance(problem, BlackScholesSensitivityProblem)
    assert isinstance(method, AnalyticBlackScholesSensitivity)
    assert isinstance(result, BlackScholesSensitivityResult)
    with pytest.raises(FrozenInstanceError):
        result.value = 0.0  # type: ignore[misc]


@pytest.mark.parametrize(
    ("sensitivity", "absolute_tolerance"),
    [
        (BlackScholesSensitivity.DELTA, 2e-6),
        (BlackScholesSensitivity.GAMMA, 5e-7),
        (BlackScholesSensitivity.VEGA, 5e-5),
        (BlackScholesSensitivity.THETA, 1e-5),
        (BlackScholesSensitivity.RHO, 2e-6),
    ],
)
@pytest.mark.parametrize("right", [OptionRight.CALL, OptionRight.PUT])
def test_finite_differences_cross_validate_analytic_greeks(
    right: OptionRight,
    sensitivity: BlackScholesSensitivity,
    absolute_tolerance: float,
) -> None:
    pricing_problem = make_problem(right)
    problem = BlackScholesSensitivityProblem(pricing_problem, sensitivity)
    analytic = evaluate_sensitivity(problem, AnalyticBlackScholesSensitivity())
    numerical = evaluate_sensitivity(
        problem,
        FiniteDifferenceBlackScholesSensitivity(),
    )

    assert numerical.value == pytest.approx(
        analytic.value,
        rel=0.0,
        abs=absolute_tolerance,
    )


def test_gamma_bump_study_exposes_truncation_then_cancellation() -> None:
    pricing_problem = make_problem()
    problem = BlackScholesSensitivityProblem(
        pricing_problem,
        BlackScholesSensitivity.GAMMA,
    )
    analytic = evaluate_sensitivity(problem, AnalyticBlackScholesSensitivity()).value

    coarse = evaluate_sensitivity(
        problem,
        FiniteDifferenceBlackScholesSensitivity(spot_bump=5.0),
    ).value
    balanced = evaluate_sensitivity(
        problem,
        FiniteDifferenceBlackScholesSensitivity(spot_bump=0.01),
    ).value
    cancellation_dominated = evaluate_sensitivity(
        problem,
        FiniteDifferenceBlackScholesSensitivity(spot_bump=1e-6),
    ).value

    coarse_error = abs(coarse - analytic)
    balanced_error = abs(balanced - analytic)
    cancellation_error = abs(cancellation_dominated - analytic)

    assert balanced_error < coarse_error / 1000.0
    assert balanced_error < cancellation_error / 1000.0


def test_analytic_sensitivities_reject_nondifferentiable_pricing_boundaries() -> None:
    method = AnalyticBlackScholesSensitivity()
    zero_volatility = BlackScholesSensitivityProblem(
        make_problem(volatility=0.0),
        BlackScholesSensitivity.DELTA,
    )
    at_expiry = BlackScholesSensitivityProblem(
        make_problem(expiry=VALUATION_DATE),
        BlackScholesSensitivity.DELTA,
    )

    assert not method.supports(zero_volatility)
    assert not method.supports(at_expiry)
    with pytest.raises(UnsupportedSensitivityProblem, match="interior"):
        evaluate_sensitivity(zero_volatility, method)


def test_finite_difference_support_rejects_bumps_that_cross_domains() -> None:
    spot_problem = BlackScholesSensitivityProblem(
        make_problem(spot=0.05),
        BlackScholesSensitivity.DELTA,
    )
    volatility_problem = BlackScholesSensitivityProblem(
        make_problem(volatility=0.0005),
        BlackScholesSensitivity.VEGA,
    )

    assert not FiniteDifferenceBlackScholesSensitivity(
        spot_bump=0.1
    ).supports(spot_problem)
    assert not FiniteDifferenceBlackScholesSensitivity(
        volatility_bump=0.001
    ).supports(volatility_problem)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"spot_bump": 0.0},
        {"volatility_bump": -0.1},
        {"rate_bump": float("inf")},
        {"theta_day_bump": 0},
    ],
)
def test_finite_difference_configuration_requires_positive_finite_bumps(
    kwargs: dict[str, float | int],
) -> None:
    with pytest.raises(ValueError):
        FiniteDifferenceBlackScholesSensitivity(**kwargs)  # type: ignore[arg-type]
