"""Concrete Heston price-space calibration problem and completed evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from math import isfinite
from typing import Protocol, Self, cast

from qf_platform._validation import finite_real, nonnegative_finite_real
from qf_platform.market_data.normalization import NormalizedOptionObservation
from qf_platform.pricing.equity import EuropeanOption, OptionRight
from qf_platform.pricing.heston import HestonEquityState, HestonLaw, HestonParameters
from qf_platform.pricing.heston_fourier import HestonFourierEuropeanOption
from qf_platform.pricing.measures import PricingMeasureSemantics
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState
from qf_platform.pricing.valuation import evaluate

_HESTON_CALIBRATION_PARAMETER_COUNT = 5


class InvalidHestonCalibrationProblem(ValueError):
    """Raised when the financial Heston calibration question is not well formed."""


class InvalidHestonCalibrationInitialGuess(ValueError):
    """Raised when optimizer initialization is outside the financial domain."""


class HestonCalibrationConvergenceError(RuntimeError):
    """Raised when the configured numerical optimizer does not converge."""


class HestonCalibrationTargetSource(StrEnum):
    """Semantic origin of one price-space calibration target."""

    SYNTHETIC_MODEL = "synthetic_model"
    NORMALIZED_MARKET = "normalized_market"


class HestonCalibrationWeighting(StrEnum):
    """Price-residual scaling owned by the calibration problem."""

    UNIFORM_PRICE = "uniform_price"
    BID_ASK_HALF_SPREAD = "bid_ask_half_spread"


@dataclass(frozen=True, slots=True)
class HestonPriceCalibrationTarget:
    """One option-price target with explicit synthetic/observed provenance semantics."""

    contract: EuropeanOption
    target_price: float
    source: HestonCalibrationTargetSource
    observation: NormalizedOptionObservation | None = None
    label: str = ""

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.contract), EuropeanOption):
            msg = "contract must be a EuropeanOption"
            raise TypeError(msg)
        target_price = finite_real(self.target_price, name="target_price")
        if target_price < 0.0:
            msg = "target_price must be non-negative"
            raise ValueError(msg)
        object.__setattr__(self, "target_price", target_price)
        if not isinstance(cast(object, self.source), HestonCalibrationTargetSource):
            msg = "source must be a HestonCalibrationTargetSource"
            raise TypeError(msg)

        if self.source is HestonCalibrationTargetSource.SYNTHETIC_MODEL:
            if self.observation is not None:
                msg = "synthetic calibration targets must not carry market observations"
                raise ValueError(msg)
            return

        observation = self.observation
        if not isinstance(cast(object, observation), NormalizedOptionObservation):
            msg = "normalized-market target requires NormalizedOptionObservation"
            raise TypeError(msg)
        if observation.target_price != self.target_price:
            msg = "market target price must equal its normalized observed target"
            raise ValueError(msg)
        quote = observation.raw_quote
        if (
            quote.expiry != self.contract.expiry
            or quote.strike != self.contract.strike
            or quote.right is not self.contract.right
        ):
            msg = "market target contract must match its normalized observation"
            raise ValueError(msg)

    @classmethod
    def synthetic(
        cls,
        *,
        contract: EuropeanOption,
        target_price: float,
        label: str = "",
    ) -> Self:
        """Build a model-generated target without pretending it is observed data."""

        return cls(
            contract=contract,
            target_price=target_price,
            source=HestonCalibrationTargetSource.SYNTHETIC_MODEL,
            label=label,
        )

    @classmethod
    def from_normalized_observation(
        cls,
        observation: NormalizedOptionObservation,
        /,
        *,
        label: str = "",
    ) -> Self:
        """Build a market target while retaining the full M4 observation lineage."""

        quote = observation.raw_quote
        return cls(
            contract=EuropeanOption(
                expiry=quote.expiry,
                strike=quote.strike,
                right=quote.right,
            ),
            target_price=observation.target_price,
            source=HestonCalibrationTargetSource.NORMALIZED_MARKET,
            observation=observation,
            label=label or quote.contract_id,
        )


@dataclass(frozen=True, slots=True)
class HestonCalibrationCoordinates:
    """Financial coordinates varied by M6 without changing Heston model identity.

    Current variance remains separate from ``HestonParameters`` because M5 established
    it as current modeled state. The fixed carry input remains inside the immutable
    parameter value used by each forward pricing problem.
    """

    initial_variance: float
    parameters: HestonParameters

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "initial_variance",
            nonnegative_finite_real(
                self.initial_variance,
                name="initial_variance",
            ),
        )
        if not isinstance(cast(object, self.parameters), HestonParameters):
            msg = "parameters must be HestonParameters"
            raise TypeError(msg)

    def as_vector(self) -> tuple[float, float, float, float, float]:
        """Return direct financial optimizer coordinates in committed order."""

        return (
            self.initial_variance,
            self.parameters.mean_reversion_speed,
            self.parameters.long_run_variance,
            self.parameters.volatility_of_variance,
            self.parameters.correlation,
        )

    @classmethod
    def from_vector(
        cls,
        values: tuple[float, float, float, float, float],
        /,
        *,
        continuous_dividend_yield: float,
    ) -> Self:
        """Construct financial coordinates from the direct numerical vector."""

        return cls(
            initial_variance=values[0],
            parameters=HestonParameters(
                mean_reversion_speed=values[1],
                long_run_variance=values[2],
                volatility_of_variance=values[3],
                correlation=values[4],
                continuous_dividend_yield=continuous_dividend_yield,
            ),
        )


@dataclass(frozen=True, slots=True)
class HestonCalibrationBounds:
    """Named admissible financial domain for the five M6 calibration coordinates."""

    minimum_initial_variance: float = 1.0e-4
    maximum_initial_variance: float = 1.0
    minimum_mean_reversion_speed: float = 0.05
    maximum_mean_reversion_speed: float = 15.0
    minimum_long_run_variance: float = 1.0e-4
    maximum_long_run_variance: float = 1.0
    minimum_volatility_of_variance: float = 1.0e-4
    maximum_volatility_of_variance: float = 5.0
    minimum_correlation: float = -0.999
    maximum_correlation: float = 0.999

    def __post_init__(self) -> None:
        names = (
            "minimum_initial_variance",
            "maximum_initial_variance",
            "minimum_mean_reversion_speed",
            "maximum_mean_reversion_speed",
            "minimum_long_run_variance",
            "maximum_long_run_variance",
            "minimum_volatility_of_variance",
            "maximum_volatility_of_variance",
            "minimum_correlation",
            "maximum_correlation",
        )
        for name in names:
            object.__setattr__(self, name, finite_real(getattr(self, name), name=name))

        if self.minimum_initial_variance < 0.0:
            msg = "minimum_initial_variance must be non-negative"
            raise ValueError(msg)
        if self.minimum_mean_reversion_speed <= 0.0:
            msg = "minimum_mean_reversion_speed must be strictly positive"
            raise ValueError(msg)
        if self.minimum_long_run_variance < 0.0:
            msg = "minimum_long_run_variance must be non-negative"
            raise ValueError(msg)
        if self.minimum_volatility_of_variance < 0.0:
            msg = "minimum_volatility_of_variance must be non-negative"
            raise ValueError(msg)
        if self.minimum_correlation < -1.0 or self.maximum_correlation > 1.0:
            msg = "correlation calibration bounds must lie in [-1, 1]"
            raise ValueError(msg)

        pairs = (
            (self.minimum_initial_variance, self.maximum_initial_variance),
            (self.minimum_mean_reversion_speed, self.maximum_mean_reversion_speed),
            (self.minimum_long_run_variance, self.maximum_long_run_variance),
            (self.minimum_volatility_of_variance, self.maximum_volatility_of_variance),
            (self.minimum_correlation, self.maximum_correlation),
        )
        if any(lower >= upper for lower, upper in pairs):
            msg = "every Heston calibration lower bound must be below its upper bound"
            raise ValueError(msg)

    @property
    def lower_vector(self) -> tuple[float, float, float, float, float]:
        """Return lower financial-coordinate bounds in committed optimizer order."""

        return (
            self.minimum_initial_variance,
            self.minimum_mean_reversion_speed,
            self.minimum_long_run_variance,
            self.minimum_volatility_of_variance,
            self.minimum_correlation,
        )

    @property
    def upper_vector(self) -> tuple[float, float, float, float, float]:
        """Return upper financial-coordinate bounds in committed optimizer order."""

        return (
            self.maximum_initial_variance,
            self.maximum_mean_reversion_speed,
            self.maximum_long_run_variance,
            self.maximum_volatility_of_variance,
            self.maximum_correlation,
        )

    @property
    def widths(self) -> tuple[float, float, float, float, float]:
        """Return finite domain widths used only to scale identifiability evidence."""

        lower = self.lower_vector
        upper = self.upper_vector
        return (
            upper[0] - lower[0],
            upper[1] - lower[1],
            upper[2] - lower[2],
            upper[3] - lower[3],
            upper[4] - lower[4],
        )

    def contains(self, coordinates: HestonCalibrationCoordinates, /) -> bool:
        """Return whether financial coordinates lie inside this admissible domain."""

        return all(
            lower <= value <= upper
            for value, lower, upper in zip(
                coordinates.as_vector(),
                self.lower_vector,
                self.upper_vector,
                strict=True,
            )
        )


@dataclass(frozen=True, slots=True)
class HestonCalibrationProblem:
    """Financial statement of M6's concrete Heston price-space inverse problem."""

    valuation_date: date
    spot: float
    targets: tuple[HestonPriceCalibrationTarget, ...]
    numeraire: FlatMoneyMarketNumeraire
    pricing_measure: PricingMeasureSemantics[date]
    continuous_dividend_yield: float
    bounds: HestonCalibrationBounds
    weighting: HestonCalibrationWeighting = HestonCalibrationWeighting.UNIFORM_PRICE
    forward_method: HestonFourierEuropeanOption = field(
        default_factory=HestonFourierEuropeanOption
    )

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.valuation_date), date):
            msg = "valuation_date must be a date"
            raise TypeError(msg)
        spot = finite_real(self.spot, name="spot")
        if spot <= 0.0:
            msg = "calibration spot must be strictly positive"
            raise InvalidHestonCalibrationProblem(msg)
        object.__setattr__(self, "spot", spot)
        if type(self.targets) is not tuple or not self.targets:
            msg = "targets must be a non-empty tuple"
            raise InvalidHestonCalibrationProblem(msg)
        if not isinstance(cast(object, self.numeraire), FlatMoneyMarketNumeraire):
            msg = "numeraire must be FlatMoneyMarketNumeraire"
            raise TypeError(msg)
        if not isinstance(cast(object, self.pricing_measure), PricingMeasureSemantics):
            msg = "pricing_measure must be PricingMeasureSemantics"
            raise TypeError(msg)
        if self.pricing_measure.numeraire is not self.numeraire:
            msg = "pricing_measure must reference the calibration numeraire"
            raise InvalidHestonCalibrationProblem(msg)
        if not isinstance(cast(object, self.bounds), HestonCalibrationBounds):
            msg = "bounds must be HestonCalibrationBounds"
            raise TypeError(msg)
        if not isinstance(cast(object, self.weighting), HestonCalibrationWeighting):
            msg = "weighting must be HestonCalibrationWeighting"
            raise TypeError(msg)
        if not isinstance(cast(object, self.forward_method), HestonFourierEuropeanOption):
            msg = "forward_method must be HestonFourierEuropeanOption"
            raise TypeError(msg)
        object.__setattr__(
            self,
            "continuous_dividend_yield",
            finite_real(
                self.continuous_dividend_yield,
                name="continuous_dividend_yield",
            ),
        )
        self._validate_targets()

    def _validate_targets(self) -> None:
        contract_keys: set[tuple[date, float, OptionRight]] = set()
        market_underlyings: set[str] = set()
        for target in self.targets:
            if not isinstance(cast(object, target), HestonPriceCalibrationTarget):
                msg = "every target must be HestonPriceCalibrationTarget"
                raise TypeError(msg)
            contract = target.contract
            if contract.expiry <= self.valuation_date:
                msg = "Heston calibration targets require positive time to expiry"
                raise InvalidHestonCalibrationProblem(msg)
            if contract.strike <= 0.0:
                msg = "Heston calibration targets require positive strikes"
                raise InvalidHestonCalibrationProblem(msg)
            key = (contract.expiry, contract.strike, contract.right)
            if key in contract_keys:
                msg = "duplicate option contracts are not supported in one calibration"
                raise InvalidHestonCalibrationProblem(msg)
            contract_keys.add(key)

            observation = target.observation
            if observation is not None:
                if observation.valuation_date != self.valuation_date:
                    msg = "market calibration targets must share one valuation date"
                    raise InvalidHestonCalibrationProblem(msg)
                if observation.spot != self.spot:
                    msg = "market calibration targets must share the calibration spot"
                    raise InvalidHestonCalibrationProblem(msg)
                market_underlyings.add(observation.raw_underlying.underlying_id)

            if self.weighting is HestonCalibrationWeighting.BID_ASK_HALF_SPREAD:
                self._validate_bid_ask_scale(target)

        if len(market_underlyings) > 1:
            msg = "market calibration targets must reference one underlying"
            raise InvalidHestonCalibrationProblem(msg)

    @staticmethod
    def _validate_bid_ask_scale(target: HestonPriceCalibrationTarget) -> None:
        observation = target.observation
        if observation is None:
            msg = "bid/ask weighting requires normalized market targets"
            raise InvalidHestonCalibrationProblem(msg)
        bid = observation.raw_quote.bid
        ask = observation.raw_quote.ask
        if bid is None or ask is None or ask <= bid:
            msg = "bid/ask weighting requires a strictly positive observed spread"
            raise InvalidHestonCalibrationProblem(msg)

    def residual_scale(self, target: HestonPriceCalibrationTarget, /) -> float:
        """Return the explicit price scale defining this target's objective weight."""

        if self.weighting is HestonCalibrationWeighting.UNIFORM_PRICE:
            return 1.0
        observation = target.observation
        if observation is None:
            msg = "bid/ask weighting requires normalized market targets"
            raise InvalidHestonCalibrationProblem(msg)
        bid = observation.raw_quote.bid
        ask = observation.raw_quote.ask
        if bid is None or ask is None:
            msg = "bid/ask weighting requires bid and ask"
            raise InvalidHestonCalibrationProblem(msg)
        return 0.5 * (ask - bid)


