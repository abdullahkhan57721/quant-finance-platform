"""Independent Monte Carlo valuation for Heston European options."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from math import exp, isfinite, log, sqrt
from typing import cast

from qf_platform.pricing.dates import actual_365_fixed_year_fraction
from qf_platform.pricing.equity import EuropeanOption, OptionRight
from qf_platform.pricing.heston import (
    HestonEquityState,
    HestonLaw,
    HestonParameters,
    HestonStateSpace,
    integrated_deterministic_heston_variance,
)
from qf_platform.pricing.measures import validated_numeraire_value
from qf_platform.pricing.monte_carlo import MonteCarloValuationResult
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.valuation import UnsupportedPricingProblem

_NORMAL_95_Z = 1.959963984540054
_FULL_TRUNCATION_EULER = "full_truncation_euler"
_EXACT_DETERMINISTIC_VARIANCE = "exact_deterministic_variance"
_NO_VARIANCE_PATH = "not_applicable"
_SUPPORTED_VARIANCE_SCHEMES = frozenset(
    {
        _FULL_TRUNCATION_EULER,
        _EXACT_DETERMINISTIC_VARIANCE,
        _NO_VARIANCE_PATH,
    }
)


def _payoff(right: OptionRight, terminal_spot: float, strike: float) -> float:
    signed = terminal_spot - strike
    if right is OptionRight.CALL:
        return max(signed, 0.0)
    return max(-signed, 0.0)


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


@dataclass(frozen=True, slots=True)
class HestonMonteCarloValuationResult(MonteCarloValuationResult):
    """Heston Monte Carlo value with sampling and discretization evidence.

    ``negative_variance_proposals`` counts full-truncation Euler transitions whose raw
    next variance is negative. It is diagnostic evidence of variance-boundary pressure;
    it is not a financial-model error count.
    """

    time_steps: int
    negative_variance_proposals: int
    variance_scheme: str

    def __post_init__(self) -> None:
        MonteCarloValuationResult.__post_init__(self)
        if type(self.time_steps) is not int:
            msg = "time_steps must be an integer"
            raise TypeError(msg)
        if self.time_steps < 1:
            msg = "time_steps must be positive"
            raise ValueError(msg)
        if type(self.negative_variance_proposals) is not int:
            msg = "negative_variance_proposals must be an integer"
            raise TypeError(msg)
        if self.negative_variance_proposals < 0:
            msg = "negative_variance_proposals must be non-negative"
            raise ValueError(msg)
        if self.negative_variance_proposals > self.paths * self.time_steps:
            msg = (
                "negative_variance_proposals cannot exceed simulated variance "
                "transitions"
            )
            raise ValueError(msg)
        if self.variance_scheme not in _SUPPORTED_VARIANCE_SCHEMES:
            msg = "variance_scheme is not a supported Heston Monte Carlo scheme label"
            raise ValueError(msg)
        if (
            self.variance_scheme != _FULL_TRUNCATION_EULER
            and self.negative_variance_proposals != 0
        ):
            msg = (
                "negative_variance_proposals must be zero when no full-truncation "
                "variance path is simulated"
            )
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class HestonMonteCarloEuropeanOption:
    """Seeded Heston Monte Carlo with explicit variance-discretization semantics.

    For positive volatility of variance, the method uses full-truncation Euler: the raw
    Euler variance state may cross below zero, while drift/diffusion coefficients use
    its positive part. Negative raw proposals are counted as discretization-pressure
    evidence. This scheme belongs to the numerical method, not ``HestonLaw``.

    At exactly ``xi=0``, variance is deterministic and terminal log spot is sampled
    exactly from the integrated variance. That boundary has sampling error but no
    Heston time-discretization bias. Expiry/zero-spot/zero-strike cases require no
    variance path at all.
    """

    paths: int
    time_steps: int
    seed: int

    def __post_init__(self) -> None:
        if type(self.paths) is not int:
            msg = "paths must be an integer"
            raise TypeError(msg)
        if self.paths < 2:
            msg = "paths must be at least 2"
            raise ValueError(msg)
        if type(self.time_steps) is not int:
            msg = "time_steps must be an integer"
            raise TypeError(msg)
        if self.time_steps < 1:
            msg = "time_steps must be positive"
            raise ValueError(msg)
        if type(self.seed) is not int:
            msg = "seed must be an integer"
            raise TypeError(msg)

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
    ) -> HestonMonteCarloValuationResult:
        if not self.supports(problem):
            msg = (
                "HestonMonteCarloEuropeanOption does not support the supplied pricing "
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
        discount = numeraire_now / numeraire_expiry
        if not isfinite(discount) or discount <= 0.0:
            msg = "risk-free discount factor must be positive and finite"
            raise ValueError(msg)

        if year_fraction == 0.0:
            return self._deterministic_result(_payoff(contract.right, spot, strike))

        dividend_discount = _positive_finite_exp(
            -problem.parameters.continuous_dividend_yield * year_fraction,
            name="dividend discount factor",
        )
        discounted_spot = spot * dividend_discount
        discounted_strike = strike * discount
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
            return self._deterministic_result(value)

        if problem.parameters.volatility_of_variance == 0.0:
            return self._exact_deterministic_variance_sample(
                problem,
                contract,
                year_fraction,
                discount,
            )

        return self._full_truncation_sample(
            problem,
            contract,
            year_fraction,
            discount,
        )

    def _exact_deterministic_variance_sample(
        self,
        problem: PricingProblem[date, HestonEquityState, HestonParameters],
        contract: EuropeanOption,
        year_fraction: float,
        discount: float,
    ) -> HestonMonteCarloValuationResult:
        integrated_variance = integrated_deterministic_heston_variance(
            problem.current_state.value.instantaneous_variance,
            problem.parameters,
            year_fraction,
        )
        rate = cast(
            FlatMoneyMarketNumeraire,
            problem.numeraire,
        ).continuously_compounded_rate
        drift = (
            rate - problem.parameters.continuous_dividend_yield
        ) * year_fraction - 0.5 * integrated_variance
        diffusion = sqrt(integrated_variance)
        log_spot = log(problem.current_state.value.spot)
        rng = random.Random(self.seed)
        mean = 0.0
        sum_squared_deviations = 0.0

        for sample_number in range(1, self.paths + 1):
            terminal_log_spot = log_spot + drift + diffusion * rng.gauss(0.0, 1.0)
            try:
                terminal_spot = exp(terminal_log_spot)
            except OverflowError as exc:
                msg = "simulated terminal Heston spot must be finite"
                raise ValueError(msg) from exc
            discounted_payoff = discount * _payoff(
                contract.right,
                terminal_spot,
                contract.strike,
            )
            if not isfinite(discounted_payoff):
                msg = "discounted simulated Heston payoff must be finite"
                raise ValueError(msg)
            difference = discounted_payoff - mean
            mean += difference / sample_number
            sum_squared_deviations += difference * (discounted_payoff - mean)

        return self._sample_result(
            mean,
            sum_squared_deviations,
            negative_variance_proposals=0,
            variance_scheme=_EXACT_DETERMINISTIC_VARIANCE,
        )

    def _full_truncation_sample(
        self,
        problem: PricingProblem[date, HestonEquityState, HestonParameters],
        contract: EuropeanOption,
        year_fraction: float,
        discount: float,
    ) -> HestonMonteCarloValuationResult:
        parameters = problem.parameters
        rate = cast(
            FlatMoneyMarketNumeraire,
            problem.numeraire,
        ).continuously_compounded_rate
        step = year_fraction / self.time_steps
        sqrt_step = sqrt(step)
        correlation_scale = sqrt(max(1.0 - parameters.correlation**2, 0.0))
        rng = random.Random(self.seed)
        mean = 0.0
        sum_squared_deviations = 0.0
        negative_variance_proposals = 0
        initial_log_spot = log(problem.current_state.value.spot)
        initial_variance = problem.current_state.value.instantaneous_variance

        for sample_number in range(1, self.paths + 1):
            log_spot = initial_log_spot
            raw_variance = initial_variance
            for _ in range(self.time_steps):
                variance = max(raw_variance, 0.0)
                variance_shock = rng.gauss(0.0, 1.0)
                independent_shock = rng.gauss(0.0, 1.0)
                spot_shock = (
                    parameters.correlation * variance_shock
                    + correlation_scale * independent_shock
                )
                sqrt_variance = sqrt(variance)
                log_spot += (
                    rate
                    - parameters.continuous_dividend_yield
                    - 0.5 * variance
                ) * step + sqrt_variance * sqrt_step * spot_shock
                next_raw_variance = raw_variance + (
                    parameters.mean_reversion_speed
                    * (parameters.long_run_variance - variance)
                    * step
                    + parameters.volatility_of_variance
                    * sqrt_variance
                    * sqrt_step
                    * variance_shock
                )
                if next_raw_variance < 0.0:
                    negative_variance_proposals += 1
                raw_variance = next_raw_variance

            if not isfinite(log_spot):
                msg = "simulated terminal Heston log spot must be finite"
                raise ValueError(msg)
            try:
                terminal_spot = exp(log_spot)
            except OverflowError as exc:
                msg = "simulated terminal Heston spot must be finite"
                raise ValueError(msg) from exc
            discounted_payoff = discount * _payoff(
                contract.right,
                terminal_spot,
                contract.strike,
            )
            if not isfinite(discounted_payoff):
                msg = "discounted simulated Heston payoff must be finite"
                raise ValueError(msg)
            difference = discounted_payoff - mean
            mean += difference / sample_number
            sum_squared_deviations += difference * (discounted_payoff - mean)

        return self._sample_result(
            mean,
            sum_squared_deviations,
            negative_variance_proposals=negative_variance_proposals,
            variance_scheme=_FULL_TRUNCATION_EULER,
        )

    def _sample_result(
        self,
        mean: float,
        sum_squared_deviations: float,
        *,
        negative_variance_proposals: int,
        variance_scheme: str,
    ) -> HestonMonteCarloValuationResult:
        sample_variance = sum_squared_deviations / (self.paths - 1)
        standard_error = sqrt(max(sample_variance, 0.0) / self.paths)
        half_width = _NORMAL_95_Z * standard_error
        return HestonMonteCarloValuationResult(
            present_value=mean,
            standard_error=standard_error,
            confidence_interval_95=(mean - half_width, mean + half_width),
            paths=self.paths,
            seed=self.seed,
            time_steps=self.time_steps,
            negative_variance_proposals=negative_variance_proposals,
            variance_scheme=variance_scheme,
        )

    def _deterministic_result(
        self,
        present_value: float,
    ) -> HestonMonteCarloValuationResult:
        return HestonMonteCarloValuationResult(
            present_value=present_value,
            standard_error=0.0,
            confidence_interval_95=(present_value, present_value),
            paths=self.paths,
            seed=self.seed,
            time_steps=self.time_steps,
            negative_variance_proposals=0,
            variance_scheme=_NO_VARIANCE_PATH,
        )
