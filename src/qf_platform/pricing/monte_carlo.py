"""Monte Carlo valuation for the concrete M1 European Black-Scholes family."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from math import exp, isfinite, sqrt
from typing import cast

from qf_platform._validation import finite_real, nonnegative_finite_real
from qf_platform.pricing.black_scholes import (
    BlackScholesLaw,
    BlackScholesParameters,
)
from qf_platform.pricing.dates import actual_365_fixed_year_fraction
from qf_platform.pricing.equity import (
    EquityState,
    EquityStateSpace,
    EuropeanOption,
    OptionRight,
)
from qf_platform.pricing.measures import validated_numeraire_value
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.valuation import UnsupportedPricingProblem, ValuationResult

_NORMAL_95_Z = 1.959963984540054


def _payoff(right: OptionRight, terminal_spot: float, strike: float) -> float:
    signed = terminal_spot - strike
    if right is OptionRight.CALL:
        return max(signed, 0.0)
    return max(-signed, 0.0)


@dataclass(frozen=True, slots=True)
class MonteCarloValuationResult(ValuationResult):
    """Immutable Monte Carlo estimate with explicit sampling uncertainty.

    The confidence interval is the conventional normal-approximation 95% interval
    ``estimate ± 1.959963984540054 * standard_error``. It describes sampling
    uncertainty of this estimator; it is not a deterministic pricing tolerance.
    """

    standard_error: float
    confidence_interval_95: tuple[float, float]
    paths: int
    seed: int

    def __post_init__(self) -> None:
        ValuationResult.__post_init__(self)
        object.__setattr__(
            self,
            "standard_error",
            nonnegative_finite_real(self.standard_error, name="standard_error"),
        )
        if len(self.confidence_interval_95) != 2:
            msg = "confidence_interval_95 must contain lower and upper bounds"
            raise ValueError(msg)
        lower = finite_real(self.confidence_interval_95[0], name="confidence lower")
        upper = finite_real(self.confidence_interval_95[1], name="confidence upper")
        if lower > upper:
            msg = "confidence interval lower bound must not exceed upper bound"
            raise ValueError(msg)
        object.__setattr__(self, "confidence_interval_95", (lower, upper))
        if type(self.paths) is not int:
            msg = "paths must be an integer"
            raise TypeError(msg)
        if self.paths < 2:
            msg = "paths must be at least 2 to estimate sampling uncertainty"
            raise ValueError(msg)
        if type(self.seed) is not int:
            msg = "seed must be an integer"
            raise TypeError(msg)


@dataclass(frozen=True, slots=True)
class MonteCarloEuropeanOption:
    """Exact-terminal GBM Monte Carlo valuation with explicitly owned RNG seed.

    Each application creates a fresh local ``random.Random`` from ``seed``. The
    method therefore has no ambient or shared mutable RNG state. It samples the exact
    Black-Scholes terminal distribution because a European terminal payoff does not
    require a time-discretized path approximation.
    """

    paths: int
    seed: int

    def __post_init__(self) -> None:
        if type(self.paths) is not int:
            msg = "paths must be an integer"
            raise TypeError(msg)
        if self.paths < 2:
            msg = "paths must be at least 2"
            raise ValueError(msg)
        if type(self.seed) is not int:
            msg = "seed must be an integer"
            raise TypeError(msg)

    def supports(
        self,
        problem: PricingProblem[date, EquityState, BlackScholesParameters],
        /,
    ) -> bool:
        contract = problem.contract
        return (
            isinstance(problem.current_state.state_space, EquityStateSpace)
            and isinstance(problem.stochastic_law, BlackScholesLaw)
            and isinstance(contract, EuropeanOption)
            and isinstance(problem.numeraire, FlatMoneyMarketNumeraire)
            and contract.expiry >= problem.valuation_time
        )

    def apply(
        self,
        problem: PricingProblem[date, EquityState, BlackScholesParameters],
        /,
    ) -> MonteCarloValuationResult:
        if not self.supports(problem):
            msg = "MonteCarloEuropeanOption does not support the supplied pricing problem"
            raise UnsupportedPricingProblem(msg)

        contract = cast(EuropeanOption, problem.contract)
        year_fraction = actual_365_fixed_year_fraction(
            problem.valuation_time,
            contract.expiry,
        )
        spot = problem.current_state.value.spot
        strike = contract.strike
        rate = cast(
            FlatMoneyMarketNumeraire,
            problem.numeraire,
        ).continuously_compounded_rate
        dividend_yield = problem.parameters.continuous_dividend_yield
        volatility = problem.parameters.annualized_volatility
        numeraire_now = validated_numeraire_value(
            problem.numeraire,
            problem.valuation_time,
        )
        numeraire_expiry = validated_numeraire_value(problem.numeraire, contract.expiry)
        discount = numeraire_now / numeraire_expiry

        if year_fraction == 0.0:
            present_value = _payoff(contract.right, spot, strike)
            return self._deterministic_result(present_value)
        if volatility == 0.0 or spot == 0.0:
            terminal_spot = spot * exp((rate - dividend_yield) * year_fraction)
            present_value = discount * _payoff(
                contract.right,
                terminal_spot,
                strike,
            )
            return self._deterministic_result(present_value)

        rng = random.Random(self.seed)
        drift = (rate - dividend_yield - 0.5 * volatility * volatility) * year_fraction
        diffusion = volatility * sqrt(year_fraction)
        mean = 0.0
        sum_squared_deviations = 0.0

        for sample_number in range(1, self.paths + 1):
            normal_draw = rng.gauss(0.0, 1.0)
            try:
                terminal_spot = spot * exp(drift + diffusion * normal_draw)
            except OverflowError as exc:
                msg = "simulated terminal spot must be finite"
                raise ValueError(msg) from exc
            discounted_payoff = discount * _payoff(
                contract.right,
                terminal_spot,
                strike,
            )
            if not isfinite(discounted_payoff):
                msg = "discounted simulated payoff must be finite"
                raise ValueError(msg)
            difference = discounted_payoff - mean
            mean += difference / sample_number
            sum_squared_deviations += difference * (discounted_payoff - mean)

        sample_variance = sum_squared_deviations / (self.paths - 1)
        standard_error = sqrt(max(sample_variance, 0.0) / self.paths)
        half_width = _NORMAL_95_Z * standard_error
        return MonteCarloValuationResult(
            present_value=mean,
            standard_error=standard_error,
            confidence_interval_95=(mean - half_width, mean + half_width),
            paths=self.paths,
            seed=self.seed,
        )

    def _deterministic_result(self, present_value: float) -> MonteCarloValuationResult:
        return MonteCarloValuationResult(
            present_value=present_value,
            standard_error=0.0,
            confidence_interval_95=(present_value, present_value),
            paths=self.paths,
            seed=self.seed,
        )
