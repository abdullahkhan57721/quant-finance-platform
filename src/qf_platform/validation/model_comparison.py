"""Concrete M7 Black-Scholes versus Heston empirical validation semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from math import exp, log, sqrt
from statistics import fmean
from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import least_squares

from qf_platform._validation import finite_real
from qf_platform.inference import (
    HestonCalibrationBounds,
    HestonCalibrationConvergenceError,
    HestonCalibrationCoordinates,
    HestonCalibrationProblem,
    HestonCalibrationResult,
    HestonCalibrationWeighting,
    HestonPriceCalibrationTarget,
    ScipyLeastSquaresHestonCalibration,
    calibrate_heston,
)
from qf_platform.market_data import NormalizedOptionObservation
from qf_platform.pricing import (
    BlackScholesClosedForm,
    BlackScholesLaw,
    BlackScholesParameters,
    EquityState,
    FlatMoneyMarketNumeraire,
    HestonEquityState,
    HestonFourierEuropeanOption,
    HestonLaw,
    ModeledState,
    PricingMeasureSemantics,
    PricingProblem,
    actual_365_fixed_year_fraction,
    evaluate,
)


class InvalidBlackScholesHestonValidationProblem(ValueError):
    """Raised when M7's concrete validation question is not well formed."""


class BlackScholesBenchmarkConvergenceError(RuntimeError):
    """Raised when the concrete one-volatility benchmark fit does not converge."""


class ValidationPartition(StrEnum):
    """Predeclared role of an observation in the M7 comparison."""

    TRAINING = "training"
    EVALUATION = "evaluation"


class ValidationModel(StrEnum):
    """Concrete model identity in the first empirical comparison."""

    BLACK_SCHOLES = "black_scholes"
    HESTON = "heston"


