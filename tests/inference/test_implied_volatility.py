from __future__ import annotations

from datetime import UTC, date, datetime
from math import erfc, exp, log, sqrt

import pytest

from qf_platform.inference import (
    BisectionImpliedVolatility,
    BlackScholesImpliedVolatilityProblem,
    ImpliedVolatilityConvergenceError,
    ImpliedVolatilityNotBracketed,
    InconsistentObservedPrice,
    InvalidImpliedVolatilityProblem,
    infer_implied_volatility,
    log_forward_moneyness,
)
from qf_platform.market_data import (
    NormalizedOptionObservation,
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    RawOptionQuote,
    RawUnderlyingObservation,
    normalize_european_option_midpoint,
)
from qf_platform.pricing import (
    FlatMoneyMarketNumeraire,
    OptionRight,
    PricingMeasureSemantics,
)

_VALUATION_DATE = date(2026, 1, 2)
_RETRIEVED_AT = datetime(2026, 1, 3, 12, tzinfo=UTC)


def _normal_cdf(value: float) -> float:
    return 0.5 * erfc(-value / sqrt(2.0))


def _black_scholes_price(
    *,
    spot: float,
    strike: float,
    year_fraction: float,
    rate: float,
    dividend_yield: float,
    volatility: float,
    right: OptionRight,
) -> float:
    discounted_spot = spot * exp(-dividend_yield * year_fraction)
    discounted_strike = strike * exp(-rate * year_fraction)
    if volatility == 0.0:
        signed = discounted_spot - discounted_strike
        return max(signed, 0.0) if right is OptionRight.CALL else max(-signed, 0.0)
    sigma_sqrt_t = volatility * sqrt(year_fraction)
    d1 = (
        log(spot / strike)
        + (rate - dividend_yield + 0.5 * volatility * volatility) * year_fraction
    ) / sigma_sqrt_t
    d2 = d1 - sigma_sqrt_t
    if right is OptionRight.CALL:
        return discounted_spot * _normal_cdf(d1) - discounted_strike * _normal_cdf(d2)
    return discounted_strike * _normal_cdf(-d2) - discounted_spot * _normal_cdf(-d1)


def _observation(
    *,
    target_price: float,
    expiry: date = date(2027, 1, 2),
    strike: float = 100.0,
    spot: float = 100.0,
    right: OptionRight = OptionRight.CALL,
    half_spread: float = 0.01,
) -> NormalizedOptionObservation:
    provenance = ObservationProvenance(
        provider="synthetic:test",
        source="inference unit fixture",
        market_date=_VALUATION_DATE,
        retrieved_at=_RETRIEVED_AT,
        raw_artifact_sha256="b" * 64,
        license_notes="synthetic fixture; unrestricted test use",
    )
    quote = RawOptionQuote(
        contract_id=f"SYN-{expiry.isoformat()}-{right.value}-{strike}",
        underlying_id="SYN",
        expiry=expiry,
        strike=strike,
        right=right,
        exercise_style=OptionExerciseStyle.EUROPEAN,
        provenance=provenance,
        bid=target_price - half_spread,
        ask=target_price + half_spread,
        settlement_time=OptionSettlementTime.PM,
    )
    underlying = RawUnderlyingObservation(
        underlying_id="SYN",
        value=spot,
        provenance=provenance,
    )
    return normalize_european_option_midpoint(quote, underlying)


def _problem(
    observation: NormalizedOptionObservation,
    *,
    rate: float = 0.05,
    dividend_yield: float = 0.0,
    maximum_volatility: float = 5.0,
) -> BlackScholesImpliedVolatilityProblem:
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=rate,
    )
    measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
    return BlackScholesImpliedVolatilityProblem(
        observation=observation,
        numeraire=numeraire,
        pricing_measure=measure,
        continuous_dividend_yield=dividend_yield,
        maximum_annualized_volatility=maximum_volatility,
    )


def test_bisection_recovers_known_black_scholes_volatility_and_conditioning() -> None:
    target = _black_scholes_price(
        spot=100.0,
        strike=100.0,
        year_fraction=1.0,
        rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        right=OptionRight.CALL,
    )
    observation = _observation(target_price=target)

    result = infer_implied_volatility(
        _problem(observation), BisectionImpliedVolatility()
    )

    assert result.observation is observation
    assert result.annualized_volatility == pytest.approx(0.20, abs=1.0e-8)
    assert result.model_price == pytest.approx(target, abs=1.0e-8)
    assert result.residual == pytest.approx(0.0, abs=1.0e-8)
    assert result.vega is not None
    assert result.vega == pytest.approx(37.5240346917, rel=1.0e-9)
    assert result.volatility_change_per_price_unit == pytest.approx(
        1.0 / result.vega,
    )
    assert result.local_volatility_shift_for_half_spread == pytest.approx(
        0.01 / result.vega,
    )


