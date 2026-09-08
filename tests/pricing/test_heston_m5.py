from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
from math import exp, sqrt
from typing import cast

import pytest

from qf_platform.pricing import (
    BlackScholesClosedForm,
    BlackScholesLaw,
    BlackScholesParameters,
    EquityState,
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    HestonEquityState,
    HestonFourierEuropeanOption,
    HestonLaw,
    HestonMonteCarloEuropeanOption,
    HestonParameters,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
    UnsupportedPricingProblem,
    evaluate,
)

_VALUATION_DATE = date(2026, 1, 1)
_EXPIRY = date(2027, 1, 1)


def _heston_problem(
    *,
    right: OptionRight = OptionRight.CALL,
    spot: float = 100.0,
    strike: float = 100.0,
    initial_variance: float = 0.04,
    mean_reversion_speed: float = 2.0,
    long_run_variance: float = 0.04,
    volatility_of_variance: float = 0.5,
    correlation: float = -0.7,
    dividend_yield: float = 0.01,
    rate: float = 0.03,
    expiry: date = _EXPIRY,
) -> PricingProblem[date, HestonEquityState, HestonParameters]:
    law = HestonLaw()
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=rate,
    )
    measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
    return PricingProblem(
        current_state=ModeledState(
            time=_VALUATION_DATE,
            value=HestonEquityState(
                spot=spot,
                instantaneous_variance=initial_variance,
            ),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=HestonParameters(
            mean_reversion_speed=mean_reversion_speed,
            long_run_variance=long_run_variance,
            volatility_of_variance=volatility_of_variance,
            correlation=correlation,
            continuous_dividend_yield=dividend_yield,
        ),
        contract=EuropeanOption(expiry=expiry, strike=strike, right=right),
        numeraire=numeraire,
        pricing_measure=measure,
    )


def _black_scholes_problem(
    *,
    right: OptionRight,
    volatility: float,
    rate: float = 0.03,
    dividend_yield: float = 0.01,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    law = BlackScholesLaw()
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=rate,
    )
    measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
    return PricingProblem(
        current_state=ModeledState(
            time=_VALUATION_DATE,
            value=EquityState(100.0),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=BlackScholesParameters(
            annualized_volatility=volatility,
            continuous_dividend_yield=dividend_yield,
        ),
        contract=EuropeanOption(expiry=_EXPIRY, strike=100.0, right=right),
        numeraire=numeraire,
        pricing_measure=measure,
    )


def test_heston_state_refines_equity_state_and_parameters_are_immutable() -> None:
    state = HestonEquityState(spot=100.0, instantaneous_variance=0.04)
    parameters = HestonParameters(
        mean_reversion_speed=2.0,
        long_run_variance=0.04,
        volatility_of_variance=0.3,
        correlation=-0.6,
    )

    assert isinstance(state, EquityState)
    assert state.spot == 100.0
    assert state.instantaneous_variance == 0.04
    assert parameters.feller_condition_satisfied
    with pytest.raises(FrozenInstanceError):
        state.instantaneous_variance = 0.09  # type: ignore


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ((0.0, 0.04, 0.3, -0.6), "strictly positive"),
        ((2.0, -0.01, 0.3, -0.6), "non-negative"),
        ((2.0, 0.04, -0.01, -0.6), "non-negative"),
        ((2.0, 0.04, 0.3, 1.01), "correlation must lie"),
    ],
)
def test_heston_parameter_domain_is_explicit(
    values: tuple[float, float, float, float],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        HestonParameters(
            mean_reversion_speed=values[0],
            long_run_variance=values[1],
            volatility_of_variance=values[2],
            correlation=values[3],
        )


def test_feller_violation_is_diagnostic_not_structural_rejection() -> None:
    problem = _heston_problem(volatility_of_variance=0.5)

    assert not problem.parameters.feller_condition_satisfied
    result = evaluate(problem, HestonFourierEuropeanOption(intervals=512))

    assert result.present_value > 0.0


def test_heston_fourier_non_degenerate_regression_and_diagnostics() -> None:
    result = evaluate(_heston_problem(), HestonFourierEuropeanOption())

    assert result.present_value == pytest.approx(8.2528489705, abs=2.0e-8)
    assert result.intervals == 2048
    assert result.integration_lower_bound == 1.0e-8
    assert result.integration_upper_bound == 100.0
    assert result.characteristic_function_evaluations == 4099


def test_heston_fourier_converges_under_finer_integration_configuration() -> None:
    problem = _heston_problem()
    coarse = evaluate(
        problem,
        HestonFourierEuropeanOption(
            integration_upper_bound=75.0,
            intervals=512,
        ),
    )
    fine = evaluate(
        problem,
        HestonFourierEuropeanOption(
            integration_upper_bound=125.0,
            intervals=2048,
        ),
    )

    assert coarse.present_value == pytest.approx(fine.present_value, abs=5.0e-5)


def test_heston_fourier_put_call_parity_uses_existing_rate_carry_conventions() -> None:
    call = evaluate(
        _heston_problem(right=OptionRight.CALL),
        HestonFourierEuropeanOption(intervals=1024),
    ).present_value
    put = evaluate(
        _heston_problem(right=OptionRight.PUT),
        HestonFourierEuropeanOption(intervals=1024),
    ).present_value
    expected_difference = 100.0 * exp(-0.01) - 100.0 * exp(-0.03)

    assert call - put == pytest.approx(expected_difference, abs=2.0e-10)


def test_zero_vol_of_variance_matches_independent_black_scholes_limit() -> None:
    initial_variance = 0.04
    theta = 0.09
    kappa = 1.7
    year_fraction = 1.0
    integrated_variance = (
        theta * year_fraction
        + (initial_variance - theta) * (1.0 - exp(-kappa * year_fraction)) / kappa
    )
    effective_volatility = sqrt(integrated_variance / year_fraction)

    heston = evaluate(
        _heston_problem(
            initial_variance=initial_variance,
            mean_reversion_speed=kappa,
            long_run_variance=theta,
            volatility_of_variance=0.0,
            correlation=-0.7,
        ),
        HestonFourierEuropeanOption(),
    )
    black_scholes = evaluate(
        _black_scholes_problem(
            right=OptionRight.CALL,
            volatility=effective_volatility,
        ),
        BlackScholesClosedForm(),
    )

    assert heston.present_value == pytest.approx(
        black_scholes.present_value,
        abs=2.0e-13,
    )
    assert heston.characteristic_function_evaluations == 0


def test_heston_expiry_and_zero_spot_boundaries_are_deterministic() -> None:
    expiry_value = evaluate(
        _heston_problem(spot=120.0, strike=100.0, expiry=_VALUATION_DATE),
        HestonFourierEuropeanOption(),
    )
    zero_spot_put = evaluate(
        _heston_problem(spot=0.0, right=OptionRight.PUT),
        HestonFourierEuropeanOption(),
    )

    assert expiry_value.present_value == 20.0
    assert expiry_value.characteristic_function_evaluations == 0
    assert zero_spot_put.present_value == pytest.approx(100.0 * exp(-0.03))


def test_heston_monte_carlo_is_reproducible_and_records_boundary_pressure() -> None:
    problem = _heston_problem()
    method = HestonMonteCarloEuropeanOption(paths=1500, time_steps=32, seed=17)

    first = evaluate(problem, method)
    second = evaluate(problem, method)

    assert first == second
    assert first.standard_error > 0.0
    assert first.negative_variance_proposals > 0
    assert first.variance_scheme == "full_truncation_euler"
    assert first.time_steps == 32


def test_heston_monte_carlo_agrees_with_fourier_with_sampling_and_bias_allowance() -> (
    None
):
    problem = _heston_problem()
    fourier = evaluate(
        problem,
        HestonFourierEuropeanOption(intervals=1024),
    )
    monte_carlo = evaluate(
        problem,
        HestonMonteCarloEuropeanOption(
            paths=10_000,
            time_steps=128,
            seed=123,
        ),
    )

    allowed_difference = 4.0 * monte_carlo.standard_error + 0.05
    assert abs(monte_carlo.present_value - fourier.present_value) <= allowed_difference
    assert monte_carlo.confidence_interval_95[0] < monte_carlo.present_value
    assert monte_carlo.present_value < monte_carlo.confidence_interval_95[1]


def test_zero_vol_of_variance_monte_carlo_uses_exact_variance_boundary() -> None:
    problem = _heston_problem(
        initial_variance=0.04,
        long_run_variance=0.09,
        mean_reversion_speed=1.7,
        volatility_of_variance=0.0,
    )
    analytic = evaluate(problem, HestonFourierEuropeanOption()).present_value
    monte_carlo = evaluate(
        problem,
        HestonMonteCarloEuropeanOption(paths=5000, time_steps=4, seed=9),
    )

    assert monte_carlo.negative_variance_proposals == 0
    assert monte_carlo.variance_scheme == "exact_deterministic_variance"
    assert abs(monte_carlo.present_value - analytic) <= 4.0 * monte_carlo.standard_error


def test_heston_methods_reject_black_scholes_pricing_problem() -> None:
    black_scholes_problem = _black_scholes_problem(
        right=OptionRight.CALL,
        volatility=0.2,
    )
    incompatible_problem = cast(
        PricingProblem[date, HestonEquityState, HestonParameters],
        black_scholes_problem,
    )

    with pytest.raises(UnsupportedPricingProblem):
        evaluate(incompatible_problem, HestonFourierEuropeanOption())
    with pytest.raises(UnsupportedPricingProblem):
        evaluate(
            incompatible_problem,
            HestonMonteCarloEuropeanOption(paths=10, time_steps=2, seed=1),
        )