@dataclass(frozen=True, slots=True)
class HestonCalibrationResidual:
    """One target's model mismatch under completed calibration coordinates."""

    target: HestonPriceCalibrationTarget
    model_price: float
    residual: float
    residual_scale: float
    standardized_residual: float

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.target), HestonPriceCalibrationTarget):
            msg = "target must be HestonPriceCalibrationTarget"
            raise TypeError(msg)
        for name in ("model_price", "residual", "residual_scale", "standardized_residual"):
            object.__setattr__(self, name, finite_real(getattr(self, name), name=name))
        if self.residual_scale <= 0.0:
            msg = "residual_scale must be strictly positive"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class HestonCalibrationConditioning:
    """Local identifiability evidence from the domain-scaled residual Jacobian."""

    singular_values: tuple[float, ...]
    jacobian_rank: int
    parameter_count: int
    target_count: int
    condition_number: float | None

    def __post_init__(self) -> None:
        if type(self.singular_values) is not tuple:
            msg = "singular_values must be a tuple"
            raise TypeError(msg)
        for value in self.singular_values:
            if not isfinite(value) or value < 0.0:
                msg = "singular_values must be non-negative and finite"
                raise ValueError(msg)
        for name in ("jacobian_rank", "parameter_count", "target_count"):
            value = getattr(self, name)
            if type(value) is not int:
                msg = f"{name} must be an integer"
                raise TypeError(msg)
            if value < 0:
                msg = f"{name} must be non-negative"
                raise ValueError(msg)
        if self.parameter_count != _HESTON_CALIBRATION_PARAMETER_COUNT:
            msg = "M6 conditioning parameter_count must be five"
            raise ValueError(msg)
        if self.jacobian_rank > min(self.target_count, self.parameter_count):
            msg = "jacobian_rank exceeds the Jacobian dimensions"
            raise ValueError(msg)
        if self.condition_number is not None:
            condition_number = finite_real(
                self.condition_number,
                name="condition_number",
            )
            if condition_number < 1.0:
                msg = "condition_number must be at least one"
                raise ValueError(msg)
            object.__setattr__(self, "condition_number", condition_number)

    @property
    def rank_deficient(self) -> bool:
        """Return whether local first-order identification is rank deficient."""

        return self.jacobian_rank < self.parameter_count