def test_financially_inconsistent_target_fails_before_root_search() -> None:
    observation = _observation(target_price=101.0)

    with pytest.raises(
        InconsistentObservedPrice,
        match="outside European option price bounds",
    ):
        _problem(observation, rate=0.0)


def test_financially_admissible_target_can_still_fail_configured_bracket() -> None:
    target = _black_scholes_price(
        spot=100.0,
        strike=100.0,
        year_fraction=1.0,
        rate=0.05,
        dividend_yield=0.0,
        volatility=0.80,
        right=OptionRight.CALL,
    )
    problem = _problem(_observation(target_price=target), maximum_volatility=0.40)

    with pytest.raises(ImpliedVolatilityNotBracketed, match="not bracketed"):
        infer_implied_volatility(problem, BisectionImpliedVolatility())


def test_unresolved_iteration_limit_has_deterministic_failure_semantics() -> None:
    target = _black_scholes_price(
        spot=100.0,
        strike=100.0,
        year_fraction=1.0,
        rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        right=OptionRight.CALL,
    )
    method = BisectionImpliedVolatility(
        price_tolerance=1.0e-16,
        volatility_tolerance=1.0e-16,
        max_iterations=1,
    )

    with pytest.raises(ImpliedVolatilityConvergenceError, match="max_iterations"):
        infer_implied_volatility(_problem(_observation(target_price=target)), method)


def test_exact_zero_volatility_boundary_is_not_mislabeled_as_low_vega_solution() -> (
    None
):
    lower_bound = 100.0 - 100.0 * exp(-0.05)
    observation = _observation(target_price=lower_bound, half_spread=0.0)

    result = infer_implied_volatility(
        _problem(observation), BisectionImpliedVolatility()
    )

    assert result.annualized_volatility == 0.0
    assert result.iterations == 0
    assert result.vega is None
    assert result.volatility_change_per_price_unit is None


def test_near_expiry_problem_recovers_known_volatility() -> None:
    expiry = date(2026, 1, 3)
    year_fraction = 1.0 / 365.0
    target = _black_scholes_price(
        spot=100.0,
        strike=100.0,
        year_fraction=year_fraction,
        rate=0.03,
        dividend_yield=0.01,
        volatility=0.35,
        right=OptionRight.CALL,
    )
    observation = _observation(
        target_price=target,
        expiry=expiry,
        half_spread=min(0.001, target / 4.0),
    )

    result = infer_implied_volatility(
        _problem(observation, rate=0.03, dividend_yield=0.01),
        BisectionImpliedVolatility(),
    )

    assert result.annualized_volatility == pytest.approx(0.35, abs=1.0e-8)


def test_low_vega_deep_otm_solution_reports_worse_inverse_conditioning() -> None:
    atm_price = _black_scholes_price(
        spot=100.0,
        strike=100.0,
        year_fraction=1.0,
        rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        right=OptionRight.CALL,
    )
    wing_price = _black_scholes_price(
        spot=100.0,
        strike=200.0,
        year_fraction=1.0,
        rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        right=OptionRight.CALL,
    )
    atm = infer_implied_volatility(
        _problem(_observation(target_price=atm_price)),
        BisectionImpliedVolatility(),
    )
    wing = infer_implied_volatility(
        _problem(
            _observation(
                target_price=wing_price,
                strike=200.0,
                half_spread=0.001,
            )
        ),
        BisectionImpliedVolatility(),
    )

    assert wing.vega is not None
    assert atm.vega is not None
    assert wing.vega < atm.vega
    assert wing.volatility_change_per_price_unit is not None
    assert atm.volatility_change_per_price_unit is not None
    assert (
        wing.volatility_change_per_price_unit
        > 100.0 * atm.volatility_change_per_price_unit
    )


def test_nonpositive_time_to_expiry_is_a_financial_problem_failure() -> None:
    observation = _observation(target_price=1.0, expiry=_VALUATION_DATE)

    with pytest.raises(
        InvalidImpliedVolatilityProblem, match="positive time to expiry"
    ):
        _problem(observation)


def test_log_forward_moneyness_uses_rate_and_carry_inputs() -> None:
    rate = 0.03
    dividend_yield = 0.01
    forward = 100.0 * exp(rate - dividend_yield)
    target = _black_scholes_price(
        spot=100.0,
        strike=forward,
        year_fraction=1.0,
        rate=rate,
        dividend_yield=dividend_yield,
        volatility=0.20,
        right=OptionRight.CALL,
    )
    problem = _problem(
        _observation(target_price=target, strike=forward),
        rate=rate,
        dividend_yield=dividend_yield,
    )

    assert log_forward_moneyness(problem) == pytest.approx(0.0, abs=1.0e-14)
