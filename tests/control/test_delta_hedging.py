from __future__ import annotations

from datetime import date, timedelta
from math import exp

import pytest

from qf_platform.control import (
    AnalyticDeltaHedgePolicy,
    BlackScholesDeltaHedgeProblem,
    BlackScholesPathSimulation,
    DeltaHedgeResult,
    EquityPathPoint,
    ReplicationErrorSummary,
    SimulatedEquityPath,
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
from qf_platform.sensitivity import (
    AnalyticBlackScholesSensitivity,
    BlackScholesSensitivity,
    BlackScholesSensitivityProblem,
    evaluate_sensitivity,
)

_VALUATION_DATE = date(2026, 1, 1)
_EXPIRY_DATE = date(2027, 1, 1)


def _pricing_problem(
    *,
    volatility: float = 0.20,
    dividend_yield: float = 0.0,
    right: OptionRight = OptionRight.CALL,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    state_space = EquityStateSpace()
    law = BlackScholesLaw(state_space=state_space)
    parameters = BlackScholesParameters(
        annualized_volatility=volatility,
        continuous_dividend_yield=dividend_yield,
    )
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=0.05,
    )
    pricing_measure = PricingMeasureSemantics(name="Q^B", numeraire=numeraire)
    return PricingProblem(
        current_state=ModeledState(
            time=_VALUATION_DATE,
            value=EquityState(100.0),
            state_space=state_space,
        ),
        stochastic_law=law,
        parameters=parameters,
        contract=EuropeanOption(
            expiry=_EXPIRY_DATE,
            strike=100.0,
            right=right,
        ),
        numeraire=numeraire,
        pricing_measure=pricing_measure,
    )


def _daily_dates() -> tuple[date, ...]:
    days = (_EXPIRY_DATE - _VALUATION_DATE).days
    return tuple(_VALUATION_DATE + timedelta(days=offset) for offset in range(days + 1))


def _rebalance_dates(
    observation_dates: tuple[date, ...], every_days: int
) -> tuple[date, ...]:
    return observation_dates[:-1:every_days]


def _simulated_path(
    *,
    seed: int,
    generating_volatility: float = 0.20,
    observation_dates: tuple[date, ...] | None = None,
) -> SimulatedEquityPath:
    dates = observation_dates if observation_dates is not None else _daily_dates()
    simulation = BlackScholesPathSimulation.from_pricing_problem(
        _pricing_problem(volatility=generating_volatility),
        observation_dates=dates,
        seed=seed,
    )
    return simulate_black_scholes_path(simulation)


def _hedge_result(
    *,
    seed: int,
    every_days: int,
    generating_volatility: float = 0.20,
    hedging_volatility: float = 0.20,
    transaction_cost_rate: float = 0.0,
) -> DeltaHedgeResult:
    dates = _daily_dates()
    path = _simulated_path(
        seed=seed,
        generating_volatility=generating_volatility,
        observation_dates=dates,
    )
    problem = BlackScholesDeltaHedgeProblem(
        pricing_problem=_pricing_problem(volatility=hedging_volatility),
        rebalance_dates=_rebalance_dates(dates, every_days),
        proportional_transaction_cost_rate=transaction_cost_rate,
    )
    return run_delta_hedge(problem, path)


def _study_summary(
    *,
    every_days: int,
    generating_volatility: float = 0.20,
    hedging_volatility: float = 0.20,
    replicate_count: int = 64,
) -> ReplicationErrorSummary:
    results = tuple(
        _hedge_result(
            seed=seed,
            every_days=every_days,
            generating_volatility=generating_volatility,
            hedging_volatility=hedging_volatility,
        )
        for seed in range(replicate_count)
    )
    return summarize_replication_errors(results)


def test_exact_transition_path_is_seeded_and_reproducible() -> None:
    first = _simulated_path(seed=17)
    repeated = _simulated_path(seed=17)
    different = _simulated_path(seed=18)

    assert first == repeated
    assert first.points != different.points
    assert first.seed == 17
    assert first.value_at(_EXPIRY_DATE).spot == first.points[-1].spot


def test_zero_volatility_path_matches_deterministic_money_market_drift() -> None:
    coarse_dates = (_VALUATION_DATE, _EXPIRY_DATE)
    path = _simulated_path(
        seed=11,
        generating_volatility=0.0,
        observation_dates=coarse_dates,
    )

    expected_terminal_spot = 100.0 * exp(0.05)
    assert path.points[-1].spot == pytest.approx(expected_terminal_spot)


def test_delta_policy_consumes_m2_sensitivity_without_owning_dynamic_state() -> None:
    pricing_problem = _pricing_problem()
    direct_delta = evaluate_sensitivity(
        BlackScholesSensitivityProblem(
            pricing_problem=pricing_problem,
            sensitivity=BlackScholesSensitivity.DELTA,
        ),
        AnalyticBlackScholesSensitivity(),
    ).value

    policy_delta = AnalyticDeltaHedgePolicy().target_underlying_units(pricing_problem)

    assert policy_delta == direct_delta


def test_frictionless_rebalance_preserves_accounting_identities() -> None:
    result = _hedge_result(seed=7, every_days=30)
    numeraire = result.problem.pricing_problem.numeraire

    assert len(result.path.points) == 366
    assert len(result.steps) == 13
    assert result.total_transaction_cost == 0.0
    assert result.steps[0].cash_before_financing == result.initial_option_value
    assert result.steps[0].action.previous_underlying_units == 0.0

    previous_time = _VALUATION_DATE
    for step in result.steps:
        action = step.action
        assert action.trade_underlying_units == pytest.approx(
            action.target_underlying_units - action.previous_underlying_units
        )
        assert action.trade_notional == pytest.approx(
            action.trade_underlying_units * step.spot
        )
        assert step.cash_before_rebalance == pytest.approx(
            step.cash_before_financing + step.financing_gain
        )
        assert step.cash_after_rebalance == pytest.approx(
            step.cash_before_rebalance - action.trade_notional
        )
        assert step.portfolio_value_after_rebalance == pytest.approx(
            step.portfolio_value_before_rebalance
        )
        expected_financing_gain = step.cash_before_financing * (
            numeraire.value_at(step.time) / numeraire.value_at(previous_time) - 1.0
        )
        assert step.financing_gain == pytest.approx(expected_financing_gain)
        previous_time = step.time

    terminal = result.terminal
    assert terminal.hedge_value == pytest.approx(
        terminal.stock_units * terminal.spot + terminal.cash_account
    )
    assert terminal.replication_error == pytest.approx(
        terminal.hedge_value - terminal.option_payoff
    )
    assert terminal.hedged_short_option_pnl == terminal.replication_error


def test_transaction_cost_is_explicit_cash_outflow_not_hidden_pnl() -> None:
    frictionless = _hedge_result(seed=23, every_days=7)
    with_cost = _hedge_result(
        seed=23,
        every_days=7,
        transaction_cost_rate=0.001,
    )

    assert with_cost.total_transaction_cost > 0.0
    assert with_cost.replication_error < frictionless.replication_error
    assert with_cost.total_transaction_cost == pytest.approx(
        sum(step.action.transaction_cost for step in with_cost.steps)
    )
    for step in with_cost.steps:
        assert step.portfolio_value_after_rebalance == pytest.approx(
            step.portfolio_value_before_rebalance - step.action.transaction_cost
        )


def test_hedge_actions_do_not_look_ahead_on_the_realized_path() -> None:
    original = _simulated_path(seed=31)
    cutoff = _VALUATION_DATE + timedelta(days=180)
    altered_points = tuple(
        point
        if point.time <= cutoff
        else EquityPathPoint(time=point.time, spot=point.spot * 1.40)
        for point in original.points
    )
    altered = SimulatedEquityPath(
        simulation=original.simulation,
        points=altered_points,
    )
    dates = original.simulation.observation_dates
    problem = BlackScholesDeltaHedgeProblem(
        pricing_problem=_pricing_problem(),
        rebalance_dates=_rebalance_dates(dates, 7),
    )

    original_result = run_delta_hedge(problem, original)
    altered_result = run_delta_hedge(problem, altered)
    original_prefix = tuple(
        step for step in original_result.steps if step.time <= cutoff
    )
    altered_prefix = tuple(step for step in altered_result.steps if step.time <= cutoff)

    assert original_prefix == altered_prefix
    assert original_result.terminal.spot != altered_result.terminal.spot


def test_replication_error_improves_with_more_frequent_rebalancing() -> None:
    monthly = _study_summary(every_days=30)
    weekly = _study_summary(every_days=7)
    daily = _study_summary(every_days=1)

    assert daily.root_mean_square_error < weekly.root_mean_square_error
    assert weekly.root_mean_square_error < monthly.root_mean_square_error
    assert daily.mean_absolute_error < weekly.mean_absolute_error
    assert weekly.mean_absolute_error < monthly.mean_absolute_error
    assert daily.replicate_count == 64
    assert daily.seeds == tuple(range(64))
    assert daily.path_observation_count == 366


def test_volatility_misspecification_is_distinct_from_discrete_hedging_error() -> None:
    correctly_specified = _study_summary(
        every_days=7,
        generating_volatility=0.30,
        hedging_volatility=0.30,
    )
    misspecified = _study_summary(
        every_days=7,
        generating_volatility=0.30,
        hedging_volatility=0.20,
    )

    assert misspecified.root_mean_square_error > (
        2.0 * correctly_specified.root_mean_square_error
    )
    assert misspecified.mean_error < -2.0
    assert misspecified.generating_annualized_volatility == 0.30
    assert misspecified.hedging_annualized_volatility == 0.20


def test_nonzero_dividend_yield_requires_explicit_cash_flow_accounting() -> None:
    with pytest.raises(ValueError, match="zero continuous dividend yield"):
        BlackScholesDeltaHedgeProblem(
            pricing_problem=_pricing_problem(dividend_yield=0.02),
            rebalance_dates=(_VALUATION_DATE,),
        )


def test_summary_rejects_mixed_hedge_conditions() -> None:
    weekly = _hedge_result(seed=1, every_days=7)
    monthly = _hedge_result(seed=2, every_days=30)

    with pytest.raises(ValueError, match="one common hedge study condition"):
        summarize_replication_errors((weekly, monthly))