@dataclass(frozen=True, slots=True)
class BlackScholesHestonValidationProblem:
    """Financial statement of M7's same-date cross-sectional validation question.

    Observations and train/evaluation roles are problem semantics. Optimizer starts and
    tolerances remain method configuration.
    """

    observations: tuple[NormalizedOptionObservation, ...]
    training_contract_ids: tuple[str, ...]
    evaluation_contract_ids: tuple[str, ...]
    numeraire: FlatMoneyMarketNumeraire
    pricing_measure: PricingMeasureSemantics[date]
    continuous_dividend_yield: float
    heston_bounds: HestonCalibrationBounds = field(
        default_factory=HestonCalibrationBounds
    )
    heston_forward_method: HestonFourierEuropeanOption = field(
        default_factory=HestonFourierEuropeanOption
    )
    minimum_black_scholes_volatility: float = 1.0e-4
    maximum_black_scholes_volatility: float = 5.0

    def __post_init__(self) -> None:
        if type(self.observations) is not tuple or not self.observations:
            msg = "observations must be a non-empty tuple"
            raise InvalidBlackScholesHestonValidationProblem(msg)
        if (
            type(self.training_contract_ids) is not tuple
            or not self.training_contract_ids
        ):
            msg = "training_contract_ids must be a non-empty tuple"
            raise InvalidBlackScholesHestonValidationProblem(msg)
        if (
            type(self.evaluation_contract_ids) is not tuple
            or not self.evaluation_contract_ids
        ):
            msg = "evaluation_contract_ids must be a non-empty tuple"
            raise InvalidBlackScholesHestonValidationProblem(msg)
        if self.pricing_measure.numeraire is not self.numeraire:
            msg = "pricing_measure must reference the validation numeraire"
            raise InvalidBlackScholesHestonValidationProblem(msg)

        object.__setattr__(
            self,
            "continuous_dividend_yield",
            finite_real(
                self.continuous_dividend_yield,
                name="continuous_dividend_yield",
            ),
        )
        minimum = finite_real(
            self.minimum_black_scholes_volatility,
            name="minimum_black_scholes_volatility",
        )
        maximum = finite_real(
            self.maximum_black_scholes_volatility,
            name="maximum_black_scholes_volatility",
        )
        if minimum < 0.0 or maximum <= minimum:
            msg = "Black-Scholes validation volatility bounds are invalid"
            raise InvalidBlackScholesHestonValidationProblem(msg)
        object.__setattr__(self, "minimum_black_scholes_volatility", minimum)
        object.__setattr__(self, "maximum_black_scholes_volatility", maximum)
        self._validate_observations_and_partition()

    def _validate_observations_and_partition(self) -> None:
        ids: list[str] = []
        market_dates: set[date] = set()
        spots: set[float] = set()
        underlyings: set[str] = set()
        for observation in self.observations:
            quote = observation.raw_quote
            if not quote.contract_id:
                msg = "validation observations require non-empty contract identifiers"
                raise InvalidBlackScholesHestonValidationProblem(msg)
            if quote.bid is None or quote.ask is None or quote.ask <= quote.bid:
                msg = (
                    "validation observations require a strictly positive bid/ask spread"
                )
                raise InvalidBlackScholesHestonValidationProblem(msg)
            ids.append(quote.contract_id)
            market_dates.add(observation.valuation_date)
            spots.add(observation.spot)
            underlyings.add(observation.raw_underlying.underlying_id)

        if len(ids) != len(set(ids)):
            msg = "validation observation contract identifiers must be unique"
            raise InvalidBlackScholesHestonValidationProblem(msg)
        if len(market_dates) != 1 or len(spots) != 1 or len(underlyings) != 1:
            msg = "validation observations must share market date, spot, and underlying"
            raise InvalidBlackScholesHestonValidationProblem(msg)

        training = set(self.training_contract_ids)
        evaluation = set(self.evaluation_contract_ids)
        if len(training) != len(self.training_contract_ids) or len(evaluation) != len(
            self.evaluation_contract_ids
        ):
            msg = "validation partition identifiers must be unique"
            raise InvalidBlackScholesHestonValidationProblem(msg)
        if training & evaluation:
            msg = "training and evaluation partitions must not overlap"
            raise InvalidBlackScholesHestonValidationProblem(msg)
        if training | evaluation != set(ids):
            msg = "every validation observation must be assigned exactly once"
            raise InvalidBlackScholesHestonValidationProblem(msg)

    @property
    def valuation_date(self) -> date:
        return self.observations[0].valuation_date

    @property
    def spot(self) -> float:
        return self.observations[0].spot

    @property
    def training_observations(self) -> tuple[NormalizedOptionObservation, ...]:
        training = set(self.training_contract_ids)
        return tuple(
            observation
            for observation in self.observations
            if observation.raw_quote.contract_id in training
        )

    @property
    def evaluation_observations(self) -> tuple[NormalizedOptionObservation, ...]:
        evaluation = set(self.evaluation_contract_ids)
        return tuple(
            observation
            for observation in self.observations
            if observation.raw_quote.contract_id in evaluation
        )

    def partition_for(self, contract_id: str, /) -> ValidationPartition:
        if contract_id in set(self.training_contract_ids):
            return ValidationPartition.TRAINING
        if contract_id in set(self.evaluation_contract_ids):
            return ValidationPartition.EVALUATION
        raise KeyError(contract_id)


@dataclass(frozen=True, slots=True)
class BlackScholesBenchmarkFit:
    """One fitted constant-volatility benchmark from training prices only."""

    annualized_volatility: float
    objective_value: float
    function_evaluations: int
    termination_status: int
    termination_message: str


@dataclass(frozen=True, slots=True)
class HestonStartEvidence:
    """Outcome of one explicit Heston optimizer start."""

    initial_guess: HestonCalibrationCoordinates
    result: HestonCalibrationResult | None
    failure_message: str | None

    def __post_init__(self) -> None:
        if (self.result is None) == (self.failure_message is None):
            msg = "Heston start evidence must contain exactly one outcome"
            raise ValueError(msg)

    @property
    def converged(self) -> bool:
        return self.result is not None


