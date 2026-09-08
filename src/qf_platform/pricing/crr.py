"""Cox-Ross-Rubinstein valuation for the concrete M1 equity-option family."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import exp, isfinite, sqrt
from typing import cast

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


def _intrinsic(right: OptionRight, spot: float, strike: float) -> float:
    signed = spot - strike
    if right is OptionRight.CALL:
        return max(signed, 0.0)
    return max(-signed, 0.0)


def _discounted_deterministic_value(
    problem: PricingProblem[date, EquityState, BlackScholesParameters],
    contract: EuropeanOption,
    year_fraction: float,
) -> float:
    spot = problem.current_state.value.spot
    strike = contract.strike
    dividend_discount = exp(
        -problem.parameters.continuous_dividend_yield * year_fraction
    )
    numeraire_now = validated_numeraire_value(
        problem.numeraire,
        problem.valuation_time,
    )
    numeraire_expiry = validated_numeraire_value(problem.numeraire, contract.expiry)
    risk_free_discount = numeraire_now / numeraire_expiry
    signed = spot * dividend_discount - strike * risk_free_discount
    if contract.right is OptionRight.CALL:
        return max(signed, 0.0)
    return max(-signed, 0.0)


@dataclass(frozen=True, slots=True)
class CoxRossRubinstein:
    """Configured CRR valuation method for the M1 Black-Scholes problem family.

    At a fixed positive number of steps, this is a discrete-time complete-market
    binomial model when its one-step risk-neutral probability lies strictly between
    zero and one. Across increasing step counts, the same construction is used as a
    numerical approximation to the continuous Black-Scholes limit.
    """

    steps: int

    def __post_init__(self) -> None:
        if type(self.steps) is not int:
            msg = "steps must be an integer"
            raise TypeError(msg)
        if self.steps <= 0:
            msg = "steps must be positive"
            raise ValueError(msg)

    def supports(
        self,
        problem: PricingProblem[date, EquityState, BlackScholesParameters],
        /,
    ) -> bool:
        contract = problem.contract
        if not (
            isinstance(problem.current_state.state_space, EquityStateSpace)
            and isinstance(problem.stochastic_law, BlackScholesLaw)
            and isinstance(contract, EuropeanOption)
            and isinstance(problem.numeraire, FlatMoneyMarketNumeraire)
            and contract.expiry >= problem.valuation_time
        ):
            return False

        year_fraction = actual_365_fixed_year_fraction(
            problem.valuation_time,
            contract.expiry,
        )
        volatility = problem.parameters.annualized_volatility
        if year_fraction == 0.0 or volatility == 0.0:
            return True

        try:
            _, _, probability, _ = self._step_parameters(problem, year_fraction)
        except (OverflowError, ValueError):
            return False
        return 0.0 < probability < 1.0

    def apply(
        self,
        problem: PricingProblem[date, EquityState, BlackScholesParameters],
        /,
    ) -> ValuationResult:
        if not self.supports(problem):
            msg = "CoxRossRubinstein does not support the supplied pricing problem"
            raise UnsupportedPricingProblem(msg)

        contract = cast(EuropeanOption, problem.contract)
        year_fraction = actual_365_fixed_year_fraction(
            problem.valuation_time,
            contract.expiry,
        )
        spot = problem.current_state.value.spot
        strike = contract.strike
        volatility = problem.parameters.annualized_volatility

        if year_fraction == 0.0:
            return ValuationResult(_intrinsic(contract.right, spot, strike))
        if volatility == 0.0:
            return ValuationResult(
                _discounted_deterministic_value(problem, contract, year_fraction)
            )

        up, down, probability, step_discount = self._step_parameters(
            problem,
            year_fraction,
        )
        values = self._terminal_payoffs(
            contract.right,
            spot,
            strike,
            up,
            down,
        )
        one_minus_probability = 1.0 - probability
        for level in range(self.steps, 0, -1):
            for node in range(level):
                values[node] = step_discount * (
                    probability * values[node]
                    + one_minus_probability * values[node + 1]
                )
        return ValuationResult(values[0])

    def _step_parameters(
        self,
        problem: PricingProblem[date, EquityState, BlackScholesParameters],
        year_fraction: float,
    ) -> tuple[float, float, float, float]:
        dt = year_fraction / self.steps
        volatility = problem.parameters.annualized_volatility
        up = exp(volatility * sqrt(dt))
        down = 1.0 / up
        rate = cast(
            FlatMoneyMarketNumeraire,
            problem.numeraire,
        ).continuously_compounded_rate
        dividend_yield = problem.parameters.continuous_dividend_yield
        growth = exp((rate - dividend_yield) * dt)
        denominator = up - down
        if denominator <= 0.0 or not isfinite(denominator):
            msg = "CRR up/down factors must define a non-degenerate finite tree"
            raise ValueError(msg)
        probability = (growth - down) / denominator
        step_discount = exp(-rate * dt)
        if not all(isfinite(value) for value in (probability, step_discount)):
            msg = "CRR step parameters must be finite"
            raise ValueError(msg)
        return up, down, probability, step_discount

    def _terminal_payoffs(
        self,
        right: OptionRight,
        spot: float,
        strike: float,
        up: float,
        down: float,
    ) -> list[float]:
        if spot == 0.0:
            return [_intrinsic(right, 0.0, strike)] * (self.steps + 1)

        terminal_spot = spot * up**self.steps
        ratio = down / up
        values: list[float] = []
        for _ in range(self.steps + 1):
            if not isfinite(terminal_spot):
                msg = "CRR terminal state must be finite"
                raise ValueError(msg)
            values.append(_intrinsic(right, terminal_spot, strike))
            terminal_spot *= ratio
        return values
