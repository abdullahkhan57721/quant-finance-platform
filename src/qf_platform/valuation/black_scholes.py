"""Analytic Black-Scholes valuation for European options."""

from math import erf, isfinite, log, sqrt

from qf_platform.instruments import EuropeanOption, OptionRight
from qf_platform.market import MarketEnvironment, actual_365_fixed_year_fraction
from qf_platform.models import BlackScholesParameters

_SQRT_TWO = sqrt(2.0)


def _standard_normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + erf(value / _SQRT_TWO))


def _checked_discount_factor(value: float, *, name: str) -> float:
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return value


def black_scholes_present_value(
    option: EuropeanOption,
    market: MarketEnvironment,
    parameters: BlackScholesParameters,
) -> float:
    """Return the Black-Scholes present value of a European call or put.

    The implementation uses spot ``S``, strike ``K``, Actual/365 Fixed model
    time ``T``, risk-free discount factor ``D_r(T)``, dividend/carry discount
    factor ``D_q(T)``, and annualized decimal volatility ``sigma``.

    For positive ``S``, ``K``, ``T``, and ``sigma`` it evaluates the generalized
    deterministic-carry Black-Scholes formula through discount factors rather
    than naked rate scalars. Expiry and deterministic/degenerate limits are
    handled explicitly to avoid undefined logarithms or divisions.
    """
    year_fraction = actual_365_fixed_year_fraction(
        market.valuation_date,
        option.expiry,
    )
    spot = market.spot
    strike = option.strike

    if year_fraction == 0.0:
        if option.right is OptionRight.CALL:
            return max(spot - strike, 0.0)
        return max(strike - spot, 0.0)

    risk_free_df = _checked_discount_factor(
        market.risk_free_discounting.discount_factor(option.expiry),
        name="risk-free discount factor",
    )
    dividend_df = _checked_discount_factor(
        market.dividend_discounting.discount_factor(option.expiry),
        name="dividend discount factor",
    )
    volatility = parameters.annualized_volatility

    discounted_spot = spot * dividend_df
    discounted_strike = strike * risk_free_df

    if volatility == 0.0 or spot == 0.0 or strike == 0.0:
        signed_intrinsic = discounted_spot - discounted_strike
        if option.right is OptionRight.CALL:
            return max(signed_intrinsic, 0.0)
        return max(-signed_intrinsic, 0.0)

    sigma_sqrt_t = volatility * sqrt(year_fraction)
    log_forward_moneyness = (
        log(spot / strike) + log(dividend_df) - log(risk_free_df)
    )
    d1 = (
        log_forward_moneyness
        + 0.5 * volatility * volatility * year_fraction
    ) / sigma_sqrt_t
    d2 = d1 - sigma_sqrt_t

    if option.right is OptionRight.CALL:
        present_value = (
            discounted_spot * _standard_normal_cdf(d1)
            - discounted_strike * _standard_normal_cdf(d2)
        )
    else:
        present_value = (
            discounted_strike * _standard_normal_cdf(-d2)
            - discounted_spot * _standard_normal_cdf(-d1)
        )

    if not isfinite(present_value):
        raise ValueError("Black-Scholes present value must be finite")
    return present_value
