from __future__ import annotations

from datetime import date, timedelta

import pytest

from qf_platform.control import (
    BlackScholesDeltaHedgeProblem,
    BlackScholesPathSimulation,
    run_delta_hedge,
    simulate_black_scholes_path,
    summarize_replication_errors,
)
from qf_platform.pricing import (
    BlackScholesLaw,
    BlackScholesParameters,
    EquityState,
    EquityStateSpace,
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
)

_VALUATION_DATE = date(2026, 1, 1)
_EXPIRY_DATE = date(2027, 1, 1)


def _pricing_problem() -> PricingProblem[date, EquityState, BlackScholesParameters]:
    state_space = EquityStateSpace()
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=0.05,
    )
    return PricingProblem(
        current_state=ModeledState(
            time=_VALUATION_DATE,
            value=EquityState(100.0),
            state_space=state_space,
        ),
        stochastic_law=BlackScholesLaw(state_space=state_space),
        parameters=BlackScholesParameters(annualized_volatility=0.20),
        contract=EuropeanOption(
            expiry=_EXPIRY_DATE,
            strike=100.0,
            right=OptionRight.CALL,
        ),
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^B", numeraire=numeraire),
    )


def _result(*, seed: int, observation_dates: tuple[date, ...]):
    pricing_problem = _pricing_problem()
    path = simulate_black_scholes_path(
        BlackScholesPathSimulation.from_pricing_problem(
            pricing_problem,
            observation_dates=observation_dates,
            seed=seed,
        )
    )
    hedge_problem = BlackScholesDeltaHedgeProblem(
        pricing_problem=pricing_problem,
        rebalance_dates=(_VALUATION_DATE,),
    )
    return run_delta_hedge(hedge_problem, path)


def test_summary_rejects_duplicate_seed_replicates() -> None:
    dates = (_VALUATION_DATE, _EXPIRY_DATE)
    first = _result(seed=7, observation_dates=dates)
    duplicate_seed = _result(seed=7, observation_dates=dates)

    with pytest.raises(ValueError, match="distinct seeds"):
        summarize_replication_errors((first, duplicate_seed))


def test_summary_rejects_equal_length_but_different_observation_grids() -> None:
    first_dates = (
        _VALUATION_DATE,
        _VALUATION_DATE + timedelta(days=180),
        _EXPIRY_DATE,
    )
    second_dates = (
        _VALUATION_DATE,
        _VALUATION_DATE + timedelta(days=181),
        _EXPIRY_DATE,
    )
    first = _result(seed=7, observation_dates=first_dates)
    different_grid = _result(seed=8, observation_dates=second_dates)

    with pytest.raises(ValueError, match="one common hedge study condition"):
        summarize_replication_errors((first, different_grid))
