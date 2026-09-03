from datetime import date
from typing import cast

import pytest

from qf_platform.market import (
    DiscountFactorProvider,
    FlatContinuousDiscountCurve,
    MarketEnvironment,
)

VALUATION_DATE = date(2026, 1, 1)


def make_curve(
    rate: float = 0.0,
    *,
    valuation_date: date = VALUATION_DATE,
) -> FlatContinuousDiscountCurve:
    return FlatContinuousDiscountCurve(
        valuation_date=valuation_date,
        continuously_compounded_rate=rate,
    )


def test_market_environment_normalizes_spot_and_is_valuation_ready() -> None:
    environment = MarketEnvironment(
        valuation_date=VALUATION_DATE,
        spot=100,
        risk_free_discounting=make_curve(0.05),
        dividend_discounting=make_curve(0.02),
    )

    assert environment.spot == 100.0
    assert isinstance(environment.spot, float)


@pytest.mark.parametrize("spot", [-1.0, float("inf"), float("nan")])
def test_market_environment_rejects_invalid_spot(spot: float) -> None:
    with pytest.raises(ValueError):
        MarketEnvironment(
            valuation_date=VALUATION_DATE,
            spot=spot,
            risk_free_discounting=make_curve(),
            dividend_discounting=make_curve(),
        )


def test_market_environment_allows_zero_spot_as_structurally_meaningful() -> None:
    environment = MarketEnvironment(
        valuation_date=VALUATION_DATE,
        spot=0.0,
        risk_free_discounting=make_curve(),
        dividend_discounting=make_curve(),
    )

    assert environment.spot == 0.0


def test_market_environment_rejects_inconsistent_risk_free_valuation_date() -> None:
    with pytest.raises(ValueError, match="risk-free"):
        MarketEnvironment(
            valuation_date=VALUATION_DATE,
            spot=100.0,
            risk_free_discounting=make_curve(
                valuation_date=date(2026, 1, 2)
            ),
            dividend_discounting=make_curve(),
        )


def test_market_environment_rejects_inconsistent_dividend_valuation_date() -> None:
    with pytest.raises(ValueError, match="dividend"):
        MarketEnvironment(
            valuation_date=VALUATION_DATE,
            spot=100.0,
            risk_free_discounting=make_curve(),
            dividend_discounting=make_curve(
                valuation_date=date(2026, 1, 2)
            ),
        )


def test_market_environment_requires_discount_factor_provider() -> None:
    invalid = cast(DiscountFactorProvider, object())

    with pytest.raises(TypeError, match="risk_free_discounting"):
        MarketEnvironment(
            valuation_date=VALUATION_DATE,
            spot=100.0,
            risk_free_discounting=invalid,
            dividend_discounting=make_curve(),
        )
