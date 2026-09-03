from dataclasses import FrozenInstanceError

import pytest

from qf_platform.models import BlackScholesParameters


def test_black_scholes_parameters_normalize_volatility_and_are_immutable() -> None:
    parameters = BlackScholesParameters(annualized_volatility=0.20)

    assert parameters.annualized_volatility == 0.20
    with pytest.raises(FrozenInstanceError):
        setattr(parameters, "annualized_volatility", 0.25)


@pytest.mark.parametrize(
    "volatility",
    [-0.01, float("inf"), float("nan")],
)
def test_black_scholes_parameters_reject_invalid_volatility(
    volatility: float,
) -> None:
    with pytest.raises(ValueError):
        BlackScholesParameters(annualized_volatility=volatility)


def test_black_scholes_parameters_allow_zero_volatility_limit() -> None:
    parameters = BlackScholesParameters(annualized_volatility=0.0)

    assert parameters.annualized_volatility == 0.0
