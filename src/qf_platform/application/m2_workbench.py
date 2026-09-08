"""Concrete M2 Workbench orchestration over merged pricing and sensitivity APIs."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from qf_platform.application.black_scholes_study import BlackScholesStudyComposition
from qf_platform.pricing import (
    BlackScholesClosedForm,
    CoxRossRubinstein,
    EquityState,
    MonteCarloEuropeanOption,
    MonteCarloValuationResult,
    ValuationResult,
    evaluate,
)
from qf_platform.sensitivity import (
    AnalyticBlackScholesSensitivity,
    BlackScholesSensitivity,
    BlackScholesSensitivityProblem,
    BlackScholesSensitivityResult,
    FiniteDifferenceBlackScholesSensitivity,
    evaluate_sensitivity,
)


class WorkbenchValuationMethod(StrEnum):
    """Valuation methods exposed by UI2 because M2 implements them."""

    ANALYTIC = "analytic"
    CRR = "crr"
    MONTE_CARLO = "monte_carlo"

    @property
    def label(self) -> str:
        if self is WorkbenchValuationMethod.ANALYTIC:
            return "Black-Scholes analytic"
        if self is WorkbenchValuationMethod.CRR:
            return "Cox-Ross-Rubinstein"
        return "Monte Carlo"


@dataclass(frozen=True, slots=True)
class M2WorkbenchDraft:
    """Transient method/sensitivity configuration; never financial state."""

    valuation_method: str = "analytic"
    crr_steps: str = "400"
    monte_carlo_paths: str = "20000"
    monte_carlo_seed: str = "1729"
    selected_greek: str = "delta"
    spot_bump: str = "0.1"
    volatility_bump: str = "0.001"
    rate_bump: str = "0.0001"
    theta_day_bump: str = "1"


@dataclass(frozen=True, slots=True)
class M2WorkbenchConfig:
    """Normalized UI2 configuration separate from quantitative results."""

    valuation_method: WorkbenchValuationMethod
    crr_steps: int
    monte_carlo_paths: int
    monte_carlo_seed: int
    selected_greek: BlackScholesSensitivity
    finite_difference_method: FiniteDifferenceBlackScholesSensitivity

    @property
    def method_configuration(self) -> str:
        if self.valuation_method is WorkbenchValuationMethod.ANALYTIC:
            return "closed form"
        if self.valuation_method is WorkbenchValuationMethod.CRR:
            return f"steps={self.crr_steps}"
        return f"paths={self.monte_carlo_paths}; seed={self.monte_carlo_seed}"


@dataclass(frozen=True, slots=True)
class M2WorkbenchRequest:
    """One UI2 analysis request over an authoritative UI1 pricing composition."""

    composition: BlackScholesStudyComposition
    config: M2WorkbenchConfig


@dataclass(frozen=True, slots=True)
class ValuationRun:
    method: WorkbenchValuationMethod
    configuration: str
    supported: bool
    result: ValuationResult | None


@dataclass(frozen=True, slots=True)
class CRRConvergencePoint:
    steps: int
    supported: bool
    result: ValuationResult | None


@dataclass(frozen=True, slots=True)
class MonteCarloConvergencePoint:
    paths: int
    result: MonteCarloValuationResult


@dataclass(frozen=True, slots=True)
class SensitivityRun:
    sensitivity: BlackScholesSensitivity
    analytic_supported: bool
    analytic_result: BlackScholesSensitivityResult | None
    finite_difference_supported: bool
    finite_difference_result: BlackScholesSensitivityResult | None


@dataclass(frozen=True, slots=True)
class GreekCurvePoint:
    spot: float
    analytic_result: BlackScholesSensitivityResult | None
    finite_difference_result: BlackScholesSensitivityResult | None


@dataclass(frozen=True, slots=True)
class GammaBumpPoint:
    spot_bump: float
    supported: bool
    result: BlackScholesSensitivityResult | None


@dataclass(frozen=True, slots=True)
class M2WorkbenchAnalysis:
    """Immutable UI2 evidence assembled from merged M2 public APIs."""

    selected_valuation: ValuationRun
    valuations: tuple[ValuationRun, ...]
    crr_convergence: tuple[CRRConvergencePoint, ...]
    monte_carlo_convergence: tuple[MonteCarloConvergencePoint, ...]
    sensitivities: tuple[SensitivityRun, ...]
    greek_curve: tuple[GreekCurvePoint, ...]
    gamma_bump_study: tuple[GammaBumpPoint, ...]


def normalize_m2_workbench_config(draft: M2WorkbenchDraft) -> M2WorkbenchConfig:
    """Normalize transient UI2 method configuration into typed M2 values."""
    try:
        method = WorkbenchValuationMethod(draft.valuation_method.strip().lower())
    except ValueError as exc:
        raise ValueError(
            "valuation method must be analytic, crr, or monte_carlo"
        ) from exc
    try:
        greek = BlackScholesSensitivity(draft.selected_greek.strip().lower())
    except ValueError as exc:
        raise ValueError(
            "selected Greek must be delta, gamma, vega, theta, or rho"
        ) from exc
    return M2WorkbenchConfig(
        valuation_method=method,
        crr_steps=_positive_int(draft.crr_steps, "CRR steps"),
        monte_carlo_paths=_positive_int(
            draft.monte_carlo_paths,
            "Monte Carlo paths",
            minimum=2,
        ),
        monte_carlo_seed=_integer(draft.monte_carlo_seed, "Monte Carlo seed"),
        selected_greek=greek,
        finite_difference_method=FiniteDifferenceBlackScholesSensitivity(
            spot_bump=_positive_float(draft.spot_bump, "spot bump"),
            volatility_bump=_positive_float(
                draft.volatility_bump,
                "volatility bump",
            ),
            rate_bump=_positive_float(draft.rate_bump, "rate bump"),
            theta_day_bump=_positive_int(
                draft.theta_day_bump,
                "theta day bump",
            ),
        ),
    )


def make_m2_workbench_request(
    composition: BlackScholesStudyComposition,
    draft: M2WorkbenchDraft,
) -> M2WorkbenchRequest:
    return M2WorkbenchRequest(composition, normalize_m2_workbench_config(draft))


def selected_method(
    config: M2WorkbenchConfig,
) -> BlackScholesClosedForm | CoxRossRubinstein | MonteCarloEuropeanOption:
    """Construct only the selected concrete production valuation method."""
    if config.valuation_method is WorkbenchValuationMethod.ANALYTIC:
        return BlackScholesClosedForm()
    if config.valuation_method is WorkbenchValuationMethod.CRR:
        return CoxRossRubinstein(config.crr_steps)
    return MonteCarloEuropeanOption(
        paths=config.monte_carlo_paths,
        seed=config.monte_carlo_seed,
    )


def run_m2_workbench(request: M2WorkbenchRequest) -> M2WorkbenchAnalysis:
    """Run concrete UI2 comparison and sensitivity studies."""
    valuations = tuple(
        _valuation_run(request, method) for method in WorkbenchValuationMethod
    )
    selected = next(
        run for run in valuations if run.method is request.config.valuation_method
    )
    sensitivities = tuple(
        _sensitivity_run(request, sensitivity)
        for sensitivity in BlackScholesSensitivity
    )
    return M2WorkbenchAnalysis(
        selected_valuation=selected,
        valuations=valuations,
        crr_convergence=_crr_convergence(request),
        monte_carlo_convergence=_monte_carlo_convergence(request),
        sensitivities=sensitivities,
        greek_curve=_greek_curve(request),
        gamma_bump_study=_gamma_bump_study(request),
    )


def _valuation_run(
    request: M2WorkbenchRequest,
    method: WorkbenchValuationMethod,
) -> ValuationRun:
    problem = request.composition.problem
    config = request.config
    if method is WorkbenchValuationMethod.ANALYTIC:
        analytic = BlackScholesClosedForm()
        supported = analytic.supports(problem)
        result = evaluate(problem, analytic) if supported else None
        return ValuationRun(method, "closed form", supported, result)
    if method is WorkbenchValuationMethod.CRR:
        crr = CoxRossRubinstein(config.crr_steps)
        supported = crr.supports(problem)
        result = evaluate(problem, crr) if supported else None
        return ValuationRun(
            method,
            f"steps={config.crr_steps}",
            supported,
            result,
        )
    monte_carlo = MonteCarloEuropeanOption(
        paths=config.monte_carlo_paths,
        seed=config.monte_carlo_seed,
    )
    supported = monte_carlo.supports(problem)
    result = evaluate(problem, monte_carlo) if supported else None
    return ValuationRun(
        method,
        f"paths={config.monte_carlo_paths}; seed={config.monte_carlo_seed}",
        supported,
        result,
    )


def _crr_convergence(
    request: M2WorkbenchRequest,
) -> tuple[CRRConvergencePoint, ...]:
    problem = request.composition.problem
    counts = (25, 50, 100, 200, 400, 800)
    points: list[CRRConvergencePoint] = []
    for steps in counts:
        method = CoxRossRubinstein(steps)
        supported = method.supports(problem)
        result = evaluate(problem, method) if supported else None
        points.append(CRRConvergencePoint(steps, supported, result))
    return tuple(points)


def _monte_carlo_convergence(
    request: M2WorkbenchRequest,
) -> tuple[MonteCarloConvergencePoint, ...]:
    problem = request.composition.problem
    seed = request.config.monte_carlo_seed
    counts = (2000, 5000, 10000, 20000)
    return tuple(
        MonteCarloConvergencePoint(
            paths,
            evaluate(problem, MonteCarloEuropeanOption(paths=paths, seed=seed)),
        )
        for paths in counts
    )


def _sensitivity_run(
    request: M2WorkbenchRequest,
    sensitivity: BlackScholesSensitivity,
) -> SensitivityRun:
    problem = BlackScholesSensitivityProblem(
        request.composition.problem,
        sensitivity,
    )
    analytic = AnalyticBlackScholesSensitivity()
    finite_difference = request.config.finite_difference_method
    analytic_supported = analytic.supports(problem)
    fd_supported = finite_difference.supports(problem)
    return SensitivityRun(
        sensitivity=sensitivity,
        analytic_supported=analytic_supported,
        analytic_result=(
            evaluate_sensitivity(problem, analytic) if analytic_supported else None
        ),
        finite_difference_supported=fd_supported,
        finite_difference_result=(
            evaluate_sensitivity(problem, finite_difference) if fd_supported else None
        ),
    )


def _greek_curve(
    request: M2WorkbenchRequest,
    sample_count: int = 41,
) -> tuple[GreekCurvePoint, ...]:
    base = request.composition.problem
    base_spot = base.current_state.value.spot
    upper = max(2.0 * base_spot, 1.0)
    lower = max(upper / 200.0, 1e-6)
    analytic = AnalyticBlackScholesSensitivity()
    finite_difference = request.config.finite_difference_method
    points: list[GreekCurvePoint] = []
    for index in range(sample_count):
        spot = lower + (upper - lower) * index / (sample_count - 1)
        current_state = replace(
            base.current_state,
            value=EquityState(spot),
        )
        pricing_problem = replace(base, current_state=current_state)
        problem = BlackScholesSensitivityProblem(
            pricing_problem,
            request.config.selected_greek,
        )
        analytic_result = (
            evaluate_sensitivity(problem, analytic)
            if analytic.supports(problem)
            else None
        )
        fd_result = (
            evaluate_sensitivity(problem, finite_difference)
            if finite_difference.supports(problem)
            else None
        )
        points.append(GreekCurvePoint(spot, analytic_result, fd_result))
    return tuple(points)


def _gamma_bump_study(
    request: M2WorkbenchRequest,
) -> tuple[GammaBumpPoint, ...]:
    problem = BlackScholesSensitivityProblem(
        request.composition.problem,
        BlackScholesSensitivity.GAMMA,
    )
    configured = request.config.finite_difference_method.spot_bump
    bumps = tuple(dict.fromkeys((5.0, 0.1, 0.01, 0.001, 1e-6, configured)))
    points: list[GammaBumpPoint] = []
    for bump in bumps:
        method = replace(
            request.config.finite_difference_method,
            spot_bump=bump,
        )
        supported = method.supports(problem)
        result = evaluate_sensitivity(problem, method) if supported else None
        points.append(GammaBumpPoint(bump, supported, result))
    return tuple(points)


def _positive_float(value: str, name: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if parsed <= 0.0:
        raise ValueError(f"{name} must be positive")
    return parsed


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