@dataclass(frozen=True, slots=True)
class ModelResidualEvidence:
    """One immutable observed-versus-model pricing comparison."""

    contract_id: str
    model: ValidationModel
    partition: ValidationPartition
    expiry: date
    strike: float
    right: str
    log_forward_moneyness: float
    observed_price: float
    model_price: float
    residual: float
    half_spread: float
    standardized_residual: float
    relative_absolute_error: float


@dataclass(frozen=True, slots=True)
class ValidationMetrics:
    """Aggregate price-space evidence for one model and one partition."""

    observation_count: int
    mean_residual: float
    mean_absolute_error: float
    root_mean_square_error: float
    relative_mean_absolute_error: float
    standardized_mean_absolute_error: float
    standardized_root_mean_square_error: float
    maximum_absolute_standardized_residual: float


@dataclass(frozen=True, slots=True)
class HestonParameterStabilityEvidence:
    """Multiple-start and train-versus-full-sample parameter stability evidence."""

    successful_training_starts: int
    failed_training_starts: int
    maximum_training_start_domain_scaled_spread: float
    training_condition_number: float | None
    training_jacobian_rank: int
    full_sample_condition_number: float | None
    full_sample_jacobian_rank: int
    train_to_full_domain_scaled_shifts: tuple[float, float, float, float, float]
    maximum_train_to_full_domain_scaled_shift: float


@dataclass(frozen=True, slots=True)
class ValidationComputationEvidence:
    """Structural workload evidence handed to M8; not a performance benchmark."""

    black_scholes_training_function_evaluations: int
    heston_training_target_count: int
    heston_training_start_count: int
    heston_training_function_evaluations: tuple[int, ...]
    heston_training_jacobian_evaluations: tuple[int, ...]
    heston_full_sample_target_count: int
    heston_full_sample_start_count: int
    heston_full_sample_function_evaluations: tuple[int, ...]
    heston_full_sample_jacobian_evaluations: tuple[int, ...]
    heston_fourier_upper_bound: float
    heston_fourier_intervals: int


@dataclass(frozen=True, slots=True)
class BlackScholesHestonValidationConclusion:
    """Bounded interpretation of the evidence, not a universal model ranking."""

    heston_lower_training_price_rmse: bool
    heston_lower_evaluation_price_rmse: bool
    heston_lower_evaluation_standardized_rmse: bool
    temporal_out_of_sample_tested: bool
    heston_hedge_comparison_supported: bool
    statement: str


@dataclass(frozen=True, slots=True)
class BlackScholesHestonValidationEvidence:
    """Completed evidence from one concrete M7 validation execution."""

    problem: BlackScholesHestonValidationProblem
    black_scholes_fit: BlackScholesBenchmarkFit
    selected_heston_training_result: HestonCalibrationResult
    heston_training_starts: tuple[HestonStartEvidence, ...]
    selected_heston_full_sample_result: HestonCalibrationResult
    heston_full_sample_starts: tuple[HestonStartEvidence, ...]
    residuals: tuple[ModelResidualEvidence, ...]
    black_scholes_training_metrics: ValidationMetrics
    black_scholes_evaluation_metrics: ValidationMetrics
    heston_training_metrics: ValidationMetrics
    heston_evaluation_metrics: ValidationMetrics
    heston_stability: HestonParameterStabilityEvidence
    computation: ValidationComputationEvidence
    conclusion: BlackScholesHestonValidationConclusion


