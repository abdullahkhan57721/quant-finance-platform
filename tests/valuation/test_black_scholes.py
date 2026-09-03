import math
from dataclasses import dataclass
from datetime import date

import pytest

from qf_platform.instruments import EuropeanOption, OptionRight
from qf_platform.market import FlatContinuousDiscountCurve, MarketEnvironment
from qf_platform.models import BlackScholesParameters
from qf_platform.valuation import black_scholes_present_value


VALUATION_DATE = date(2026, 1, 1)
ONE_YEAR = date(2027, 1, 1)
ANALYTIC_ABS_TOL = 2e-13


def make_market(
    *,
    spot: float = 100.0,
    risk_free_rate: float = 0.05,
    dividend_yield: float = 0.0,
    valuation_date: date = VALUATION_DATE,
) -> MarketEnvironment:
    return MarketEnvironment(
        valuation_date=valuation_date,
        spot=spot,
        risk_free_discounting=FlatContinuousDiscountCurve(
            valuation_date=valuation_date,
            continuously_compounded_rate=risk_free_rate,
        ),
        dividend_discounting=FlatContinuousDiscountCurve(
            valuation_date=valuation_date,
            continuously_compounded_rate=dividend_yield,
        ),
    )


def make_option(right: OptionRight, *, strike: float = 100.0) -> EuropeanOption:
    return EuropeanOption(expiry=ONE_YEAR, strike=strike, right=right)


def value(
    right: OptionRight,
    *,
    market: MarketEnvironment | None = None,
    strike: float = 100.0,
    volatility: float = 0.20,
) -> float:
    return black_scholes_present_value(
        make_option(right, strike=strike),
        market or make_market(),
        BlackScholesParameters(annualized_volatility=volatility),
    )


def test_reference_benchmark_call_and_put_values() -> None:
    # Canonical one-year benchmark: S=K=100, r=5% continuously compounded,
    # q=0, sigma=20%. Values are independently documented in the M1 model note.
    call = value(OptionRight.CALL)
    put = value(OptionRight.PUT)

    assert call == pytest.approx(10.450583572185565, rel=0.0, abs=ANALYTIC_ABS_TOL)
    assert put == pytest.approx(5.573526022256971, rel=0.0, abs=ANALYTIC_ABS_TOL)


@pytest.mark.parametrize(
    ("spot", "strike", "risk_free_rate", "dividend_yield", "volatility"),
    [
        (100.0, 100.0, 0.05, 0.00, 0.20),
        (120.0, 95.0, 0.03, 0.02, 0.35),
        (70.0, 100.0, -0.01, 0.04, 0.50),
    ],
)
def test_put_call_parity(
    spot: float,
    strike: float,
    risk_free_rate: float,
    dividend_yield: float,
    volatility: float,
) -> None:
    market = make_market(
        spot=spot,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
    )
    call = value(
        OptionRight.CALL,
        market=market,
        strike=strike,
        volatility=volatility,
    )
    put = value(
        OptionRight.PUT,
        market=market,
        strike=strike,
        volatility=volatility,
    )
    risk_free_df = market.risk_free_discounting.discount_factor(ONE_YEAR)
    dividend_df = market.dividend_discounting.discount_factor(ONE_YEAR)
    parity_rhs = spot * dividend_df - strike * risk_free_df

    assert call - put == pytest.approx(
        parity_rhs,
        rel=0.0,
        abs=ANALYTIC_ABS_TOL,
    )


@pytest.mark.parametrize(
    ("right", "spot", "strike", "risk_free_rate", "dividend_yield"),
    [
        (OptionRight.CALL, 100.0, 100.0, 0.05, 0.02),
        (OptionRight.CALL, 150.0, 100.0, -0.01, 0.00),
        (OptionRight.PUT, 100.0, 100.0, 0.05, 0.02),
        (OptionRight.PUT, 60.0, 100.0, 0.03, 0.01),
    ],
)
def test_discounted_no_arbitrage_bounds(
    right: OptionRight,
    spot: float,
    strike: float,
    risk_free_rate: float,
    dividend_yield: float,
) -> None:
    market = make_market(
        spot=spot,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
    )
    present_value = value(right, market=market, strike=strike, volatility=0.3)
    risk_free_df = market.risk_free_discounting.discount_factor(ONE_YEAR)
    dividend_df = market.dividend_discounting.discount_factor(ONE_YEAR)
    discounted_spot = spot * dividend_df
    discounted_strike = strike * risk_free_df

    if right is OptionRight.CALL:
        lower = max(discounted_spot - discounted_strike, 0.0)
        upper = discounted_spot
    else:
        lower = max(discounted_strike - discounted_spot, 0.0)
        upper = discounted_strike

    assert present_value >= lower - ANALYTIC_ABS_TOL
    assert present_value <= upper + ANALYTIC_ABS_TOL


