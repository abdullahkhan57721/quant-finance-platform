"""Characteristic-function/Fourier valuation for Heston European options."""

from __future__ import annotations

import cmath
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from math import exp, isfinite, log, pi, sqrt
from typing import cast

from qf_platform._validation import finite_real
from qf_platform.pricing.black_scholes import BlackScholesLaw, BlackScholesParameters
from qf_platform.pricing.black_scholes_valuation import BlackScholesClosedForm
from qf_platform.pricing.dates import actual_365_fixed_year_fraction
from qf_platform.pricing.equity import EquityState, EuropeanOption, OptionRight
from qf_platform.pricing.heston import (
    HestonEquityState,
    HestonLaw,
    HestonParameters,
    HestonStateSpace,
    integrated_deterministic_heston_variance,
)
from qf_platform.pricing.measures import validated_numeraire_value
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState
from qf_platform.pricing.valuation import (
    UnsupportedPricingProblem,
    ValuationResult,
    evaluate,
)


def _finite_complex(value: complex, *, name: str) -> complex:
    if not isfinite(value.real) or not isfinite(value.imag):
        msg = f"{name} must be finite"
        raise ValueError(msg)
    return value


def _positive_finite_exp(exponent: float, *, name: str) -> float:
    try:
        value = exp(exponent)
    except OverflowError as exc:
        msg = f"{name} must be positive and finite"
        raise ValueError(msg) from exc
    if not isfinite(value) or value <= 0.0:
        msg = f"{name} must be positive and finite"
        raise ValueError(msg)
    return value


def _simpson_integral(
    integrand: Callable[[float], float],
    *,
    lower: float,
    upper: float,
    intervals: int,
) -> float:
    width = (upper - lower) / intervals
    total = integrand(lower) + integrand(upper)
    for index in range(1, intervals):
        weight = 4.0 if index % 2 else 2.0
        total += weight * integrand(lower + index * width)
    value = width * total / 3.0
    if not isfinite(value):
        msg = "Heston Fourier integral must be finite"
        raise ValueError(msg)
    return value


def heston_characteristic_function(
    argument: complex,
    *,
    log_spot: float,
    year_fraction: float,
    rate: float,
    parameters: HestonParameters,
    initial_variance: float,
) -> complex:
    """Return the Heston characteristic function of terminal log spot.

    This is the shared numerical kernel used by the scalar M5 Fourier reference and the
    measured M8 maturity-batched pricing path. It intentionally accepts only numerical
    Heston inputs; it is not a financial-model or backend abstraction.

    The implementation uses the stable ``g`` representation and chooses the complex
    square-root branch so the real part of ``d`` is non-negative. The exact ``xi=0``
    boundary is handled outside this function through the deterministic-variance limit.
    """

    xi = parameters.volatility_of_variance
    if xi <= 0.0:
        msg = "Heston characteristic function requires positive volatility_of_variance"
        raise ValueError(msg)

    kappa = parameters.mean_reversion_speed
    theta = parameters.long_run_variance
    rho = parameters.correlation
    q = parameters.continuous_dividend_yield
    imaginary_argument = 1j * argument
    beta = kappa - rho * xi * imaginary_argument
    discriminant = beta * beta + xi * xi * (imaginary_argument + argument * argument)
    root = cmath.sqrt(discriminant)
    if root.real < 0.0 or (root.real == 0.0 and root.imag < 0.0):
        root = -root

    denominator = beta + root
    if abs(denominator) == 0.0:
        msg = "Heston characteristic-function branch denominator is singular"
        raise ValueError(msg)
    g = (beta - root) / denominator
    exp_minus_root_t = cmath.exp(-root * year_fraction)
    one_minus_g = 1.0 - g
    one_minus_g_exp = 1.0 - g * exp_minus_root_t
    if abs(one_minus_g) == 0.0 or abs(one_minus_g_exp) == 0.0:
        msg = "Heston characteristic-function logarithm denominator is singular"
        raise ValueError(msg)

    xi_squared = xi * xi
    c_term = imaginary_argument * (log_spot + (rate - q) * year_fraction) + (
        kappa * theta / xi_squared
    ) * ((beta - root) * year_fraction - 2.0 * cmath.log(one_minus_g_exp / one_minus_g))
    d_term = ((beta - root) / xi_squared) * ((1.0 - exp_minus_root_t) / one_minus_g_exp)
    try:
        value = cmath.exp(c_term + d_term * initial_variance)
    except OverflowError as exc:
        msg = "Heston characteristic function must be finite"
        raise ValueError(msg) from exc
    return _finite_complex(value, name="Heston characteristic function")