@dataclass(frozen=True, slots=True)
class CrossSectionalBlackScholesHestonValidation:
    """Concrete execution method for M7's predeclared same-date comparison."""

    black_scholes_initial_volatility: float
    heston_initial_guesses: tuple[HestonCalibrationCoordinates, ...]
    function_tolerance: float = 1.0e-10
    coordinate_tolerance: float = 1.0e-10
    gradient_tolerance: float = 1.0e-10
    max_function_evaluations: int = 300

    def __post_init__(self) -> None:
        initial = finite_real(
            self.black_scholes_initial_volatility,
            name="black_scholes_initial_volatility",
        )
        if initial < 0.0:
            msg = "black_scholes_initial_volatility must be non-negative"
            raise ValueError(msg)
        object.__setattr__(self, "black_scholes_initial_volatility", initial)
        if (
            type(self.heston_initial_guesses) is not tuple
            or not self.heston_initial_guesses
        ):
            msg = "heston_initial_guesses must be a non-empty tuple"
            raise ValueError(msg)
        for name in (
            "function_tolerance",
            "coordinate_tolerance",
            "gradient_tolerance",
        ):
            value = finite_real(getattr(self, name), name=name)
            if value <= 0.0:
                msg = f"{name} must be strictly positive"
                raise ValueError(msg)
            object.__setattr__(self, name, value)
        if type(self.max_function_evaluations) is not int:
            msg = "max_function_evaluations must be an integer"
            raise TypeError(msg)
        if self.max_function_evaluations <= 0:
            msg = "max_function_evaluations must be strictly positive"
            raise ValueError(msg)

    def apply(
        self,
        problem: BlackScholesHestonValidationProblem,
        /,
    ) -> BlackScholesHestonValidationEvidence:
        black_scholes_fit = _fit_black_scholes(problem, self)
        training_problem = _heston_problem(problem, problem.training_observations)
        training_starts = _calibrate_heston_starts(training_problem, self)
        selected_training = _best_heston_result(training_starts, purpose="training")

        residuals = _model_residuals(
            problem,
            black_scholes_volatility=black_scholes_fit.annualized_volatility,
            heston_coordinates=selected_training.estimate,
        )
        bs_training = _metrics(
            residuals,
            ValidationModel.BLACK_SCHOLES,
            ValidationPartition.TRAINING,
        )
        bs_evaluation = _metrics(
            residuals,
            ValidationModel.BLACK_SCHOLES,
            ValidationPartition.EVALUATION,
        )
        heston_training = _metrics(
            residuals,
            ValidationModel.HESTON,
            ValidationPartition.TRAINING,
        )
        heston_evaluation = _metrics(
            residuals,
            ValidationModel.HESTON,
            ValidationPartition.EVALUATION,
        )

        # Full-sample calibration occurs only after held-out prices/metrics are fixed.
        # It is stability evidence and cannot feed back into evaluation predictions.
        full_problem = _heston_problem(problem, problem.observations)
        full_starts = _calibrate_heston_starts(full_problem, self)
        selected_full = _best_heston_result(
            full_starts,
            purpose="full-sample stability",
        )
        stability = _stability(
            problem,
            training_starts,
            selected_training,
            selected_full,
        )
        computation = _computation_evidence(
            problem,
            black_scholes_fit,
            training_starts,
            full_starts,
        )
        conclusion = _conclusion(
            bs_training=bs_training,
            bs_evaluation=bs_evaluation,
            heston_training=heston_training,
            heston_evaluation=heston_evaluation,
        )
        return BlackScholesHestonValidationEvidence(
            problem=problem,
            black_scholes_fit=black_scholes_fit,
            selected_heston_training_result=selected_training,
            heston_training_starts=training_starts,
            selected_heston_full_sample_result=selected_full,
            heston_full_sample_starts=full_starts,
            residuals=residuals,
            black_scholes_training_metrics=bs_training,
            black_scholes_evaluation_metrics=bs_evaluation,
            heston_training_metrics=heston_training,
            heston_evaluation_metrics=heston_evaluation,
            heston_stability=stability,
            computation=computation,
            conclusion=conclusion,
        )


