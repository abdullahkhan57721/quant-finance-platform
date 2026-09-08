"""Concrete dynamic Black-Scholes delta-hedging control and evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import sqrt
from statistics import fmean, median, stdev
from typing import cast

from qf_platform._validation import calendar_date, nonnegative_finite_real
from qf_platform.control.paths import SimulatedEquityPath
from qf_platform.pricing.black_scholes import BlackScholesLaw, BlackScholesParameters
from qf_platform.pricing.black_scholes_valuation import BlackScholesClosedForm
from qf_platform.pricing.equity import EquityState, EquityStateSpace, EuropeanOption
from qf_platform.pricing.measures import validated_numeraire_value
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState
from qf_platform.pricing.valuation import evaluate
from qf_platform.sensitivity import (
    AnalyticBlackScholesSensitivity,
    BlackScholesSensitivity,
    BlackScholesSensitivityProblem,
    evaluate_sensitivity,
)

type BlackScholesPricingProblem = PricingProblem[
    date, EquityState, BlackScholesParameters
]


def _strictly_increasing_dates(
    values: tuple[date, ...], *, name: str
) -> tuple[date, ...]:
    dates = tuple(calendar_date(value, name=name) for value in values)
    if not dates:
        msg = f"{name} must not be empty"
        raise ValueError(msg)
    if any(later <= earlier for earlier, later in zip(dates, dates[1:], strict=False)):
        msg = f"{name} must be strictly increasing"
        raise ValueError(msg)
    return dates


def _require_black_scholes_problem(
    problem: BlackScholesPricingProblem,
    *,
    purpose: str,
) -> tuple[EuropeanOption, FlatMoneyMarketNumeraire]:
    contract = problem.contract
    numeraire = problem.numeraire
    if not (
        isinstance(problem.current_state.state_space, EquityStateSpace)
        and isinstance(problem.stochastic_law, BlackScholesLaw)
        and isinstance(contract, EuropeanOption)
        and isinstance(numeraire, FlatMoneyMarketNumeraire)
    ):
        msg = f"{purpose} requires the concrete M1 Black-Scholes family"
        raise ValueError(msg)
    return contract, numeraire


@dataclass(frozen=True, slots=True)
class AnalyticDeltaHedgePolicy:
    """Dynamic hedge rule that maps current Black-Scholes state to analytic Delta."""

    def target_underlying_units(self, problem: BlackScholesPricingProblem, /) -> float:
        sensitivity_problem = BlackScholesSensitivityProblem(
            pricing_problem=problem,
            sensitivity=BlackScholesSensitivity.DELTA,
        )
        result = evaluate_sensitivity(
            sensitivity_problem,
            AnalyticBlackScholesSensitivity(),
        )
        return result.value


@dataclass(frozen=True, slots=True)
class BlackScholesDeltaHedgeProblem:
    """Concrete dynamic replication question for one European option liability.

    The liability is one short option. Initial hedge capital equals the hedging-model
    option present value. The stock position follows the supplied Delta policy and the
    residual is held in the problem's money-market account.

    M3 intentionally supports zero continuous dividend yield only. Nonzero yield would
    require a separately explicit dividend-cash-flow integration convention between
    rebalances; it is not silently approximated here.
    """

    pricing_problem: BlackScholesPricingProblem
    rebalance_dates: tuple[date, ...]
    proportional_transaction_cost_rate: float = 0.0

    def __post_init__(self) -> None:
        contract, _ = _require_black_scholes_problem(
            self.pricing_problem,
            purpose="delta hedging",
        )
        pricing_problem = self.pricing_problem
        if contract.expiry <= pricing_problem.valuation_time:
            msg = "delta hedging requires expiry after valuation time"
            raise ValueError(msg)
        if pricing_problem.current_state.value.spot <= 0.0 or contract.strike <= 0.0:
            msg = "delta hedging requires positive spot and strike"
            raise ValueError(msg)
        if pricing_problem.parameters.annualized_volatility <= 0.0:
            msg = "delta hedging requires positive hedging volatility"
            raise ValueError(msg)
        if pricing_problem.parameters.continuous_dividend_yield != 0.0:
            msg = "M3 delta hedging currently supports zero continuous dividend yield"
            raise ValueError(msg)

        dates = _strictly_increasing_dates(
            tuple(self.rebalance_dates),
            name="rebalance date",
        )
        if dates[0] != pricing_problem.valuation_time:
            msg = "first rebalance date must equal valuation time"
            raise ValueError(msg)
        if any(rebalance_date >= contract.expiry for rebalance_date in dates):
            msg = "rebalance dates must be strictly before option expiry"
            raise ValueError(msg)
        object.__setattr__(self, "rebalance_dates", dates)
        object.__setattr__(
            self,
            "proportional_transaction_cost_rate",
            nonnegative_finite_real(
                self.proportional_transaction_cost_rate,
                name="proportional_transaction_cost_rate",
            ),
        )


@dataclass(frozen=True, slots=True)
class DeltaHedgeAction:
    """One realized rebalance action, distinct from the Delta sensitivity itself."""

    time: date
    spot: float
    previous_underlying_units: float
    target_underlying_units: float
    trade_underlying_units: float
    trade_notional: float
    transaction_cost: float


@dataclass(frozen=True, slots=True)
class DeltaHedgeStep:
    """Explicit stock/cash accounting around one rebalance event."""

    time: date
    spot: float
    option_value: float
    action: DeltaHedgeAction
    cash_before_financing: float
    financing_gain: float
    cash_before_rebalance: float
    cash_after_rebalance: float
    portfolio_value_before_rebalance: float
    portfolio_value_after_rebalance: float


@dataclass(frozen=True, slots=True)
class DeltaHedgeTerminal:
    """Terminal hedge accounting and short-option settlement evidence."""

    time: date
    spot: float
    stock_units: float
    cash_before_financing: float
    financing_gain: float
    cash_account: float
    hedge_value: float
    option_payoff: float
    replication_error: float

    @property
    def hedged_short_option_pnl(self) -> float:
        """Terminal P&L after settling one short option; equals replication error."""

        return self.replication_error


@dataclass(frozen=True, slots=True)
class DeltaHedgeResult:
    """Immutable completed path-level evidence for one dynamic hedge execution."""

    problem: BlackScholesDeltaHedgeProblem
    path: SimulatedEquityPath
    initial_option_value: float
    steps: tuple[DeltaHedgeStep, ...]
    terminal: DeltaHedgeTerminal
    total_transaction_cost: float

    @property
    def replication_error(self) -> float:
        return self.terminal.replication_error

    @property
    def seed(self) -> int:
        return self.path.seed

    @property
    def generating_annualized_volatility(self) -> float:
        return self.path.simulation.parameters.annualized_volatility

    @property
    def hedging_annualized_volatility(self) -> float:
        return self.problem.pricing_problem.parameters.annualized_volatility


@dataclass(frozen=True, slots=True)
class ReplicationErrorSummary:
    """Aggregate evidence across stochastic replicates of one hedge condition."""

    replicate_count: int
    seeds: tuple[int, ...]
    rebalance_dates: tuple[date, ...]
    path_observation_count: int
    generating_annualized_volatility: float
    hedging_annualized_volatility: float
    proportional_transaction_cost_rate: float
    mean_error: float
    median_error: float
    error_standard_deviation: float
    mean_absolute_error: float
    root_mean_square_error: float


def _pricing_problem_at(
    base_problem: BlackScholesPricingProblem,
    *,
    time: date,
    spot: float,
) -> BlackScholesPricingProblem:
    current_state = ModeledState(
        time=time,
        value=EquityState(spot),
        state_space=base_problem.current_state.state_space,
    )
    return PricingProblem(
        current_state=current_state,
        stochastic_law=base_problem.stochastic_law,
        parameters=base_problem.parameters,
        contract=base_problem.contract,
        numeraire=base_problem.numeraire,
        pricing_measure=base_problem.pricing_measure,
    )


def _financing_gain(
    cash: float,
    *,
    earlier: date,
    later: date,
    numeraire: FlatMoneyMarketNumeraire,
) -> float:
    earlier_value = validated_numeraire_value(numeraire, earlier)
    later_value = validated_numeraire_value(numeraire, later)
    return cash * (later_value / earlier_value - 1.0)


def _require_compatible_path(
    problem: BlackScholesDeltaHedgeProblem,
    path: SimulatedEquityPath,
) -> EuropeanOption:
    pricing_problem = problem.pricing_problem
    contract, numeraire = _require_black_scholes_problem(
        pricing_problem,
        purpose="delta hedging",
    )
    simulation = path.simulation
    if simulation.initial_state.time != pricing_problem.valuation_time:
        msg = "path and hedge problem must share the valuation time"
        raise ValueError(msg)
    if simulation.initial_state.value.spot != pricing_problem.current_state.value.spot:
        msg = "path and hedge problem must share the initial spot"
        raise ValueError(msg)
    if simulation.observation_dates[-1] != contract.expiry:
        msg = "simulated path must terminate at option expiry"
        raise ValueError(msg)
    if simulation.numeraire != numeraire:
        msg = "path and hedge problem must share money-market financing semantics"
        raise ValueError(msg)
    if simulation.pricing_measure != pricing_problem.pricing_measure:
        msg = "path and hedge problem must share pricing-measure semantics"
        raise ValueError(msg)
    if (
        simulation.parameters.continuous_dividend_yield
        != pricing_problem.parameters.continuous_dividend_yield
    ):
        msg = "M3 misspecification currently varies volatility only"
        raise ValueError(msg)
    path_dates = set(simulation.observation_dates)
    if any(
        rebalance_date not in path_dates for rebalance_date in problem.rebalance_dates
    ):
        msg = "every rebalance date must be present on the simulated path"
        raise ValueError(msg)
    return contract


def _rebalance_step(
    *,
    problem: BlackScholesDeltaHedgeProblem,
    policy: AnalyticDeltaHedgePolicy,
    time: date,
    spot: float,
    previous_time: date,
    previous_underlying_units: float,
    previous_cash: float,
) -> DeltaHedgeStep:
    numeraire = cast(FlatMoneyMarketNumeraire, problem.pricing_problem.numeraire)
    financing_gain = 0.0
    if time != previous_time:
        financing_gain = _financing_gain(
            previous_cash,
            earlier=previous_time,
            later=time,
            numeraire=numeraire,
        )
    cash_before_rebalance = previous_cash + financing_gain
    current_problem = _pricing_problem_at(problem.pricing_problem, time=time, spot=spot)
    option_value = evaluate(current_problem, BlackScholesClosedForm()).present_value
    target_units = policy.target_underlying_units(current_problem)
    trade_units = target_units - previous_underlying_units
    trade_notional = trade_units * spot
    transaction_cost = problem.proportional_transaction_cost_rate * abs(trade_notional)
    cash_after_rebalance = cash_before_rebalance - trade_notional - transaction_cost
    portfolio_before = previous_underlying_units * spot + cash_before_rebalance
    portfolio_after = target_units * spot + cash_after_rebalance
    action = DeltaHedgeAction(
        time=time,
        spot=spot,
        previous_underlying_units=previous_underlying_units,
        target_underlying_units=target_units,
        trade_underlying_units=trade_units,
        trade_notional=trade_notional,
        transaction_cost=transaction_cost,
    )
    return DeltaHedgeStep(
        time=time,
        spot=spot,
        option_value=option_value,
        action=action,
        cash_before_financing=previous_cash,
        financing_gain=financing_gain,
        cash_before_rebalance=cash_before_rebalance,
        cash_after_rebalance=cash_after_rebalance,
        portfolio_value_before_rebalance=portfolio_before,
        portfolio_value_after_rebalance=portfolio_after,
    )


def run_delta_hedge(
    problem: BlackScholesDeltaHedgeProblem,
    path: SimulatedEquityPath,
    /,
    *,
    policy: AnalyticDeltaHedgePolicy | None = None,
) -> DeltaHedgeResult:
    """Execute one no-lookahead discrete Delta hedge on an already realized path."""

    contract = _require_compatible_path(problem, path)
    selected_policy = policy if policy is not None else AnalyticDeltaHedgePolicy()
    initial_option_value = evaluate(
        problem.pricing_problem,
        BlackScholesClosedForm(),
    ).present_value
    point_by_date = {point.time: point for point in path.points}

    steps: list[DeltaHedgeStep] = []
    previous_time = problem.pricing_problem.valuation_time
    previous_underlying_units = 0.0
    previous_cash = initial_option_value
    total_transaction_cost = 0.0

    for rebalance_date in problem.rebalance_dates:
        point = point_by_date[rebalance_date]
        step = _rebalance_step(
            problem=problem,
            policy=selected_policy,
            time=rebalance_date,
            spot=point.spot,
            previous_time=previous_time,
            previous_underlying_units=previous_underlying_units,
            previous_cash=previous_cash,
        )
        steps.append(step)
        previous_time = rebalance_date
        previous_underlying_units = step.action.target_underlying_units
        previous_cash = step.cash_after_rebalance
        total_transaction_cost += step.action.transaction_cost

    terminal_point = path.points[-1]
    numeraire = cast(FlatMoneyMarketNumeraire, problem.pricing_problem.numeraire)
    terminal_financing_gain = _financing_gain(
        previous_cash,
        earlier=previous_time,
        later=contract.expiry,
        numeraire=numeraire,
    )
    terminal_cash = previous_cash + terminal_financing_gain
    hedge_value = previous_underlying_units * terminal_point.spot + terminal_cash
    cash_flows = contract.cash_flows(path).cash_flows
    if len(cash_flows) != 1 or cash_flows[0].payment_time != contract.expiry:
        msg = "European option hedge expects one terminal cash flow"
        raise ValueError(msg)
    option_payoff = cash_flows[0].amount
    replication_error = hedge_value - option_payoff
    terminal = DeltaHedgeTerminal(
        time=contract.expiry,
        spot=terminal_point.spot,
        stock_units=previous_underlying_units,
        cash_before_financing=previous_cash,
        financing_gain=terminal_financing_gain,
        cash_account=terminal_cash,
        hedge_value=hedge_value,
        option_payoff=option_payoff,
        replication_error=replication_error,
    )
    return DeltaHedgeResult(
        problem=problem,
        path=path,
        initial_option_value=initial_option_value,
        steps=tuple(steps),
        terminal=terminal,
        total_transaction_cost=total_transaction_cost,
    )


def _same_summary_condition(
    first: DeltaHedgeResult,
    candidate: DeltaHedgeResult,
) -> bool:
    return (
        first.problem.pricing_problem == candidate.problem.pricing_problem
        and first.problem.rebalance_dates == candidate.problem.rebalance_dates
        and first.problem.proportional_transaction_cost_rate
        == candidate.problem.proportional_transaction_cost_rate
        and len(first.path.points) == len(candidate.path.points)
        and first.generating_annualized_volatility
        == candidate.generating_annualized_volatility
        and first.path.simulation.parameters.continuous_dividend_yield
        == candidate.path.simulation.parameters.continuous_dividend_yield
        and first.path.simulation.numeraire == candidate.path.simulation.numeraire
        and first.path.simulation.pricing_measure
        == candidate.path.simulation.pricing_measure
    )


def summarize_replication_errors(
    results: tuple[DeltaHedgeResult, ...],
    /,
) -> ReplicationErrorSummary:
    """Summarize terminal errors for replicates sharing one explicit hedge condition."""

    completed = tuple(results)
    if len(completed) < 2:
        msg = "replication-error summary requires at least two stochastic replicates"
        raise ValueError(msg)
    first = completed[0]
    if any(not _same_summary_condition(first, result) for result in completed[1:]):
        msg = "replication-error summary requires one common hedge study condition"
        raise ValueError(msg)
    errors = tuple(result.replication_error for result in completed)
    squared_errors = tuple(error * error for error in errors)
    return ReplicationErrorSummary(
        replicate_count=len(completed),
        seeds=tuple(result.seed for result in completed),
        rebalance_dates=first.problem.rebalance_dates,
        path_observation_count=len(first.path.points),
        generating_annualized_volatility=first.generating_annualized_volatility,
        hedging_annualized_volatility=first.hedging_annualized_volatility,
        proportional_transaction_cost_rate=(
            first.problem.proportional_transaction_cost_rate
        ),
        mean_error=fmean(errors),
        median_error=median(errors),
        error_standard_deviation=stdev(errors),
        mean_absolute_error=fmean(abs(error) for error in errors),
        root_mean_square_error=sqrt(fmean(squared_errors)),
    )
