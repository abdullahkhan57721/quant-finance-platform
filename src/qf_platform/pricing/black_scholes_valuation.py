"""Closed-form Black-Scholes valuation as an M0A ValuationMethod."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import erfc, exp, isfinite, log, sqrt
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
from qf_platform.pricing.valuation import (
    UnsupportedPricingProblem,
    ValuationResult,
)

_SQRT_TWO = sqrt(2.0)


def _standard_normal_cdf(value: float) -> float:
    return 0.5 * erfc(-value / _SQRT_TWO)


def _positive_finite_exponential(exponent: float, *, name: str) -> float:
    try:
        value = exp(exponent)
    except OverflowError as exc:
        msg = f"{name} must be positive and finite"
        raise ValueError(msg) from exc
    if not isfinite(value) or value <= 0.0:
        msg = f"{name} must be positive and finite"
        raise ValueError(msg)
    return value


def _finite_product(left: float, right: float, *, name: str) -> float:
    value = left * right
    if not isfinite(value):
        msg = f"{name} must be finite"
        raise ValueError(msg)
    return value


def _deterministic_value(
    right: OptionRight,
    discounted_spot: float,
    discounted_strike: float,
) -> float:
    signed_intrinsic = discounted_spot - discounted_strike
    if right is OptionRight.CALL:
        return max(signed_intrinsic, 0.0)
    return max(-signed_intrinsic, 0.0)


@dataclass(frozen=True, slots=True)
class BlackScholesClosedForm:
    """Analytic valuation method for the concrete M1 Black-Scholes problem family."""

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
    ) -> ValuationResult:
        if not self.supports(problem):
            msg = "BlackScholesClosedForm does not support the supplied pricing problem"
            raise UnsupportedPricingProblem(msg)

        contract = cast(EuropeanOption, problem.contract)
        valuation_date = problem.valuation_time
        year_fraction = actual_365_fixed_year_fraction(
            valuation_date,
            contract.expiry,
        )
        spot = problem.current_state.value.spot
        strike = contract.strike

        if year_fraction == 0.0:
            return ValuationResult(_deterministic_value(contract.right, spot, strike))

        numeraire_now = validated_numeraire_value(
            problem.numeraire,
            valuation_date,
        )
        numeraire_expiry = validated_numeraire_value(
            problem.numeraire,
            contract.expiry,
        )
        risk_free_discount = numeraire_now / numeraire_expiry
        if not isfinite(risk_free_discount) or risk_free_discount <= 0.0:
            msg = "risk-free discount factor must be positive and finite"
            raise ValueError(msg)

        parameters = problem.parameters
        dividend_discount = _positive_finite_exponential(
            -parameters.continuous_dividend_yield * year_fraction,
            name="dividend discount factor",
        )
        discounted_spot = _finite_product(
            spot,
            dividend_discount,
            name="discounted spot",
        )
        discounted_strike = _finite_product(
            strike,
            risk_free_discount,
            name="discounted strike",
        )
        volatility = parameters.annualized_volatility

        if volatility == 0.0 or spot == 0.0 or strike == 0.0:
            return ValuationResult(
                _deterministic_value(
                    contract.right,
                    discounted_spot,
                    discounted_strike,
                )
            )

        sigma_sqrt_t = volatility * sqrt(year_fraction)
        log_forward_moneyness = (
            log(spot) - log(strike) + log(dividend_discount) - log(risk_free_discount)
        )
        d1 = (
            log_forward_moneyness + 0.5 * volatility * volatility * year_fraction
        ) / sigma_sqrt_t
        d2 = d1 - sigma_sqrt_t

        if contract.right is OptionRight.CALL:
            present_value = discounted_spot * _standard_normal_cdf(
                d1
            ) - discounted_strike * _standard_normal_cdf(d2)
        else:
            present_value = discounted_strike * _standard_normal_cdf(
                -d2
            ) - discounted_spot * _standard_normal_cdf(-d1)
        return ValuationResult(present_value)
