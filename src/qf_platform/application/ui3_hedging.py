"""Frontend-neutral UI3 orchestration for merged M3 dynamic-hedging evidence."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta

from qf_platform.application.black_scholes_study import BlackScholesStudyComposition
from qf_platform.control import (
    BlackScholesDeltaHedgeProblem,
    BlackScholesPathSimulation,
    DeltaHedgeResult,
    ReplicationErrorSummary,
    SimulatedEquityPath,
    run_delta_hedge,
    simulate_black_scholes_path,
    summarize_replication_errors,
)
from qf_platform.pricing import (
    BlackScholesParameters,
    EquityState,
    EuropeanOption,
    PricingProblem,
)

type BlackScholesPricingProblem = PricingProblem[
    date, EquityState, BlackScholesParameters
]


@dataclass(frozen=True, slots=True)
class HedgeWorkbenchDraft:
    """Transient UI3 control configuration, separate from financial draft state."""

    generating_volatility: str = "0.20"
    hedging_volatility: str = "0.20"
    rebalance_day_interval: str = "7"
    seed: str = "1729"
    replicate_count: str = "16"
    transaction_cost_rate: str = "0.0"


@dataclass(frozen=True, slots=True)
class HedgeWorkbenchConfig:
    """Normalized M3 research configuration for the native Workbench."""

    generating_volatility: float
    hedging_volatility: float
    rebalance_day_interval: int
    seed: int
    replicate_count: int
    transaction_cost_rate: float


@dataclass(frozen=True, slots=True)
class HedgeWorkbenchRequest:
    """One authoritative M3 Workbench request over an M1 pricing composition."""

    composition: BlackScholesStudyComposition
    config: HedgeWorkbenchConfig


@dataclass(frozen=True, slots=True)
class HedgeReplicateEvidence:
    """Path-level terminal evidence kept distinct from aggregate conclusions."""

    seed: int
    replication_error: float
    total_transaction_cost: float


@dataclass(frozen=True, slots=True)
class HedgeFrequencyEvidence:
    """Aggregate replication evidence for one explicit rebalance cadence."""

    rebalance_day_interval: int
    summary: ReplicationErrorSummary


@dataclass(frozen=True, slots=True)
class HedgeWorkbenchAnalysis:
    """Completed UI3 hedge evidence assembled only through merged M3 APIs."""

    selected_result: DeltaHedgeResult
    selected_replicates: tuple[HedgeReplicateEvidence, ...]
    selected_summary: ReplicationErrorSummary
    frequency_evidence: tuple[HedgeFrequencyEvidence, ...]
    correctly_specified_summary: ReplicationErrorSummary
    frictionless_summary: ReplicationErrorSummary


def normalize_hedge_workbench_config(
    draft: HedgeWorkbenchDraft,
) -> HedgeWorkbenchConfig:
    """Normalize transient UI controls without changing M3 quantitative semantics."""

    return HedgeWorkbenchConfig(
        generating_volatility=_positive_float(
            draft.generating_volatility,
            "generating volatility",
        ),
        hedging_volatility=_positive_float(
            draft.hedging_volatility,
            "hedging volatility",
        ),
        rebalance_day_interval=_positive_int(
            draft.rebalance_day_interval,
            "rebalance day interval",
        ),
        seed=_integer(draft.seed, "seed"),
        replicate_count=_positive_int(
            draft.replicate_count,
            "replicate count",
            minimum=2,
        ),
        transaction_cost_rate=_nonnegative_float(
            draft.transaction_cost_rate,
            "transaction cost rate",
        ),
    )


def make_hedge_workbench_request(
    composition: BlackScholesStudyComposition,
    draft: HedgeWorkbenchDraft,
) -> HedgeWorkbenchRequest:
    """Combine one normalized M1 composition with explicit M3 study configuration."""

    if composition.problem.parameters.continuous_dividend_yield != 0.0:
        msg = "UI3 hedging preserves M3's zero continuous dividend-yield limitation"
        raise ValueError(msg)
    return HedgeWorkbenchRequest(
        composition=composition,
        config=normalize_hedge_workbench_config(draft),
    )


def run_hedge_workbench(request: HedgeWorkbenchRequest) -> HedgeWorkbenchAnalysis:
    """Run one selected path plus paired M3 aggregate studies on common paths."""

    observation_dates = _daily_observation_dates(request)
    paths = _simulated_paths(request, observation_dates)
    config = request.config
    selected_results = _hedge_condition(
        request,
        paths,
        observation_dates,
        rebalance_day_interval=config.rebalance_day_interval,
        hedging_volatility=config.hedging_volatility,
        transaction_cost_rate=config.transaction_cost_rate,
    )
    selected_summary = summarize_replication_errors(selected_results)

    frequency_evidence: list[HedgeFrequencyEvidence] = []
    for interval in _frequency_intervals(config.rebalance_day_interval):
        summary = selected_summary
        if interval != config.rebalance_day_interval:
            summary = summarize_replication_errors(
                _hedge_condition(
                    request,
                    paths,
                    observation_dates,
                    rebalance_day_interval=interval,
                    hedging_volatility=config.hedging_volatility,
                    transaction_cost_rate=config.transaction_cost_rate,
                )
            )
        frequency_evidence.append(HedgeFrequencyEvidence(interval, summary))

    correctly_specified = selected_summary
    if config.hedging_volatility != config.generating_volatility:
        correctly_specified = summarize_replication_errors(
            _hedge_condition(
                request,
                paths,
                observation_dates,
                rebalance_day_interval=config.rebalance_day_interval,
                hedging_volatility=config.generating_volatility,
                transaction_cost_rate=config.transaction_cost_rate,
            )
        )

    frictionless = selected_summary
    if config.transaction_cost_rate != 0.0:
        frictionless = summarize_replication_errors(
            _hedge_condition(
                request,
                paths,
                observation_dates,
                rebalance_day_interval=config.rebalance_day_interval,
                hedging_volatility=config.hedging_volatility,
                transaction_cost_rate=0.0,
            )
        )

    return HedgeWorkbenchAnalysis(
        selected_result=selected_results[0],
        selected_replicates=tuple(
            HedgeReplicateEvidence(
                seed=result.seed,
                replication_error=result.replication_error,
                total_transaction_cost=result.total_transaction_cost,
            )
            for result in selected_results
        ),
        selected_summary=selected_summary,
        frequency_evidence=tuple(frequency_evidence),
        correctly_specified_summary=correctly_specified,
        frictionless_summary=frictionless,
    )


def _daily_observation_dates(request: HedgeWorkbenchRequest) -> tuple[date, ...]:
    problem = request.composition.problem
    contract = problem.contract
    if not isinstance(contract, EuropeanOption):
        raise TypeError("UI3 hedging requires the M1 European option contract")
    expiry = contract.expiry
    valuation_date = problem.valuation_time
    days = (expiry - valuation_date).days
    if days <= 0:
        raise ValueError("UI3 hedging requires expiry after valuation date")
    return tuple(valuation_date + timedelta(days=offset) for offset in range(days + 1))


def _rebalance_dates(
    observation_dates: tuple[date, ...],
    every_days: int,
) -> tuple[date, ...]:
    return observation_dates[:-1:every_days]


def _pricing_problem_with_volatility(
    request: HedgeWorkbenchRequest,
    annualized_volatility: float,
) -> BlackScholesPricingProblem:
    base = request.composition.problem
    return replace(
        base,
        parameters=BlackScholesParameters(
            annualized_volatility=annualized_volatility,
            continuous_dividend_yield=base.parameters.continuous_dividend_yield,
        ),
    )


def _simulated_paths(
    request: HedgeWorkbenchRequest,
    observation_dates: tuple[date, ...],
) -> tuple[SimulatedEquityPath, ...]:
    generating_problem = _pricing_problem_with_volatility(
        request,
        request.config.generating_volatility,
    )
    return tuple(
        simulate_black_scholes_path(
            BlackScholesPathSimulation.from_pricing_problem(
                generating_problem,
                observation_dates=observation_dates,
                seed=request.config.seed + offset,
            )
        )
        for offset in range(request.config.replicate_count)
    )


def _hedge_condition(
    request: HedgeWorkbenchRequest,
    paths: tuple[SimulatedEquityPath, ...],
    observation_dates: tuple[date, ...],
    *,
    rebalance_day_interval: int,
    hedging_volatility: float,
    transaction_cost_rate: float,
) -> tuple[DeltaHedgeResult, ...]:
    hedge_problem = BlackScholesDeltaHedgeProblem(
        pricing_problem=_pricing_problem_with_volatility(request, hedging_volatility),
        rebalance_dates=_rebalance_dates(observation_dates, rebalance_day_interval),
        proportional_transaction_cost_rate=transaction_cost_rate,
    )
    return tuple(run_delta_hedge(hedge_problem, path) for path in paths)


def _frequency_intervals(configured: int) -> tuple[int, ...]:
    return tuple(dict.fromkeys((30, 14, 7, 1, configured)))


def _positive_float(value: str, name: str) -> float:
    parsed = _float(value, name)
    if parsed <= 0.0:
        raise ValueError(f"{name} must be positive")
    return parsed


def _nonnegative_float(value: str, name: str) -> float:
    parsed = _float(value, name)
    if parsed < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return parsed


def _float(value: str, name: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


def _integer(value: str, name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _positive_int(value: str, name: str, minimum: int = 1) -> int:
    parsed = _integer(value, name)
    if parsed < minimum:
        qualifier = "positive" if minimum == 1 else f"at least {minimum}"
        raise ValueError(f"{name} must be {qualifier}")
    return parsed
