from __future__ import annotations

from datetime import date

import numpy as np

from qf_platform.pricing import (
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    HestonEquityState,
    HestonLaw,
    HestonMonteCarloEuropeanOption,
    HestonParameters,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
    evaluate,
)


def _problem() -> PricingProblem[date, HestonEquityState, HestonParameters]:
    valuation_date = date(2026, 1, 1)
    law = HestonLaw()
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=valuation_date,
        continuously_compounded_rate=0.03,
    )
    return PricingProblem(
        current_state=ModeledState(
            time=valuation_date,
            value=HestonEquityState(spot=100.0, instantaneous_variance=0.04),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=HestonParameters(
            mean_reversion_speed=2.0,
            long_run_variance=0.04,
            volatility_of_variance=0.5,
            correlation=-0.7,
            continuous_dividend_yield=0.01,
        ),
        contract=EuropeanOption(date(2027, 1, 1), 100.0, OptionRight.CALL),
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^N", numeraire=numeraire),
    )


def test_heston_monte_carlo_seed_is_owned_locally_not_by_global_numpy_state() -> None:
    problem = _problem()
    method = HestonMonteCarloEuropeanOption(paths=2_000, time_steps=32, seed=20260910)

    np.random.seed(17)
    first = evaluate(problem, method)
    _ = np.random.standard_normal(10_000)
    np.random.seed(999)
    second = evaluate(problem, method)

    assert second == first
