"""Frontend-neutral UI4 Heston pricing and calibration workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from math import isfinite, sqrt

from qf_platform.inference import (
    HestonCalibrationBounds,
    HestonCalibrationCoordinates,
    HestonCalibrationProblem,
    HestonCalibrationResult,
    HestonCalibrationWeighting,
    HestonPriceCalibrationTarget,
    ScipyLeastSquaresHestonCalibration,
    calibrate_heston,
)
from qf_platform.pricing import (
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    HestonEquityState,
    HestonFourierEuropeanOption,
    HestonFourierValuationResult,
    HestonLaw,
    HestonMonteCarloEuropeanOption,
    HestonMonteCarloValuationResult,
    HestonParameters,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
    evaluate,
)


@dataclass(frozen=True, slots=True)
class HestonPricingDraft:
    """Text-valued draft state; typed finance objects exist only after normalization."""

    spot: str = "100"
    strike: str = "100"
    valuation_date: str = "2026-01-01"
    expiry: str = "2027-01-01"
    continuously_compounded_rate: str = "0.03"
    continuous_dividend_yield: str = "0.01"
    option_right: str = "call"
    initial_variance: str = "0.04"
    mean_reversion_speed: str = "2.0"
    long_run_variance: str = "0.04"
    volatility_of_variance: str = "0.5"
    correlation: str = "-0.7"
    fourier_lower_bound: str = "1e-8"
    fourier_upper_bound: str = "80"
    fourier_intervals: str = "256"
    monte_carlo_paths: str = "4000"
    monte_carlo_time_steps: str = "128"
    monte_carlo_seed: str = "1729"


@dataclass(frozen=True, slots=True)
class HestonPricingRequest:
    """One normalized Heston pricing question plus two independent M5 methods."""

    problem: PricingProblem[date, HestonEquityState, HestonParameters]
    fourier_method: HestonFourierEuropeanOption
    monte_carlo_method: HestonMonteCarloEuropeanOption


@dataclass(frozen=True, slots=True)
class HestonFourierStabilityPoint:
    """One same-problem Fourier resolution observation."""

    intervals: int
    present_value: float
    difference_from_selected: float


@dataclass(frozen=True, slots=True)
class HestonPricingAnalysis:
    """Completed M5 forward-pricing evidence for one shared Heston problem."""

    request: HestonPricingRequest
    fourier_result: HestonFourierValuationResult
    monte_carlo_result: HestonMonteCarloValuationResult
    fourier_stability: tuple[HestonFourierStabilityPoint, ...]
    absolute_method_difference: float
    difference_in_monte_carlo_standard_errors: float | None
    fourier_inside_monte_carlo_95: bool


@dataclass(frozen=True, slots=True)
class HestonCalibrationDraft:
    """Text-valued optimizer configuration for the concrete M6 synthetic workbench."""

    initial_variance: str = "0.06"
    mean_reversion_speed: str = "1.2"
    long_run_variance: str = "0.06"
    volatility_of_variance: str = "0.8"
    correlation: str = "-0.4"
    max_function_evaluations: str = "250"
    fourier_intervals: str = "128"


@dataclass(frozen=True, slots=True)
class HestonCalibrationWorkbenchRequest:
    """Concrete UI4 request over M6 price-space calibration semantics."""

    mode: str
    initial_guess: HestonCalibrationCoordinates
    max_function_evaluations: int
    fourier_intervals: int


@dataclass(frozen=True, slots=True)
class HestonCalibrationRun:
    """One explicit optimizer start and its immutable M6 result."""

    label: str
    initial_guess: HestonCalibrationCoordinates
    result: HestonCalibrationResult


@dataclass(frozen=True, slots=True)
class HestonCalibrationWorkbenchAnalysis:
    """Truth-known or deliberately underidentified M6 evidence for UI4."""

    mode: str
    truth: HestonCalibrationCoordinates
    problem: HestonCalibrationProblem
    runs: tuple[HestonCalibrationRun, ...]


@dataclass(frozen=True, slots=True)
class M6MarketStartEvidence:
    """One recorded real-market M6 optimizer start from the reference artifact."""

    initial_guess: tuple[float, float, float, float, float]
    estimate: tuple[float, float, float, float, float]
    objective_value: float
    function_evaluations: int


@dataclass(frozen=True, slots=True)
class M6MarketReference:
    """Package-safe mirror of the committed derived M6 SPX reference evidence."""

    source_reference: str
    source_repository: str
    source_commit: str
    source_path: str
    source_git_blob_sha1: str
    license_note: str
    quote_date: str
    underlying: str
    observed_spot: float
    expiries: tuple[str, ...]
    target_count: int
    weighting: str
    continuously_compounded_rate: float
    continuous_dividend_yield: float
    fourier_upper_bound: float
    fourier_intervals: int
    starts: tuple[M6MarketStartEvidence, ...]
    best_estimate: tuple[float, float, float, float, float]
    best_objective_value: float
    max_absolute_standardized_residual: float
    termination_status: int
    termination_message: str
    feller_discriminant: float
    feller_condition_satisfied: bool
    jacobian_rank: int
    singular_values: tuple[float, ...]
    condition_number: float
    standardized_residuals: tuple[float, ...]


def _parse_float(value: str, *, name: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not isfinite(parsed):
        raise ValueError(f"{name} must be finite")
    return parsed


def _parse_positive_int(value: str, *, name: str, minimum: int = 1) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if parsed < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return parsed


def _parse_int(value: str, *, name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _parse_date(value: str, *, name: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise ValueError(f"{name} must use YYYY-MM-DD") from exc


def _option_right(value: str) -> OptionRight:
    normalized = value.strip().lower()
    if normalized == "call":
        return OptionRight.CALL
    if normalized == "put":
        return OptionRight.PUT
    raise ValueError("option_right must be 'call' or 'put'")


def make_heston_pricing_request(draft: HestonPricingDraft) -> HestonPricingRequest:
    """Normalize UI text into one authoritative M5 Heston pricing composition."""

    valuation_date = _parse_date(draft.valuation_date, name="valuation_date")
    expiry = _parse_date(draft.expiry, name="expiry")
    spot = _parse_float(draft.spot, name="spot")
    strike = _parse_float(draft.strike, name="strike")
    rate = _parse_float(
        draft.continuously_compounded_rate,
        name="continuously_compounded_rate",
    )
    q = _parse_float(
        draft.continuous_dividend_yield,
        name="continuous_dividend_yield",
    )
    initial_variance = _parse_float(draft.initial_variance, name="initial_variance")
    parameters = HestonParameters(
        mean_reversion_speed=_parse_float(
            draft.mean_reversion_speed,
            name="mean_reversion_speed",
        ),
        long_run_variance=_parse_float(
            draft.long_run_variance,
            name="long_run_variance",
        ),
        volatility_of_variance=_parse_float(
            draft.volatility_of_variance,
            name="volatility_of_variance",
        ),
        correlation=_parse_float(draft.correlation, name="correlation"),
        continuous_dividend_yield=q,
    )
    law = HestonLaw()
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=valuation_date,
        continuously_compounded_rate=rate,
    )
    measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
    problem = PricingProblem(
        current_state=ModeledState(
            time=valuation_date,
            value=HestonEquityState(
                spot=spot,
                instantaneous_variance=initial_variance,
            ),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=parameters,
        contract=EuropeanOption(
            expiry=expiry,
            strike=strike,
            right=_option_right(draft.option_right),
        ),
        numeraire=numeraire,
        pricing_measure=measure,
    )
    fourier_method = HestonFourierEuropeanOption(
        integration_lower_bound=_parse_float(
            draft.fourier_lower_bound,
            name="fourier_lower_bound",
        ),
        integration_upper_bound=_parse_float(
            draft.fourier_upper_bound,
            name="fourier_upper_bound",
        ),
        intervals=_parse_positive_int(
            draft.fourier_intervals,
            name="fourier_intervals",
            minimum=2,
        ),
    )
    monte_carlo_method = HestonMonteCarloEuropeanOption(
        paths=_parse_positive_int(
            draft.monte_carlo_paths,
            name="monte_carlo_paths",
            minimum=2,
        ),
        time_steps=_parse_positive_int(
            draft.monte_carlo_time_steps,
            name="monte_carlo_time_steps",
        ),
        seed=_parse_int(draft.monte_carlo_seed, name="monte_carlo_seed"),
    )
    return HestonPricingRequest(
        problem=problem,
        fourier_method=fourier_method,
        monte_carlo_method=monte_carlo_method,
    )


def run_heston_pricing(request: HestonPricingRequest) -> HestonPricingAnalysis:
    """Run M5 Fourier and Monte Carlo methods over the exact same Heston problem."""

    fourier = evaluate(request.problem, request.fourier_method)
    monte_carlo = evaluate(request.problem, request.monte_carlo_method)

    selected_intervals = request.fourier_method.intervals
    candidates = tuple(
        sorted(
            {
                max(2, selected_intervals // 4 * 2),
                selected_intervals,
                selected_intervals * 2,
            }
        )
    )
    stability: list[HestonFourierStabilityPoint] = []
    for intervals in candidates:
        if intervals % 2:
            intervals += 1
        if intervals == selected_intervals:
            present_value = fourier.present_value
        else:
            method = HestonFourierEuropeanOption(
                integration_lower_bound=request.fourier_method.integration_lower_bound,
                integration_upper_bound=request.fourier_method.integration_upper_bound,
                intervals=intervals,
            )
            present_value = evaluate(request.problem, method).present_value
        stability.append(
            HestonFourierStabilityPoint(
                intervals=intervals,
                present_value=present_value,
                difference_from_selected=present_value - fourier.present_value,
            )
        )

    absolute_difference = abs(fourier.present_value - monte_carlo.present_value)
    standard_error_units = (
        None
        if monte_carlo.standard_error == 0.0
        else absolute_difference / monte_carlo.standard_error
    )
    lower, upper = monte_carlo.confidence_interval_95
    return HestonPricingAnalysis(
        request=request,
        fourier_result=fourier,
        monte_carlo_result=monte_carlo,
        fourier_stability=tuple(stability),
        absolute_method_difference=absolute_difference,
        difference_in_monte_carlo_standard_errors=standard_error_units,
        fourier_inside_monte_carlo_95=lower <= fourier.present_value <= upper,
    )


_SYNTHETIC_VALUATION_DATE = date(2026, 1, 1)
_SYNTHETIC_SPOT = 100.0
_SYNTHETIC_RATE = 0.03
_SYNTHETIC_Q = 0.01
_SYNTHETIC_TRUTH = HestonCalibrationCoordinates(
    initial_variance=0.04,
    parameters=HestonParameters(
        mean_reversion_speed=2.0,
        long_run_variance=0.04,
        volatility_of_variance=0.5,
        correlation=-0.7,
        continuous_dividend_yield=_SYNTHETIC_Q,
    ),
)
_SYNTHETIC_BOUNDS = HestonCalibrationBounds(
    minimum_initial_variance=0.005,
    maximum_initial_variance=0.15,
    minimum_mean_reversion_speed=0.2,
    maximum_mean_reversion_speed=6.0,
    minimum_long_run_variance=0.005,
    maximum_long_run_variance=0.15,
    minimum_volatility_of_variance=0.1,
    maximum_volatility_of_variance=1.5,
    minimum_correlation=-0.95,
    maximum_correlation=-0.1,
)
_ALTERNATE_START = HestonCalibrationCoordinates(
    initial_variance=0.02,
    parameters=HestonParameters(
        mean_reversion_speed=5.0,
        long_run_variance=0.02,
        volatility_of_variance=0.3,
        correlation=-0.85,
        continuous_dividend_yield=_SYNTHETIC_Q,
    ),
)


def make_heston_calibration_request(
    mode: str,
    draft: HestonCalibrationDraft,
) -> HestonCalibrationWorkbenchRequest:
    """Normalize direct financial coordinates and numerical configuration."""

    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"recovery", "thin"}:
        raise ValueError("calibration mode must be 'recovery' or 'thin'")
    initial_guess = HestonCalibrationCoordinates(
        initial_variance=_parse_float(draft.initial_variance, name="initial_variance"),
        parameters=HestonParameters(
            mean_reversion_speed=_parse_float(
                draft.mean_reversion_speed,
                name="mean_reversion_speed",
            ),
            long_run_variance=_parse_float(
                draft.long_run_variance,
                name="long_run_variance",
            ),
            volatility_of_variance=_parse_float(
                draft.volatility_of_variance,
                name="volatility_of_variance",
            ),
            correlation=_parse_float(draft.correlation, name="correlation"),
            continuous_dividend_yield=_SYNTHETIC_Q,
        ),
    )
    max_nfev = _parse_positive_int(
        draft.max_function_evaluations,
        name="max_function_evaluations",
    )
    intervals = _parse_positive_int(
        draft.fourier_intervals,
        name="fourier_intervals",
        minimum=2,
    )
    if intervals % 2:
        raise ValueError("fourier_intervals must be even")
    if not _SYNTHETIC_BOUNDS.contains(initial_guess):
        raise ValueError(
            "initial guess lies outside the UI4 synthetic calibration domain"
        )
    return HestonCalibrationWorkbenchRequest(
        mode=normalized_mode,
        initial_guess=initial_guess,
        max_function_evaluations=max_nfev,
        fourier_intervals=intervals,
    )


def _synthetic_forward(intervals: int) -> HestonFourierEuropeanOption:
    return HestonFourierEuropeanOption(
        integration_upper_bound=80.0,
        intervals=intervals,
    )


def _synthetic_market_semantics() -> tuple[
    FlatMoneyMarketNumeraire,
    PricingMeasureSemantics[date],
]:
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_SYNTHETIC_VALUATION_DATE,
        continuously_compounded_rate=_SYNTHETIC_RATE,
    )
    return numeraire, PricingMeasureSemantics(name="Q^N", numeraire=numeraire)


def _synthetic_target_price(
    contract: EuropeanOption,
    *,
    forward_method: HestonFourierEuropeanOption,
) -> float:
    numeraire, measure = _synthetic_market_semantics()
    law = HestonLaw()
    problem = PricingProblem(
        current_state=ModeledState(
            time=_SYNTHETIC_VALUATION_DATE,
            value=HestonEquityState(
                spot=_SYNTHETIC_SPOT,
                instantaneous_variance=_SYNTHETIC_TRUTH.initial_variance,
            ),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=_SYNTHETIC_TRUTH.parameters,
        contract=contract,
        numeraire=numeraire,
        pricing_measure=measure,
    )
    return evaluate(problem, forward_method).present_value


def _synthetic_targets(
    *,
    forward_method: HestonFourierEuropeanOption,
) -> tuple[HestonPriceCalibrationTarget, ...]:
    targets: list[HestonPriceCalibrationTarget] = []
    for days in (91, 182, 365, 548):
        expiry = _SYNTHETIC_VALUATION_DATE + timedelta(days=days)
        for strike in (80.0, 90.0, 100.0, 110.0, 120.0):
            contract = EuropeanOption(
                expiry=expiry,
                strike=strike,
                right=OptionRight.CALL,
            )
            targets.append(
                HestonPriceCalibrationTarget.synthetic(
                    contract=contract,
                    target_price=_synthetic_target_price(
                        contract,
                        forward_method=forward_method,
                    ),
                    label=f"T{days}-K{strike:g}",
                )
            )
    return tuple(targets)


def run_heston_calibration(
    request: HestonCalibrationWorkbenchRequest,
) -> HestonCalibrationWorkbenchAnalysis:
    """Run a truth-known or deliberately thin M6 calibration from two explicit starts."""

    forward_method = _synthetic_forward(request.fourier_intervals)
    all_targets = _synthetic_targets(forward_method=forward_method)
    targets = (
        all_targets
        if request.mode == "recovery"
        else (all_targets[7], all_targets[8], all_targets[9])
    )
    numeraire, measure = _synthetic_market_semantics()
    problem = HestonCalibrationProblem(
        valuation_date=_SYNTHETIC_VALUATION_DATE,
        spot=_SYNTHETIC_SPOT,
        targets=targets,
        numeraire=numeraire,
        pricing_measure=measure,
        continuous_dividend_yield=_SYNTHETIC_Q,
        bounds=_SYNTHETIC_BOUNDS,
        weighting=HestonCalibrationWeighting.UNIFORM_PRICE,
        forward_method=forward_method,
    )
    starts = (
        ("Selected start", request.initial_guess),
        ("Alternate start", _ALTERNATE_START),
    )
    runs = tuple(
        HestonCalibrationRun(
            label=label,
            initial_guess=start,
            result=calibrate_heston(
                problem,
                ScipyLeastSquaresHestonCalibration(
                    initial_guess=start,
                    max_function_evaluations=request.max_function_evaluations,
                ),
            ),
        )
        for label, start in starts
    )
    return HestonCalibrationWorkbenchAnalysis(
        mode=request.mode,
        truth=_SYNTHETIC_TRUTH,
        problem=problem,
        runs=runs,
    )


def canonical_m6_market_reference() -> M6MarketReference:
    """Return reviewed derived M6 SPX evidence mirrored for standalone UI packaging.

    Values are copied exactly from ``docs/evidence/m6_spx_heston_calibration_reference.json``.
    That committed artifact and the raw replay script remain authoritative; this mirror
    exists because the standalone Qt executable does not package repository-level docs.
    """

    return M6MarketReference(
        source_reference="docs/evidence/m6_spx_heston_calibration_reference.json",
        source_repository="IceCurrent/local_volatility_model",
        source_commit="428531599bf3945f5d51691fdd21b1667eb14958",
        source_path="data/data.csv",
        source_git_blob_sha1="8d1db0f2710c4707555c8263f9b7f8f527974836",
        license_note=(
            "No source-repository license file was identified for M4/M6 evidence. "
            "Raw rows are not redistributed."
        ),
        quote_date="2023-01-04",
        underlying="SPX",
        observed_spot=3853.39,
        expiries=("2023-02-03", "2023-04-28"),
        target_count=14,
        weighting="bid_ask_half_spread",
        continuously_compounded_rate=0.045,
        continuous_dividend_yield=0.017,
        fourier_upper_bound=100.0,
        fourier_intervals=256,
        starts=(
            M6MarketStartEvidence(
                initial_guess=(0.04, 2.0, 0.04, 0.5, -0.7),
                estimate=(
                    0.04446682528995597,
                    3.2574605790260347,
                    0.0662244169927708,
                    0.6271475834275344,
                    -0.7793725494253791,
                ),
                objective_value=12.557496300536641,
                function_evaluations=22,
            ),
            M6MarketStartEvidence(
                initial_guess=(0.06, 1.0, 0.06, 0.8, -0.4),
                estimate=(
                    0.044466829645169396,
                    3.2574951682764226,
                    0.06622419630606502,
                    0.6271480488914908,
                    -0.7793735964788578,
                ),
                objective_value=12.557496294581263,
                function_evaluations=26,
            ),
            M6MarketStartEvidence(
                initial_guess=(0.02, 5.0, 0.02, 0.3, -0.85),
                estimate=(
                    0.0444668236448224,
                    3.2574277225393713,
                    0.06622464475623452,
                    0.6271477743895937,
                    -0.7793710927374115,
                ),
                objective_value=12.557496311978834,
                function_evaluations=16,
            ),
        ),
        best_estimate=(
            0.044466829645169396,
            3.2574951682764226,
            0.06622419630606502,
            0.6271480488914908,
            -0.7793735964788578,
        ),
        best_objective_value=12.557496294581263,
        max_absolute_standardized_residual=1.7807557078435874,
        termination_status=3,
        termination_message="xtol termination condition satisfied",
        feller_discriminant=0.03813532375158857,
        feller_condition_satisfied=True,
        jacobian_rank=5,
        singular_values=(
            9338.22177451889,
            2133.80959834023,
            563.2542372480372,
            74.56494976670845,
            23.120377478609807,
        ),
        condition_number=403.8957315103656,
        standardized_residuals=(
            -0.02699291,
            -0.36881627,
            -1.78075571,
            1.55791741,
            -0.06336414,
            0.77243334,
            -1.09253594,
            0.59482662,
            0.28713091,
            -1.22726836,
            -0.95664224,
            1.42437023,
            0.21265512,
            -0.31076359,
        ),
    )


def annualized_volatility_from_variance(variance: float) -> float:
    """Return sqrt(v) for presentation while keeping variance semantics explicit."""

    if not isfinite(variance) or variance < 0.0:
        raise ValueError("variance must be non-negative and finite")
    return sqrt(variance)


__all__ = [
    "HestonCalibrationDraft",
    "HestonCalibrationRun",
    "HestonCalibrationWorkbenchAnalysis",
    "HestonCalibrationWorkbenchRequest",
    "HestonFourierStabilityPoint",
    "HestonPricingAnalysis",
    "HestonPricingDraft",
    "HestonPricingRequest",
    "M6MarketReference",
    "M6MarketStartEvidence",
    "annualized_volatility_from_variance",
    "canonical_m6_market_reference",
    "make_heston_calibration_request",
    "make_heston_pricing_request",
    "run_heston_calibration",
    "run_heston_pricing",
]
