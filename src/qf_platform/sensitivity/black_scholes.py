"""Concrete Black-Scholes sensitivity problems, methods, and results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from math import erfc, exp, log, pi, sqrt
from typing import Protocol, cast

from qf_platform._validation import finite_real
from qf_platform.pricing.black_scholes import (
    BlackScholesLaw,
    BlackScholesParameters,
)
from qf_platform.pricing.black_scholes_valuation import BlackScholesClosedForm
from qf_platform.pricing.dates import actual_365_fixed_year_fraction
from qf_platform.pricing.equity import (
    EquityState,
    EquityStateSpace,
    EuropeanOption,
    OptionRight,
)
from qf_platform.pricing.measures import PricingMeasureSemantics
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState
from qf_platform.pricing.valuation import evaluate

_SQRT_TWO = sqrt(2.0)


class BlackScholesVariable(StrEnum):
    """Concrete differentiation variables used by M2 sensitivities."""

    SPOT = "spot"
    ANNUALIZED_VOLATILITY = "annualized_volatility"
    VALUATION_TIME = "valuation_time"
    MONEY_MARKET_RATE = "money_market_rate"


class BlackScholesSensitivity(StrEnum):
    """Supported M2 Black-Scholes sensitivities."""

    DELTA = "delta"
    GAMMA = "gamma"
    VEGA = "vega"
    THETA = "theta"
    RHO = "rho"

    @property
    def variable(self) -> BlackScholesVariable:
        if self in (BlackScholesSensitivity.DELTA, BlackScholesSensitivity.GAMMA):
            return BlackScholesVariable.SPOT
        if self is BlackScholesSensitivity.VEGA:
            return BlackScholesVariable.ANNUALIZED_VOLATILITY
        if self is BlackScholesSensitivity.THETA:
            return BlackScholesVariable.VALUATION_TIME
        return BlackScholesVariable.MONEY_MARKET_RATE

    @property
    def derivative_order(self) -> int:
        if self is BlackScholesSensitivity.GAMMA:
            return 2
        return 1

    @property
    def units(self) -> str:
        if self is BlackScholesSensitivity.DELTA:
            return "present-value units per spot unit"
        if self is BlackScholesSensitivity.GAMMA:
            return "present-value units per spot unit squared"
        if self is BlackScholesSensitivity.VEGA:
            return "present-value units per 1.00 annualized volatility decimal"
        if self is BlackScholesSensitivity.THETA:
            return "present-value units per ACT/365F model year of valuation time"
        return "present-value units per 1.00 continuously compounded rate decimal"


@dataclass(frozen=True, slots=True)
class BlackScholesSensitivityProblem:
    """One requested local sensitivity of a concrete M1 pricing problem."""

    pricing_problem: PricingProblem[date, EquityState, BlackScholesParameters]
    sensitivity: BlackScholesSensitivity

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.sensitivity), BlackScholesSensitivity):
            msg = "sensitivity must be a BlackScholesSensitivity"
            raise TypeError(msg)
        if not _is_m1_black_scholes_problem(self.pricing_problem):
            msg = "sensitivity problem requires the concrete M1 Black-Scholes family"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class BlackScholesSensitivityResult:
    """Immutable completed value for one explicitly identified sensitivity."""

    sensitivity: BlackScholesSensitivity
    value: float

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.sensitivity), BlackScholesSensitivity):
            msg = "sensitivity must be a BlackScholesSensitivity"
            raise TypeError(msg)
        object.__setattr__(
            self, "value", finite_real(self.value, name="sensitivity value")
        )

    @property
    def variable(self) -> BlackScholesVariable:
        return self.sensitivity.variable

    @property
    def derivative_order(self) -> int:
        return self.sensitivity.derivative_order

    @property
    def units(self) -> str:
        return self.sensitivity.units


class UnsupportedSensitivityProblem(ValueError):
    """Raised when a sensitivity method cannot evaluate a requested problem."""


class BlackScholesSensitivityMethod(Protocol):
    """Method responsibility for the narrow M2 Black-Scholes sensitivity family."""

    def supports(self, problem: BlackScholesSensitivityProblem, /) -> bool:
        """Return whether the method supports this concrete sensitivity problem."""
        ...

    def apply(
        self,
        problem: BlackScholesSensitivityProblem,
        /,
    ) -> BlackScholesSensitivityResult:
        """Evaluate one supported sensitivity problem."""
        ...


def evaluate_sensitivity(
    problem: BlackScholesSensitivityProblem,
    method: BlackScholesSensitivityMethod,
    /,
) -> BlackScholesSensitivityResult:
    """Evaluate only after explicit sensitivity-method capability checking."""

    if not method.supports(problem):
        method_name = type(method).__name__
        msg = f"{method_name} does not support the supplied sensitivity problem"
        raise UnsupportedSensitivityProblem(msg)
    return method.apply(problem)


def _is_m1_black_scholes_problem(
    problem: PricingProblem[date, EquityState, BlackScholesParameters],
) -> bool:
    return (
        isinstance(problem.current_state.state_space, EquityStateSpace)
        and isinstance(problem.stochastic_law, BlackScholesLaw)
        and isinstance(problem.contract, EuropeanOption)
        and isinstance(problem.numeraire, FlatMoneyMarketNumeraire)
    )


def _is_differentiable_interior(problem: BlackScholesSensitivityProblem) -> bool:
    pricing_problem = problem.pricing_problem
    contract = cast(EuropeanOption, pricing_problem.contract)
    return (
        contract.expiry > pricing_problem.valuation_time
        and pricing_problem.current_state.value.spot > 0.0
        and contract.strike > 0.0
        and pricing_problem.parameters.annualized_volatility > 0.0
    )


def _standard_normal_cdf(value: float) -> float:
    return 0.5 * erfc(-value / _SQRT_TWO)


def _standard_normal_density(value: float) -> float:
    return exp(-0.5 * value * value) / sqrt(2.0 * pi)


@dataclass(frozen=True, slots=True)
class _BlackScholesTerms:
    right: OptionRight
    spot: float
    strike: float
    rate: float
    dividend_yield: float
    volatility: float
    year_fraction: float
    sqrt_year_fraction: float
    d1: float
    d2: float
    spot_discount: float
    strike_discount: float
    density_d1: float


def _terms(problem: BlackScholesSensitivityProblem) -> _BlackScholesTerms:
    pricing_problem = problem.pricing_problem
    contract = cast(EuropeanOption, pricing_problem.contract)
    numeraire = cast(FlatMoneyMarketNumeraire, pricing_problem.numeraire)
    spot = pricing_problem.current_state.value.spot
    strike = contract.strike
    volatility = pricing_problem.parameters.annualized_volatility
    dividend_yield = pricing_problem.parameters.continuous_dividend_yield
    rate = numeraire.continuously_compounded_rate
    year_fraction = actual_365_fixed_year_fraction(
        pricing_problem.valuation_time,
        contract.expiry,
    )
    sqrt_year_fraction = sqrt(year_fraction)
    sigma_sqrt_t = volatility * sqrt_year_fraction
    d1 = (
        log(spot / strike)
        + (rate - dividend_yield + 0.5 * volatility * volatility) * year_fraction
    ) / sigma_sqrt_t
    d2 = d1 - sigma_sqrt_t
    return _BlackScholesTerms(
        right=contract.right,
        spot=spot,
        strike=strike,
        rate=rate,
        dividend_yield=dividend_yield,
        volatility=volatility,
        year_fraction=year_fraction,
        sqrt_year_fraction=sqrt_year_fraction,
        d1=d1,
        d2=d2,
        spot_discount=exp(-dividend_yield * year_fraction),
        strike_discount=exp(-rate * year_fraction),
        density_d1=_standard_normal_density(d1),
    )


@dataclass(frozen=True, slots=True)
class AnalyticBlackScholesSensitivity:
    """Closed-form Black-Scholes Delta/Gamma/Vega/Theta/Rho method."""

    def supports(self, problem: BlackScholesSensitivityProblem, /) -> bool:
        return _is_differentiable_interior(problem)

    def apply(
        self,
        problem: BlackScholesSensitivityProblem,
        /,
    ) -> BlackScholesSensitivityResult:
        if not self.supports(problem):
            msg = "analytic Black-Scholes sensitivity requires an interior problem"
            raise UnsupportedSensitivityProblem(msg)

        terms = _terms(problem)
        sensitivity = problem.sensitivity
        if sensitivity is BlackScholesSensitivity.DELTA:
            value = _analytic_delta(terms)
        elif sensitivity is BlackScholesSensitivity.GAMMA:
            value = _analytic_gamma(terms)
        elif sensitivity is BlackScholesSensitivity.VEGA:
            value = _analytic_vega(terms)
        elif sensitivity is BlackScholesSensitivity.THETA:
            value = _analytic_theta(terms)
        else:
            value = _analytic_rho(terms)
        return BlackScholesSensitivityResult(sensitivity=sensitivity, value=value)


def _analytic_delta(terms: _BlackScholesTerms) -> float:
    if terms.right is OptionRight.CALL:
        return terms.spot_discount * _standard_normal_cdf(terms.d1)
    return terms.spot_discount * (_standard_normal_cdf(terms.d1) - 1.0)


def _analytic_gamma(terms: _BlackScholesTerms) -> float:
    return (
        terms.spot_discount
        * terms.density_d1
        / (terms.spot * terms.volatility * terms.sqrt_year_fraction)
    )


def _analytic_vega(terms: _BlackScholesTerms) -> float:
    return (
        terms.spot * terms.spot_discount * terms.density_d1 * terms.sqrt_year_fraction
    )


def _analytic_theta(terms: _BlackScholesTerms) -> float:
    diffusion_decay = -(
        terms.spot
        * terms.spot_discount
        * terms.density_d1
        * terms.volatility
        / (2.0 * terms.sqrt_year_fraction)
    )
    if terms.right is OptionRight.CALL:
        financing = -(
            terms.rate
            * terms.strike
            * terms.strike_discount
            * _standard_normal_cdf(terms.d2)
        )
        carry = (
            terms.dividend_yield
            * terms.spot
            * terms.spot_discount
            * _standard_normal_cdf(terms.d1)
        )
        return diffusion_decay + financing + carry

    financing = (
        terms.rate
        * terms.strike
        * terms.strike_discount
        * _standard_normal_cdf(-terms.d2)
    )
    carry = -(
        terms.dividend_yield
        * terms.spot
        * terms.spot_discount
        * _standard_normal_cdf(-terms.d1)
    )
    return diffusion_decay + financing + carry


def _analytic_rho(terms: _BlackScholesTerms) -> float:
    scale = terms.strike * terms.year_fraction * terms.strike_discount
    if terms.right is OptionRight.CALL:
        return scale * _standard_normal_cdf(terms.d2)
    return -scale * _standard_normal_cdf(-terms.d2)


@dataclass(frozen=True, slots=True)
class FiniteDifferenceBlackScholesSensitivity:
    """Central bump-and-revalue sensitivity method with explicit native-unit bumps."""

    spot_bump: float = 0.1
    volatility_bump: float = 0.001
    rate_bump: float = 0.0001
    theta_day_bump: int = 1

    def __post_init__(self) -> None:
        for name in ("spot_bump", "volatility_bump", "rate_bump"):
            value = finite_real(getattr(self, name), name=name)
            if value <= 0.0:
                msg = f"{name} must be positive"
                raise ValueError(msg)
            object.__setattr__(self, name, value)
        if type(self.theta_day_bump) is not int:
            msg = "theta_day_bump must be an integer"
            raise TypeError(msg)
        if self.theta_day_bump <= 0:
            msg = "theta_day_bump must be positive"
            raise ValueError(msg)

    def supports(self, problem: BlackScholesSensitivityProblem, /) -> bool:
        if not _is_differentiable_interior(problem):
            return False
        pricing_problem = problem.pricing_problem
        if problem.sensitivity in (
            BlackScholesSensitivity.DELTA,
            BlackScholesSensitivity.GAMMA,
        ):
            return pricing_problem.current_state.value.spot > self.spot_bump
        if problem.sensitivity is BlackScholesSensitivity.VEGA:
            return (
                pricing_problem.parameters.annualized_volatility > self.volatility_bump
            )
        if problem.sensitivity is BlackScholesSensitivity.THETA:
            contract = cast(EuropeanOption, pricing_problem.contract)
            later = pricing_problem.valuation_time + timedelta(days=self.theta_day_bump)
            return later < contract.expiry
        return True

    def apply(
        self,
        problem: BlackScholesSensitivityProblem,
        /,
    ) -> BlackScholesSensitivityResult:
        if not self.supports(problem):
            msg = "finite-difference method cannot apply the configured bump"
            raise UnsupportedSensitivityProblem(msg)

        sensitivity = problem.sensitivity
        if sensitivity is BlackScholesSensitivity.DELTA:
            value = self._spot_first_derivative(problem)
        elif sensitivity is BlackScholesSensitivity.GAMMA:
            value = self._spot_second_derivative(problem)
        elif sensitivity is BlackScholesSensitivity.VEGA:
            value = self._volatility_derivative(problem)
        elif sensitivity is BlackScholesSensitivity.THETA:
            value = self._time_derivative(problem)
        else:
            value = self._rate_derivative(problem)
        return BlackScholesSensitivityResult(sensitivity=sensitivity, value=value)

    def _spot_first_derivative(self, problem: BlackScholesSensitivityProblem) -> float:
        pricing_problem = problem.pricing_problem
        center = pricing_problem.current_state.value.spot
        upper = _with_spot(pricing_problem, center + self.spot_bump)
        lower = _with_spot(pricing_problem, center - self.spot_bump)
        return (_price(upper) - _price(lower)) / (2.0 * self.spot_bump)

    def _spot_second_derivative(self, problem: BlackScholesSensitivityProblem) -> float:
        pricing_problem = problem.pricing_problem
        center = pricing_problem.current_state.value.spot
        upper = _with_spot(pricing_problem, center + self.spot_bump)
        lower = _with_spot(pricing_problem, center - self.spot_bump)
        center_value = _price(pricing_problem)
        return (_price(upper) - 2.0 * center_value + _price(lower)) / (
            self.spot_bump * self.spot_bump
        )

    def _volatility_derivative(self, problem: BlackScholesSensitivityProblem) -> float:
        pricing_problem = problem.pricing_problem
        center = pricing_problem.parameters.annualized_volatility
        upper = _with_volatility(pricing_problem, center + self.volatility_bump)
        lower = _with_volatility(pricing_problem, center - self.volatility_bump)
        return (_price(upper) - _price(lower)) / (2.0 * self.volatility_bump)

    def _rate_derivative(self, problem: BlackScholesSensitivityProblem) -> float:
        pricing_problem = problem.pricing_problem
        numeraire = cast(FlatMoneyMarketNumeraire, pricing_problem.numeraire)
        center = numeraire.continuously_compounded_rate
        upper = _with_rate(pricing_problem, center + self.rate_bump)
        lower = _with_rate(pricing_problem, center - self.rate_bump)
        return (_price(upper) - _price(lower)) / (2.0 * self.rate_bump)

    def _time_derivative(self, problem: BlackScholesSensitivityProblem) -> float:
        pricing_problem = problem.pricing_problem
        day_bump = timedelta(days=self.theta_day_bump)
        earlier = _with_valuation_date(
            pricing_problem,
            pricing_problem.valuation_time - day_bump,
        )
        later = _with_valuation_date(
            pricing_problem,
            pricing_problem.valuation_time + day_bump,
        )
        year_displacement = actual_365_fixed_year_fraction(
            earlier.valuation_time,
            later.valuation_time,
        )
        return (_price(later) - _price(earlier)) / year_displacement


def _price(problem: PricingProblem[date, EquityState, BlackScholesParameters]) -> float:
    return evaluate(problem, BlackScholesClosedForm()).present_value


def _with_spot(
    problem: PricingProblem[date, EquityState, BlackScholesParameters],
    spot: float,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    current_state = ModeledState(
        time=problem.valuation_time,
        value=EquityState(spot),
        state_space=problem.current_state.state_space,
    )
    return _recompose(problem, current_state=current_state)


def _with_volatility(
    problem: PricingProblem[date, EquityState, BlackScholesParameters],
    volatility: float,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    parameters = BlackScholesParameters(
        annualized_volatility=volatility,
        continuous_dividend_yield=problem.parameters.continuous_dividend_yield,
    )
    return _recompose(problem, parameters=parameters)


def _with_rate(
    problem: PricingProblem[date, EquityState, BlackScholesParameters],
    rate: float,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    old_numeraire = cast(FlatMoneyMarketNumeraire, problem.numeraire)
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=old_numeraire.reference_date,
        continuously_compounded_rate=rate,
    )
    pricing_measure = PricingMeasureSemantics(
        name=problem.pricing_measure.name,
        numeraire=numeraire,
    )
    return _recompose(
        problem,
        numeraire=numeraire,
        pricing_measure=pricing_measure,
    )


def _with_valuation_date(
    problem: PricingProblem[date, EquityState, BlackScholesParameters],
    valuation_date: date,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    current_state = ModeledState(
        time=valuation_date,
        value=problem.current_state.value,
        state_space=problem.current_state.state_space,
    )
    return _recompose(problem, current_state=current_state)


def _recompose(
    problem: PricingProblem[date, EquityState, BlackScholesParameters],
    *,
    current_state: ModeledState[date, EquityState] | None = None,
    parameters: BlackScholesParameters | None = None,
    numeraire: FlatMoneyMarketNumeraire | None = None,
    pricing_measure: PricingMeasureSemantics[date] | None = None,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    selected_state = (
        current_state if current_state is not None else problem.current_state
    )
    selected_parameters = parameters if parameters is not None else problem.parameters
    selected_numeraire = numeraire if numeraire is not None else problem.numeraire
    selected_measure = (
        pricing_measure if pricing_measure is not None else problem.pricing_measure
    )
    return PricingProblem(
        current_state=selected_state,
        stochastic_law=problem.stochastic_law,
        parameters=selected_parameters,
        contract=problem.contract,
        numeraire=selected_numeraire,
        pricing_measure=selected_measure,
    )
