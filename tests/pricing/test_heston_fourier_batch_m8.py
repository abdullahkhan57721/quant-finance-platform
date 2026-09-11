from __future__ import annotations

from datetime import date

import pytest

from qf_platform.pricing import (
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    HestonEquityState,
    HestonFourierEuropeanOption,
    HestonLaw,
    HestonParameters,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
    evaluate,
)
from qf_platform.pricing.heston_fourier_batch import (
    batch_heston_fourier_present_values,
)

_VALUATION_DATE = date(2026, 1, 1)


def _problem(
    *,
    expiry: date,
    strike: float,
    right: OptionRight,
) -> PricingProblem[date, HestonEquityState, HestonParameters]:
    law = HestonLaw()
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=0.03,
    )
    measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
    return PricingProblem(
        current_state=ModeledState(
            time=_VALUATION_DATE,
            value=HestonEquityState(spot=100.0, instantaneous_variance=0.04),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=HestonParameters(
            mean_reversion_speed=2.0,
            long_run_variance=0.04,
            volatility_of_variance=0.5,
            correlation=-0.7,
            continuous_dividend_yield=0.01,
        ),
        contract=EuropeanOption(expiry=expiry, strike=strike, right=right),
        numeraire=numeraire,
        pricing_measure=measure,
    )


def test_batch_heston_fourier_matches_scalar_reference_across_strikes_expiries() -> (
    None
):
    method = HestonFourierEuropeanOption(
        integration_upper_bound=100.0,
        intervals=256,
    )
    problems = (
        _problem(expiry=date(2026, 7, 1), strike=85.0, right=OptionRight.PUT),
        _problem(expiry=date(2026, 7, 1), strike=100.0, right=OptionRight.CALL),
        _problem(expiry=date(2026, 7, 1), strike=115.0, right=OptionRight.CALL),
        _problem(expiry=date(2027, 1, 1), strike=90.0, right=OptionRight.PUT),
        _problem(expiry=date(2027, 1, 1), strike=110.0, right=OptionRight.CALL),
    )

    batched = batch_heston_fourier_present_values(problems, method)
    scalar = tuple(evaluate(problem, method).present_value for problem in problems)

    assert batched == pytest.approx(scalar, abs=2.0e-11)