def _deterministic_variance_limit_value(
    problem: PricingProblem[date, HestonEquityState, HestonParameters],
    contract: EuropeanOption,
    year_fraction: float,
) -> float:
    integrated_variance = integrated_deterministic_heston_variance(
        problem.current_state.value.instantaneous_variance,
        problem.parameters,
        year_fraction,
    )
    effective_volatility = sqrt(integrated_variance / year_fraction)
    law = BlackScholesLaw()
    black_scholes_problem = PricingProblem(
        current_state=ModeledState(
            time=problem.valuation_time,
            value=EquityState(problem.current_state.value.spot),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=BlackScholesParameters(
            annualized_volatility=effective_volatility,
            continuous_dividend_yield=problem.parameters.continuous_dividend_yield,
        ),
        contract=contract,
        numeraire=problem.numeraire,
        pricing_measure=problem.pricing_measure,
    )
    return evaluate(black_scholes_problem, BlackScholesClosedForm()).present_value


@dataclass(frozen=True, slots=True)
class HestonFourierValuationResult(ValuationResult):
    """Heston Fourier value with explicit quadrature evidence."""

    integration_lower_bound: float
    integration_upper_bound: float
    intervals: int
    characteristic_function_evaluations: int

    def __post_init__(self) -> None:
        ValuationResult.__post_init__(self)
        lower = finite_real(
            self.integration_lower_bound,
            name="integration_lower_bound",
        )
        upper = finite_real(
            self.integration_upper_bound,
            name="integration_upper_bound",
        )
        if lower <= 0.0:
            msg = "integration_lower_bound must be strictly positive"
            raise ValueError(msg)
        if upper <= lower:
            msg = "integration_upper_bound must exceed integration_lower_bound"
            raise ValueError(msg)
        object.__setattr__(self, "integration_lower_bound", lower)
        object.__setattr__(self, "integration_upper_bound", upper)
        if type(self.intervals) is not int:
            msg = "intervals must be an integer"
            raise TypeError(msg)
        if self.intervals < 2 or self.intervals % 2:
            msg = "intervals must be an even integer of at least 2"
            raise ValueError(msg)
        if type(self.characteristic_function_evaluations) is not int:
            msg = "characteristic_function_evaluations must be an integer"
            raise TypeError(msg)
        if self.characteristic_function_evaluations < 0:
            msg = "characteristic_function_evaluations must be non-negative"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class HestonFourierEuropeanOption:
    """Configured characteristic-function valuation for Heston European options.

    The standard Heston risk-neutral probabilities ``P1`` and ``P2`` are evaluated by
    composite Simpson quadrature on an explicit finite positive frequency interval.
    Truncation and quadrature resolution therefore belong to this valuation method,
    not to the Heston stochastic law.
    """

    integration_upper_bound: float = 100.0
    intervals: int = 2048
    integration_lower_bound: float = 1.0e-8

    def __post_init__(self) -> None:
        lower = finite_real(
            self.integration_lower_bound,
            name="integration_lower_bound",
        )
        upper = finite_real(
            self.integration_upper_bound,
            name="integration_upper_bound",
        )
        if lower <= 0.0:
            msg = "integration_lower_bound must be strictly positive"
            raise ValueError(msg)
        if upper <= lower:
            msg = "integration_upper_bound must exceed integration_lower_bound"
            raise ValueError(msg)
        if type(self.intervals) is not int:
            msg = "intervals must be an integer"
            raise TypeError(msg)
        if self.intervals < 2 or self.intervals % 2:
            msg = "intervals must be an even integer of at least 2"
            raise ValueError(msg)
        object.__setattr__(self, "integration_lower_bound", lower)
        object.__setattr__(self, "integration_upper_bound", upper)

    def supports(
        self,
        problem: PricingProblem[date, HestonEquityState, HestonParameters],
        /,
    ) -> bool:
        contract = problem.contract
        return (
            isinstance(problem.current_state.state_space, HestonStateSpace)
            and isinstance(problem.stochastic_law, HestonLaw)
            and isinstance(contract, EuropeanOption)
            and isinstance(problem.numeraire, FlatMoneyMarketNumeraire)
            and contract.expiry >= problem.valuation_time
        )

    def apply(
        self,
        problem: PricingProblem[date, HestonEquityState, HestonParameters],
        /,
    ) -> HestonFourierValuationResult:
        if not self.supports(problem):
            msg = (
                "HestonFourierEuropeanOption does not support the supplied pricing "
                "problem"
            )
            raise UnsupportedPricingProblem(msg)

        contract = cast(EuropeanOption, problem.contract)
        year_fraction = actual_365_fixed_year_fraction(
            problem.valuation_time,
            contract.expiry,
        )
        spot = problem.current_state.value.spot
        strike = contract.strike
        numeraire_now = validated_numeraire_value(
            problem.numeraire,
            problem.valuation_time,
        )
        numeraire_expiry = validated_numeraire_value(problem.numeraire, contract.expiry)
        risk_free_discount = numeraire_now / numeraire_expiry
        if not isfinite(risk_free_discount) or risk_free_discount <= 0.0:
            msg = "risk-free discount factor must be positive and finite"
            raise ValueError(msg)

        if year_fraction == 0.0:
            signed = spot - strike
            payoff = (
                max(signed, 0.0)
                if contract.right is OptionRight.CALL
                else max(-signed, 0.0)
            )
            return self._result(payoff, characteristic_function_evaluations=0)

        dividend_discount = _positive_finite_exp(
            -problem.parameters.continuous_dividend_yield * year_fraction,
            name="dividend discount factor",
        )
        discounted_spot = spot * dividend_discount
        discounted_strike = strike * risk_free_discount
        if not isfinite(discounted_spot) or not isfinite(discounted_strike):
            msg = "discounted Heston spot/strike inputs must be finite"
            raise ValueError(msg)

        if spot == 0.0 or strike == 0.0:
            signed = discounted_spot - discounted_strike
            value = (
                max(signed, 0.0)
                if contract.right is OptionRight.CALL
                else max(-signed, 0.0)
            )
            return self._result(value, characteristic_function_evaluations=0)

        if problem.parameters.volatility_of_variance == 0.0:
            value = _deterministic_variance_limit_value(
                problem,
                contract,
                year_fraction,
            )
            return self._result(value, characteristic_function_evaluations=0)

        rate = cast(
            FlatMoneyMarketNumeraire,
            problem.numeraire,
        ).continuously_compounded_rate
        log_spot = log(spot)
        log_strike = log(strike)
        initial_variance = problem.current_state.value.instantaneous_variance
        phi_minus_i = heston_characteristic_function(
            -1j,
            log_spot=log_spot,
            year_fraction=year_fraction,
            rate=rate,
            parameters=problem.parameters,
            initial_variance=initial_variance,
        )
        if abs(phi_minus_i) == 0.0:
            msg = "Heston first-moment characteristic-function value must be non-zero"
            raise ValueError(msg)

        def p1_integrand(frequency: float) -> float:
            numerator = cmath.exp(-1j * frequency * log_strike) * (
                heston_characteristic_function(
                    frequency - 1j,
                    log_spot=log_spot,
                    year_fraction=year_fraction,
                    rate=rate,
                    parameters=problem.parameters,
                    initial_variance=initial_variance,
                )
            )
            denominator = 1j * frequency * phi_minus_i
            return _finite_complex(
                numerator / denominator,
                name="Heston P1 integrand",
            ).real

        def p2_integrand(frequency: float) -> float:
            numerator = cmath.exp(-1j * frequency * log_strike) * (
                heston_characteristic_function(
                    frequency,
                    log_spot=log_spot,
                    year_fraction=year_fraction,
                    rate=rate,
                    parameters=problem.parameters,
                    initial_variance=initial_variance,
                )
            )
            return _finite_complex(
                numerator / (1j * frequency),
                name="Heston P2 integrand",
            ).real

        p1 = (
            0.5
            + _simpson_integral(
                p1_integrand,
                lower=self.integration_lower_bound,
                upper=self.integration_upper_bound,
                intervals=self.intervals,
            )
            / pi
        )
        p2 = (
            0.5
            + _simpson_integral(
                p2_integrand,
                lower=self.integration_lower_bound,
                upper=self.integration_upper_bound,
                intervals=self.intervals,
            )
            / pi
        )
        if not isfinite(p1) or not isfinite(p2):
            msg = "Heston risk-neutral exercise probabilities must be finite"
            raise ValueError(msg)

        if contract.right is OptionRight.CALL:
            present_value = discounted_spot * p1 - discounted_strike * p2
        else:
            present_value = discounted_strike * (1.0 - p2) - discounted_spot * (
                1.0 - p1
            )
        if not isfinite(present_value):
            msg = "Heston Fourier present value must be finite"
            raise ValueError(msg)
        characteristic_function_evaluations = 2 * (self.intervals + 1) + 1
        return self._result(
            present_value,
            characteristic_function_evaluations=characteristic_function_evaluations,
        )

    def _result(
        self,
        present_value: float,
        *,
        characteristic_function_evaluations: int,
    ) -> HestonFourierValuationResult:
        return HestonFourierValuationResult(
            present_value=present_value,
            integration_lower_bound=self.integration_lower_bound,
            integration_upper_bound=self.integration_upper_bound,
            intervals=self.intervals,
            characteristic_function_evaluations=characteristic_function_evaluations,
        )