@dataclass(frozen=True, slots=True)
class HestonCalibrationResult:
    """Immutable successful Heston calibration output and local numerical evidence."""

    estimate: HestonCalibrationCoordinates
    objective_value: float
    residuals: tuple[HestonCalibrationResidual, ...]
    function_evaluations: int
    jacobian_evaluations: int
    termination_status: int
    termination_message: str
    conditioning: HestonCalibrationConditioning
    optimizer_name: str = "scipy.optimize.least_squares:trf"

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.estimate), HestonCalibrationCoordinates):
            msg = "estimate must be HestonCalibrationCoordinates"
            raise TypeError(msg)
        objective = finite_real(self.objective_value, name="objective_value")
        if objective < 0.0:
            msg = "objective_value must be non-negative"
            raise ValueError(msg)
        object.__setattr__(self, "objective_value", objective)
        if type(self.residuals) is not tuple or not self.residuals:
            msg = "residuals must be a non-empty tuple"
            raise ValueError(msg)
        for name in ("function_evaluations", "jacobian_evaluations"):
            value = getattr(self, name)
            if type(value) is not int:
                msg = f"{name} must be an integer"
                raise TypeError(msg)
            if value < 0:
                msg = f"{name} must be non-negative"
                raise ValueError(msg)
        if type(self.termination_status) is not int or self.termination_status <= 0:
            msg = "successful calibration termination_status must be positive"
            raise ValueError(msg)
        if not self.termination_message.strip():
            msg = "termination_message must be non-empty"
            raise ValueError(msg)
        if not isinstance(cast(object, self.conditioning), HestonCalibrationConditioning):
            msg = "conditioning must be HestonCalibrationConditioning"
            raise TypeError(msg)
        if not self.optimizer_name.strip():
            msg = "optimizer_name must be non-empty"
            raise ValueError(msg)

    @property
    def max_absolute_standardized_residual(self) -> float:
        """Return the largest absolute residual after problem-owned scaling."""

        return max(abs(item.standardized_residual) for item in self.residuals)


