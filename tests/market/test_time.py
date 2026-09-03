from datetime import date, datetime
from typing import cast

import pytest

from qf_platform.market import actual_365_fixed_year_fraction


def test_actual_365_fixed_one_non_leap_year_is_one() -> None:
    assert actual_365_fixed_year_fraction(
        date(2026, 1, 1),
        date(2027, 1, 1),
    ) == pytest.approx(1.0, abs=0.0)


def test_actual_365_fixed_does_not_switch_denominator_in_leap_year() -> None:
    year_fraction = actual_365_fixed_year_fraction(
        date(2028, 1, 1),
        date(2029, 1, 1),
    )

    assert year_fraction == pytest.approx(366.0 / 365.0, rel=0.0, abs=1e-15)
    assert year_fraction != pytest.approx(1.0, rel=0.0, abs=1e-12)


def test_actual_365_fixed_rejects_reversed_dates() -> None:
    with pytest.raises(ValueError):
        actual_365_fixed_year_fraction(date(2027, 1, 2), date(2027, 1, 1))


def test_actual_365_fixed_rejects_datetime() -> None:
    with pytest.raises(TypeError):
        actual_365_fixed_year_fraction(
            cast(date, datetime(2027, 1, 1, 12, 0)),
            date(2027, 1, 2),
        )