def validate_black_scholes_vs_heston(
    problem: BlackScholesHestonValidationProblem,
    method: CrossSectionalBlackScholesHestonValidation,
    /,
) -> BlackScholesHestonValidationEvidence:
    """Execute the concrete M7 validation problem with its supported method."""

    return method.apply(problem)


def predeclared_every_third_evaluation_partition(
    observations: tuple[NormalizedOptionObservation, ...],
    /,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Apply M7's data-independent same-date cross-sectional holdout rule.

    Observations are sorted by expiry and strike. Zero-based indices satisfying
    ``index % 3 == 2`` are evaluation observations.
    """

    ordered = sorted(
        observations,
        key=lambda item: (item.raw_quote.expiry, item.raw_quote.strike),
    )
    training: list[str] = []
    evaluation: list[str] = []
    for index, observation in enumerate(ordered):
        selected = evaluation if index % 3 == 2 else training
        selected.append(observation.raw_quote.contract_id)
    return tuple(training), tuple(evaluation)


def _half_spread(observation: NormalizedOptionObservation) -> float:
    bid = observation.raw_quote.bid
    ask = observation.raw_quote.ask
    if bid is None or ask is None or ask <= bid:
        msg = "M7 price comparison requires a strictly positive bid/ask spread"
        raise InvalidBlackScholesHestonValidationProblem(msg)
    return 0.5 * (ask - bid)


def _contract(observation: NormalizedOptionObservation):
    return HestonPriceCalibrationTarget.from_normalized_observation(
        observation
    ).contract


def _black_scholes_price(
    problem: BlackScholesHestonValidationProblem,
    observation: NormalizedOptionObservation,
    annualized_volatility: float,
) -> float:
    law = BlackScholesLaw()
    pricing_problem = PricingProblem(
        current_state=ModeledState(
            time=problem.valuation_date,
            value=EquityState(problem.spot),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=BlackScholesParameters(
            annualized_volatility=annualized_volatility,
            continuous_dividend_yield=problem.continuous_dividend_yield,
        ),
        contract=_contract(observation),
        numeraire=problem.numeraire,
        pricing_measure=problem.pricing_measure,
    )
    return evaluate(pricing_problem, BlackScholesClosedForm()).present_value


def _fit_black_scholes(
    problem: BlackScholesHestonValidationProblem,
    method: CrossSectionalBlackScholesHestonValidation,
) -> BlackScholesBenchmarkFit:
    if not (
        problem.minimum_black_scholes_volatility
        <= method.black_scholes_initial_volatility
        <= problem.maximum_black_scholes_volatility
    ):
        msg = "Black-Scholes initial volatility lies outside the validation domain"
        raise ValueError(msg)
    training = problem.training_observations

    def residual_vector(values: NDArray[np.float64]) -> NDArray[np.float64]:
        volatility = float(values[0])
        return np.asarray(
            [
                (
                    _black_scholes_price(problem, observation, volatility)
                    - observation.target_price
                )
                / _half_spread(observation)
                for observation in training
            ],
            dtype=np.float64,
        )

    optimizer_result = least_squares(
        residual_vector,
        np.asarray([method.black_scholes_initial_volatility], dtype=np.float64),
        bounds=(
            np.asarray(
                [problem.minimum_black_scholes_volatility],
                dtype=np.float64,
            ),
            np.asarray(
                [problem.maximum_black_scholes_volatility],
                dtype=np.float64,
            ),
        ),
        method="trf",
        jac="2-point",
        x_scale="jac",
        ftol=method.function_tolerance,
        xtol=method.coordinate_tolerance,
        gtol=method.gradient_tolerance,
        max_nfev=method.max_function_evaluations,
    )
    if not optimizer_result.success:
        msg = (
            f"Black-Scholes benchmark fit did not converge: {optimizer_result.message}"
        )
        raise BlackScholesBenchmarkConvergenceError(msg)
    solution = cast(NDArray[np.float64], optimizer_result.x)
    residuals = residual_vector(solution)
    return BlackScholesBenchmarkFit(
        annualized_volatility=float(solution[0]),
        objective_value=float(np.dot(residuals, residuals)),
        function_evaluations=int(optimizer_result.nfev),
        termination_status=int(cast(int, optimizer_result.status)),
        termination_message=str(optimizer_result.message),
    )


def _heston_problem(
    problem: BlackScholesHestonValidationProblem,
    observations: tuple[NormalizedOptionObservation, ...],
) -> HestonCalibrationProblem:
    targets = tuple(
        HestonPriceCalibrationTarget.from_normalized_observation(observation)
        for observation in observations
    )
    return HestonCalibrationProblem(
        valuation_date=problem.valuation_date,
        spot=problem.spot,
        targets=targets,
        numeraire=problem.numeraire,
        pricing_measure=problem.pricing_measure,
        continuous_dividend_yield=problem.continuous_dividend_yield,
        bounds=problem.heston_bounds,
        weighting=HestonCalibrationWeighting.BID_ASK_HALF_SPREAD,
        forward_method=problem.heston_forward_method,
    )


def _calibrate_heston_starts(
    calibration_problem: HestonCalibrationProblem,
    method: CrossSectionalBlackScholesHestonValidation,
) -> tuple[HestonStartEvidence, ...]:
    outcomes: list[HestonStartEvidence] = []
    for initial_guess in method.heston_initial_guesses:
        calibration_method = ScipyLeastSquaresHestonCalibration(
            initial_guess=initial_guess,
            function_tolerance=method.function_tolerance,
            coordinate_tolerance=method.coordinate_tolerance,
            gradient_tolerance=method.gradient_tolerance,
            max_function_evaluations=method.max_function_evaluations,
        )
        try:
            result = calibrate_heston(calibration_problem, calibration_method)
        except HestonCalibrationConvergenceError as exc:
            outcomes.append(
                HestonStartEvidence(
                    initial_guess=initial_guess,
                    result=None,
                    failure_message=str(exc),
                )
            )
        else:
            outcomes.append(
                HestonStartEvidence(
                    initial_guess=initial_guess,
                    result=result,
                    failure_message=None,
                )
            )
    return tuple(outcomes)


def _best_heston_result(
    starts: tuple[HestonStartEvidence, ...],
    *,
    purpose: str,
) -> HestonCalibrationResult:
    converged = [item.result for item in starts if item.result is not None]
    if not converged:
        msg = f"no Heston calibration start converged for {purpose}"
        raise HestonCalibrationConvergenceError(msg)
    return min(converged, key=lambda result: result.objective_value)


def _heston_price(
    problem: BlackScholesHestonValidationProblem,
    observation: NormalizedOptionObservation,
    coordinates: HestonCalibrationCoordinates,
) -> float:
    law = HestonLaw()
    pricing_problem = PricingProblem(
        current_state=ModeledState(
            time=problem.valuation_date,
            value=HestonEquityState(
                spot=problem.spot,
                instantaneous_variance=coordinates.initial_variance,
            ),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=coordinates.parameters,
        contract=_contract(observation),
        numeraire=problem.numeraire,
        pricing_measure=problem.pricing_measure,
    )
    return evaluate(pricing_problem, problem.heston_forward_method).present_value


def _log_forward_moneyness(
    problem: BlackScholesHestonValidationProblem,
    observation: NormalizedOptionObservation,
) -> float:
    year_fraction = actual_365_fixed_year_fraction(
        problem.valuation_date,
        observation.raw_quote.expiry,
    )
    forward = problem.spot * exp(
        (
            problem.numeraire.continuously_compounded_rate
            - problem.continuous_dividend_yield
        )
        * year_fraction
    )
    return log(observation.raw_quote.strike / forward)


def _one_residual(
    problem: BlackScholesHestonValidationProblem,
    observation: NormalizedOptionObservation,
    *,
    model: ValidationModel,
    model_price: float,
) -> ModelResidualEvidence:
    observed = observation.target_price
    residual = model_price - observed
    half_spread = _half_spread(observation)
    return ModelResidualEvidence(
        contract_id=observation.raw_quote.contract_id,
        model=model,
        partition=problem.partition_for(observation.raw_quote.contract_id),
        expiry=observation.raw_quote.expiry,
        strike=observation.raw_quote.strike,
        right=observation.raw_quote.right.value,
        log_forward_moneyness=_log_forward_moneyness(problem, observation),
        observed_price=observed,
        model_price=model_price,
        residual=residual,
        half_spread=half_spread,
        standardized_residual=residual / half_spread,
        relative_absolute_error=abs(residual) / observed,
    )


def _model_residuals(
    problem: BlackScholesHestonValidationProblem,
    *,
    black_scholes_volatility: float,
    heston_coordinates: HestonCalibrationCoordinates,
) -> tuple[ModelResidualEvidence, ...]:
    residuals: list[ModelResidualEvidence] = []
    for observation in problem.observations:
        residuals.append(
            _one_residual(
                problem,
                observation,
                model=ValidationModel.BLACK_SCHOLES,
                model_price=_black_scholes_price(
                    problem,
                    observation,
                    black_scholes_volatility,
                ),
            )
        )
        residuals.append(
            _one_residual(
                problem,
                observation,
                model=ValidationModel.HESTON,
                model_price=_heston_price(problem, observation, heston_coordinates),
            )
        )
    return tuple(residuals)


def _metrics(
    residuals: tuple[ModelResidualEvidence, ...],
    model: ValidationModel,
    partition: ValidationPartition,
) -> ValidationMetrics:
    selected = tuple(
        item
        for item in residuals
        if item.model is model and item.partition is partition
    )
    if not selected:
        msg = "validation metrics require at least one residual"
        raise ValueError(msg)
    errors = tuple(item.residual for item in selected)
    standardized = tuple(item.standardized_residual for item in selected)
    return ValidationMetrics(
        observation_count=len(selected),
        mean_residual=fmean(errors),
        mean_absolute_error=fmean(abs(value) for value in errors),
        root_mean_square_error=sqrt(fmean(value * value for value in errors)),
        relative_mean_absolute_error=fmean(
            item.relative_absolute_error for item in selected
        ),
        standardized_mean_absolute_error=fmean(abs(value) for value in standardized),
        standardized_root_mean_square_error=sqrt(
            fmean(value * value for value in standardized)
        ),
        maximum_absolute_standardized_residual=max(
            abs(value) for value in standardized
        ),
    )


def _max_domain_scaled_start_spread(
    starts: tuple[HestonStartEvidence, ...],
    widths: tuple[float, float, float, float, float],
) -> float:
    vectors = [
        item.result.estimate.as_vector() for item in starts if item.result is not None
    ]
    if len(vectors) < 2:
        return 0.0
    maximum = 0.0
    for index in range(5):
        values = [vector[index] for vector in vectors]
        maximum = max(
            maximum,
            (max(values) - min(values)) / widths[index],
        )
    return maximum


def _stability(
    problem: BlackScholesHestonValidationProblem,
    training_starts: tuple[HestonStartEvidence, ...],
    selected_training: HestonCalibrationResult,
    selected_full: HestonCalibrationResult,
) -> HestonParameterStabilityEvidence:
    widths = problem.heston_bounds.widths
    shifts = tuple(
        abs(train - full) / width
        for train, full, width in zip(
            selected_training.estimate.as_vector(),
            selected_full.estimate.as_vector(),
            widths,
            strict=True,
        )
    )
    successful = sum(item.converged for item in training_starts)
    return HestonParameterStabilityEvidence(
        successful_training_starts=successful,
        failed_training_starts=len(training_starts) - successful,
        maximum_training_start_domain_scaled_spread=(
            _max_domain_scaled_start_spread(training_starts, widths)
        ),
        training_condition_number=selected_training.conditioning.condition_number,
        training_jacobian_rank=selected_training.conditioning.jacobian_rank,
        full_sample_condition_number=selected_full.conditioning.condition_number,
        full_sample_jacobian_rank=selected_full.conditioning.jacobian_rank,
        train_to_full_domain_scaled_shifts=cast(
            tuple[float, float, float, float, float],
            shifts,
        ),
        maximum_train_to_full_domain_scaled_shift=max(shifts),
    )


def _successful_counts(
    starts: tuple[HestonStartEvidence, ...],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    function_evaluations = tuple(
        item.result.function_evaluations for item in starts if item.result is not None
    )
    jacobian_evaluations = tuple(
        item.result.jacobian_evaluations for item in starts if item.result is not None
    )
    return function_evaluations, jacobian_evaluations


def _computation_evidence(
    problem: BlackScholesHestonValidationProblem,
    black_scholes_fit: BlackScholesBenchmarkFit,
    training_starts: tuple[HestonStartEvidence, ...],
    full_starts: tuple[HestonStartEvidence, ...],
) -> ValidationComputationEvidence:
    training_nfev, training_njev = _successful_counts(training_starts)
    full_nfev, full_njev = _successful_counts(full_starts)
    return ValidationComputationEvidence(
        black_scholes_training_function_evaluations=(
            black_scholes_fit.function_evaluations
        ),
        heston_training_target_count=len(problem.training_observations),
        heston_training_start_count=len(training_starts),
        heston_training_function_evaluations=training_nfev,
        heston_training_jacobian_evaluations=training_njev,
        heston_full_sample_target_count=len(problem.observations),
        heston_full_sample_start_count=len(full_starts),
        heston_full_sample_function_evaluations=full_nfev,
        heston_full_sample_jacobian_evaluations=full_njev,
        heston_fourier_upper_bound=(
            problem.heston_forward_method.integration_upper_bound
        ),
        heston_fourier_intervals=problem.heston_forward_method.intervals,
    )


def _conclusion(
    *,
    bs_training: ValidationMetrics,
    bs_evaluation: ValidationMetrics,
    heston_training: ValidationMetrics,
    heston_evaluation: ValidationMetrics,
) -> BlackScholesHestonValidationConclusion:
    better_training = (
        heston_training.root_mean_square_error < bs_training.root_mean_square_error
    )
    better_evaluation = (
        heston_evaluation.root_mean_square_error < bs_evaluation.root_mean_square_error
    )
    better_standardized = (
        heston_evaluation.standardized_root_mean_square_error
        < bs_evaluation.standardized_root_mean_square_error
    )
    if better_evaluation and better_standardized:
        statement = (
            "Under this predeclared same-date cross-sectional holdout, explicit "
            "rate/carry convention, price-space objective, and selected observations, "
            "Heston improves held-out price and half-spread-standardized RMSE relative "
            "to the one-volatility Black-Scholes benchmark. This does not establish "
            "temporal generalization or model validity; calibration conditioning, "
            "limited date/maturity coverage, numerical cost, and unsupported Heston "
            "hedging remain material limitations."
        )
    else:
        statement = (
            "Under this predeclared same-date cross-sectional holdout, Heston does not "
            "improve both primary held-out RMSE criteria relative to the fitted "
            "one-volatility Black-Scholes benchmark. The evidence does not justify a "
            "general model-superiority claim."
        )
    return BlackScholesHestonValidationConclusion(
        heston_lower_training_price_rmse=better_training,
        heston_lower_evaluation_price_rmse=better_evaluation,
        heston_lower_evaluation_standardized_rmse=better_standardized,
        temporal_out_of_sample_tested=False,
        heston_hedge_comparison_supported=False,
        statement=statement,
    )