class HestonCalibrationMethod(Protocol):
    """Numerical-method responsibility for M6's concrete calibration problem."""

    def solve(
        self,
        problem: HestonCalibrationProblem,
        /,
    ) -> HestonCalibrationResult:
        """Solve one already-formed Heston calibration problem."""
        ...


def heston_calibration_model_price(
    problem: HestonCalibrationProblem,
    coordinates: HestonCalibrationCoordinates,
    target: HestonPriceCalibrationTarget,
    /,
) -> float:
    """Evaluate M6's configured M5 forward map at one financial coordinate set."""

    if coordinates.parameters.continuous_dividend_yield != problem.continuous_dividend_yield:
        msg = "calibration coordinates must use the problem's fixed dividend yield"
        raise InvalidHestonCalibrationProblem(msg)
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
        contract=target.contract,
        numeraire=problem.numeraire,
        pricing_measure=problem.pricing_measure,
    )
    return evaluate(pricing_problem, problem.forward_method).present_value


def evaluate_heston_calibration_residuals(
    problem: HestonCalibrationProblem,
    coordinates: HestonCalibrationCoordinates,
    /,
) -> tuple[HestonCalibrationResidual, ...]:
    """Evaluate raw and standardized price residuals without running an optimizer."""

    residuals: list[HestonCalibrationResidual] = []
    for target in problem.targets:
        model_price = heston_calibration_model_price(problem, coordinates, target)
        residual = model_price - target.target_price
        scale = problem.residual_scale(target)
        residuals.append(
            HestonCalibrationResidual(
                target=target,
                model_price=model_price,
                residual=residual,
                residual_scale=scale,
                standardized_residual=residual / scale,
            )
        )
    return tuple(residuals)


def calibrate_heston(
    problem: HestonCalibrationProblem,
    method: HestonCalibrationMethod,
    /,
) -> HestonCalibrationResult:
    """Evaluate one Heston calibration Problem + supported Method."""

    return method.solve(problem)