@pytest.mark.parametrize(
    ("right", "spot", "strike", "expected"),
    [
        (OptionRight.CALL, 120.0, 100.0, 20.0),
        (OptionRight.CALL, 80.0, 100.0, 0.0),
        (OptionRight.PUT, 80.0, 100.0, 20.0),
        (OptionRight.PUT, 120.0, 100.0, 0.0),
    ],
)
def test_expiry_returns_intrinsic_value(
    right: OptionRight,
    spot: float,
    strike: float,
    expected: float,
) -> None:
    market = make_market(spot=spot, valuation_date=VALUATION_DATE)
    option = EuropeanOption(
        expiry=VALUATION_DATE,
        strike=strike,
        right=right,
    )

    present_value = black_scholes_present_value(
        option,
        market,
        BlackScholesParameters(annualized_volatility=0.9),
    )

    assert present_value == expected


@pytest.mark.parametrize("right", [OptionRight.CALL, OptionRight.PUT])
def test_zero_volatility_returns_discounted_deterministic_intrinsic(
    right: OptionRight,
) -> None:
    market = make_market(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.02,
    )
    risk_free_df = math.exp(-0.05)
    dividend_df = math.exp(-0.02)
    signed_intrinsic = 100.0 * dividend_df - 95.0 * risk_free_df
    expected = max(signed_intrinsic, 0.0)
    if right is OptionRight.PUT:
        expected = max(-signed_intrinsic, 0.0)

    present_value = value(
        right,
        market=market,
        strike=95.0,
        volatility=0.0,
    )

    assert present_value == pytest.approx(expected, rel=0.0, abs=ANALYTIC_ABS_TOL)


def test_zero_spot_limit() -> None:
    market = make_market(spot=0.0, risk_free_rate=0.05, dividend_yield=0.02)

    call = value(OptionRight.CALL, market=market, strike=100.0, volatility=0.3)
    put = value(OptionRight.PUT, market=market, strike=100.0, volatility=0.3)

    assert call == 0.0
    assert put == pytest.approx(
        100.0 * math.exp(-0.05),
        rel=0.0,
        abs=ANALYTIC_ABS_TOL,
    )


def test_zero_strike_limit() -> None:
    market = make_market(spot=100.0, risk_free_rate=0.05, dividend_yield=0.02)

    call = value(OptionRight.CALL, market=market, strike=0.0, volatility=0.3)
    put = value(OptionRight.PUT, market=market, strike=0.0, volatility=0.3)

    assert call == pytest.approx(
        100.0 * math.exp(-0.02),
        rel=0.0,
        abs=ANALYTIC_ABS_TOL,
    )
    assert put == 0.0


def test_positive_dividend_yield_changes_carry_in_correct_direction() -> None:
    no_dividend = value(
        OptionRight.CALL,
        market=make_market(dividend_yield=0.0),
    )
    positive_dividend = value(
        OptionRight.CALL,
        market=make_market(dividend_yield=0.04),
    )

    assert positive_dividend < no_dividend


def test_negative_interest_rate_is_supported() -> None:
    present_value = value(
        OptionRight.PUT,
        market=make_market(risk_free_rate=-0.02),
        volatility=0.25,
    )

    assert present_value > 0.0


def test_extreme_finite_moneyness_avoids_ratio_underflow() -> None:
    market = make_market(
        spot=1e-300,
        risk_free_rate=0.0,
        dividend_yield=0.0,
    )

    present_value = value(
        OptionRight.PUT,
        market=market,
        strike=1e300,
        volatility=0.2,
    )

    assert present_value == pytest.approx(1e300, rel=1e-15)


def test_expiry_before_valuation_date_is_rejected_by_valuation() -> None:
    market = make_market(valuation_date=date(2027, 1, 2))
    option = EuropeanOption(
        expiry=ONE_YEAR,
        strike=100.0,
        right=OptionRight.CALL,
    )

    with pytest.raises(ValueError, match="before"):
        black_scholes_present_value(
            option,
            market,
            BlackScholesParameters(annualized_volatility=0.2),
        )


@dataclass(frozen=True)
class InvalidDiscounting:
    valuation_date: date
    factor: float = 0.0

    def discount_factor(self, maturity: date) -> float:
        del maturity
        return self.factor


def test_valuation_rejects_nonpositive_discount_factor() -> None:
    market = MarketEnvironment(
        valuation_date=VALUATION_DATE,
        spot=100.0,
        risk_free_discounting=InvalidDiscounting(VALUATION_DATE),
        dividend_discounting=FlatContinuousDiscountCurve(
            valuation_date=VALUATION_DATE,
            continuously_compounded_rate=0.0,
        ),
    )

    with pytest.raises(ValueError, match="risk-free discount factor"):
        black_scholes_present_value(
            make_option(OptionRight.CALL),
            market,
            BlackScholesParameters(annualized_volatility=0.2),
        )


def test_valuation_rejects_overflowed_discounted_amount() -> None:
    market = MarketEnvironment(
        valuation_date=VALUATION_DATE,
        spot=1e308,
        risk_free_discounting=FlatContinuousDiscountCurve(
            valuation_date=VALUATION_DATE,
            continuously_compounded_rate=0.0,
        ),
        dividend_discounting=InvalidDiscounting(VALUATION_DATE, factor=1e308),
    )

    with pytest.raises(ValueError, match="discounted spot"):
        black_scholes_present_value(
            make_option(OptionRight.CALL),
            market,
            BlackScholesParameters(annualized_volatility=0.2),
        )
