from dataclasses import FrozenInstanceError
from datetime import date, datetime
from typing import cast

import pytest

from qf_platform.instruments import EuropeanOption, OptionRight


def test_european_option_normalizes_numeric_strike_and_is_immutable() -> None:
    option = EuropeanOption(
        expiry=date(2027, 1, 1),
        strike=100,
        right=OptionRight.CALL,
    )

    assert option.strike == 100.0
    assert isinstance(option.strike, float)
    attribute = "strike"
    with pytest.raises(FrozenInstanceError):
        setattr(option, attribute, 101.0)


@pytest.mark.parametrize("strike", [-1.0, float("inf"), float("nan")])
def test_european_option_rejects_invalid_strike(strike: float) -> None:
    with pytest.raises(ValueError):
        EuropeanOption(
            expiry=date(2027, 1, 1),
            strike=strike,
            right=OptionRight.CALL,
        )


def test_european_option_rejects_bool_strike() -> None:
    with pytest.raises(TypeError):
        EuropeanOption(
            expiry=date(2027, 1, 1),
            strike=cast(float, True),
            right=OptionRight.CALL,
        )


def test_european_option_requires_calendar_date_not_datetime() -> None:
    with pytest.raises(TypeError):
        EuropeanOption(
            expiry=cast(date, datetime(2027, 1, 1, 12, 0)),
            strike=100.0,
            right=OptionRight.CALL,
        )


def test_european_option_requires_explicit_option_right() -> None:
    with pytest.raises(TypeError):
        EuropeanOption(
            expiry=date(2027, 1, 1),
            strike=100.0,
            right=cast(OptionRight, "call"),
        )
