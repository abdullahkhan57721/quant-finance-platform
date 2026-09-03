import math
from datetime import date, datetime
from typing import cast

import pytest

from qf_platform.market import FlatContinuousDiscountCurve


VALUATION_DATE = date(2026, 1, 1)
ONE_YEAR = date(2027, 1, 1)


def test_flat_continuous_discount_curve_uses_continuous_compounding() -> None:
    curve = FlatContinuousDiscountCurve(
        valuation_date=VALUATION_DATE,
        continuously_compounded_rate=0.05,
    )

    factor = curve.discount_factor(ONE_YEAR)

    assert factor == pytest.approx(math.exp(-0.05), rel=0.0, abs=1e-15)
    assert factor != pytest.approx(1.0 / 1.05, rel=0.0, abs=1e-6)


def test_flat_continuous_discount_curve_supports_negative_rates() -> None:
    curve = FlatContinuousDiscountCurve(
        valuation_date=VALUATION_DATE,
        continuously_compounded_rate=-0.01,
    )

    assert curve.discount_factor(ONE_YEAR) == pytest.approx(
        math.exp(0.01),
        rel=0.0,
        abs=1e-15,
    )


def test_discount_factor_at_valuation_date_is_one() -> None:
    curve = FlatContinuousDiscountCurve(
        valuation_date=VALUATION_DATE,
        continuously_compounded_rate=0.25,
    )

    assert curve.discount_factor(VALUATION_DATE) == 1.0


@pytest.mark.parametrize("rate", [float("inf"), float("-inf"), float("nan")])
def test_flat_continuous_discount_curve_rejects_nonfinite_rate(rate: float) -> None:
    with pytest.raises(ValueError):
        FlatContinuousDiscountCurve(
            valuation_date=VALUATION_DATE,
            continuously_compounded_rate=rate,
        )


def test_flat_continuous_discount_curve_rejects_datetime_valuation_date() -> None:
    with pytest.raises(TypeError):
        FlatContinuousDiscountCurve(
            valuation_date=cast(date, datetime(2026, 1, 1, 12, 0)),
            continuously_compounded_rate=0.05,
        )


def test_flat_continuous_discount_curve_rejects_past_maturity() -> None:
    curve = FlatContinuousDiscountCurve(
        valuation_date=VALUATION_DATE,
        continuously_compounded_rate=0.05,
    )

    with pytest.raises(ValueError):
        curve.discount_factor(date(2025, 12, 31))
