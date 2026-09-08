from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass
from datetime import date, datetime
from math import exp
from typing import cast

import pytest

from qf_platform.pricing.black_scholes import BlackScholesLaw, BlackScholesParameters
from qf_platform.pricing.black_scholes_valuation import BlackScholesClosedForm
from qf_platform.pricing.cashflows import CashFlow, CashFlowStream
from qf_platform.pricing.dates import actual_365_fixed_year_fraction
from qf_platform.pricing.equity import (
    EquityState,
    EquityStateSpace,
    EuropeanOption,
    OptionRight,
)
from qf_platform.pricing.measures import PricingMeasureSemantics
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState, StatePath
from qf_platform.pricing.valuation import UnsupportedPricingProblem, evaluate

VALUATION_DATE = date(2026, 1, 1)
ONE_YEAR = date(2027, 1, 1)
ANALYTIC_ABS_TOL = 2e-13


@dataclass(frozen=True, slots=True)
class StaticEquityPath:
    state: EquityState

    def value_at(self, time: date, /) -> EquityState:
        del time
        return self.state


@dataclass(frozen=True, slots=True)
class FixedPaymentContract:
    expiry: date

    def cash_flows(
        self,
        path: StatePath[date, EquityState],
        /,
    ) -> CashFlowStream[date]:
        del path
        return CashFlowStream((CashFlow(self.expiry, 1.0),))


def make_problem(
    right: OptionRight,
    *,
    spot: float = 100.0,
    strike: float = 100.0,
    rate: float = 0.05,
    dividend_yield: float = 0.0,
    volatility: float = 0.20,
    valuation_date: date = VALUATION_DATE,
    expiry: date = ONE_YEAR,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    state_space = EquityStateSpace()
    law = BlackScholesLaw(state_space=state_space)
    parameters = BlackScholesParameters(
        annualized_volatility=volatility,
        continuous_dividend_yield=dividend_yield,
    )
    current_state = ModeledState(
        time=valuation_date,
        value=EquityState(spot=spot),
        state_space=state_space,
    )
    contract = EuropeanOption(expiry=expiry, strike=strike, right=right)
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=valuation_date,
        continuously_compounded_rate=rate,
    )
    pricing_measure = PricingMeasureSemantics(name="Q^B", numeraire=numeraire)
    return PricingProblem(
        current_state=current_state,
        stochastic_law=law,
        parameters=parameters,
        contract=contract,
        numeraire=numeraire,
        pricing_measure=pricing_measure,
    )


def value(
    right: OptionRight,
    *,
    spot: float = 100.0,
    strike: float = 100.0,
    rate: float = 0.05,
    dividend_yield: float = 0.0,
    volatility: float = 0.20,
    valuation_date: date = VALUATION_DATE,
    expiry: date = ONE_YEAR,
) -> float:
    problem = make_problem(
        right,
        spot=spot,
        strike=strike,
        rate=rate,
        dividend_yield=dividend_yield,
        volatility=volatility,
        valuation_date=valuation_date,
        expiry=expiry,
    )
    return evaluate(problem, BlackScholesClosedForm()).present_value


def test_equity_state_contract_and_parameters_are_immutable_value_objects() -> None:
    state = EquityState(100)
    option = EuropeanOption(ONE_YEAR, 100, OptionRight.CALL)
    parameters = BlackScholesParameters(0.20, 0.01)

    assert state.spot == 100.0
    assert option.strike == 100.0
    assert parameters.annualized_volatility == 0.20
    assert parameters.continuous_dividend_yield == 0.01

    with pytest.raises(FrozenInstanceError):
        state.spot = 101.0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        option.strike = 101.0  # type: ignore[misc]


@pytest.mark.parametrize("spot", [-1.0, float("inf"), float("nan")])
def test_equity_state_rejects_invalid_spot(spot: float) -> None:
    with pytest.raises(ValueError):
        EquityState(spot)


@pytest.mark.parametrize("strike", [-1.0, float("inf"), float("nan")])
def test_european_option_rejects_invalid_strike(strike: float) -> None:
    with pytest.raises(ValueError):
        EuropeanOption(ONE_YEAR, strike, OptionRight.CALL)


def test_european_option_requires_calendar_date_and_explicit_right() -> None:
    with pytest.raises(TypeError):
        EuropeanOption(
            cast(date, datetime(2027, 1, 1, 12)),
            100.0,
            OptionRight.CALL,
        )
    with pytest.raises(TypeError):
        EuropeanOption(ONE_YEAR, 100.0, cast(OptionRight, "call"))


@pytest.mark.parametrize("volatility", [-0.01, float("inf"), float("nan")])
def test_black_scholes_parameters_reject_invalid_volatility(volatility: float) -> None:
    with pytest.raises(ValueError):
        BlackScholesParameters(volatility)


def test_european_option_emits_terminal_cash_flow_independently_of_valuation() -> None:
    call = EuropeanOption(ONE_YEAR, 100.0, OptionRight.CALL)
    put = EuropeanOption(ONE_YEAR, 100.0, OptionRight.PUT)

    call_flows = call.cash_flows(StaticEquityPath(EquityState(125.0)))
    put_flows = put.cash_flows(StaticEquityPath(EquityState(75.0)))

    assert len(call_flows) == 1
    assert call_flows.cash_flows[0].payment_time == ONE_YEAR
    assert call_flows.cash_flows[0].amount == 25.0
    assert put_flows.cash_flows[0].amount == 25.0


def test_actual_365_fixed_counts_leap_day_with_fixed_denominator() -> None:
    start = date(2024, 1, 1)
    end = date(2025, 1, 1)

    assert actual_365_fixed_year_fraction(start, end) == 366 / 365
    assert actual_365_fixed_year_fraction(end, start) == -366 / 365


def test_flat_money_market_numeraire_uses_continuous_compounding() -> None:
    numeraire = FlatMoneyMarketNumeraire(VALUATION_DATE, 0.05)

    assert numeraire.value_at(VALUATION_DATE) == 1.0
    assert numeraire.value_at(ONE_YEAR) == pytest.approx(exp(0.05))
    assert numeraire.value_at(ONE_YEAR) != pytest.approx(1.05, abs=1e-6)


def test_flat_money_market_numeraire_allows_negative_rates() -> None:
    numeraire = FlatMoneyMarketNumeraire(VALUATION_DATE, -0.02)

    assert numeraire.value_at(ONE_YEAR) == pytest.approx(exp(-0.02))
    assert numeraire.value_at(ONE_YEAR) > 0.0


def test_reference_benchmark_call_and_put_values() -> None:
    assert value(OptionRight.CALL) == pytest.approx(
        10.450583572185565,
        rel=0.0,
        abs=ANALYTIC_ABS_TOL,
    )
    assert value(OptionRight.PUT) == pytest.approx(
        5.573526022256971,
        rel=0.0,
        abs=ANALYTIC_ABS_TOL,
    )


@pytest.mark.parametrize(
    ("spot", "strike", "rate", "dividend_yield", "volatility"),
    [
        (100.0, 100.0, 0.05, 0.00, 0.20),
        (120.0, 95.0, 0.03, 0.02, 0.35),
        (70.0, 100.0, -0.01, 0.04, 0.50),
    ],
)
def test_put_call_parity(
    spot: float,
    strike: float,
    rate: float,
    dividend_yield: float,
    volatility: float,
) -> None:
    call = value(
        OptionRight.CALL,
        spot=spot,
        strike=strike,
        rate=rate,
        dividend_yield=dividend_yield,
        volatility=volatility,
    )
    put = value(
        OptionRight.PUT,
        spot=spot,
        strike=strike,
        rate=rate,
        dividend_yield=dividend_yield,
        volatility=volatility,
    )
    parity_rhs = spot * exp(-dividend_yield) - strike * exp(-rate)

    assert call - put == pytest.approx(
        parity_rhs,
        rel=0.0,
        abs=ANALYTIC_ABS_TOL,
    )


@pytest.mark.parametrize("right", [OptionRight.CALL, OptionRight.PUT])
def test_discounted_no_arbitrage_bounds(right: OptionRight) -> None:
    spot = 110.0
    strike = 95.0
    rate = -0.01
    dividend_yield = 0.03
    present_value = value(
        right,
        spot=spot,
        strike=strike,
        rate=rate,
        dividend_yield=dividend_yield,
        volatility=0.30,
    )
    discounted_spot = spot * exp(-dividend_yield)
    discounted_strike = strike * exp(-rate)

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
    assert (
        value(
            right,
            spot=spot,
            strike=strike,
            expiry=VALUATION_DATE,
            volatility=0.9,
        )
        == expected
    )


def test_zero_volatility_returns_discounted_deterministic_intrinsic() -> None:
    discounted_spot = 100.0 * exp(-0.02)
    discounted_strike = 95.0 * exp(-0.05)
    signed = discounted_spot - discounted_strike

    assert value(
        OptionRight.CALL,
        strike=95.0,
        dividend_yield=0.02,
        volatility=0.0,
    ) == pytest.approx(max(signed, 0.0), abs=ANALYTIC_ABS_TOL)
    assert value(
        OptionRight.PUT,
        strike=95.0,
        dividend_yield=0.02,
        volatility=0.0,
    ) == pytest.approx(max(-signed, 0.0), abs=ANALYTIC_ABS_TOL)


def test_zero_spot_and_zero_strike_limits() -> None:
    assert (
        value(
            OptionRight.CALL,
            spot=0.0,
            dividend_yield=0.02,
            volatility=0.30,
        )
        == 0.0
    )
    assert value(
        OptionRight.PUT,
        spot=0.0,
        volatility=0.30,
    ) == pytest.approx(100.0 * exp(-0.05), abs=ANALYTIC_ABS_TOL)

    assert value(
        OptionRight.CALL,
        strike=0.0,
        dividend_yield=0.02,
        volatility=0.30,
    ) == pytest.approx(100.0 * exp(-0.02), abs=ANALYTIC_ABS_TOL)
    assert value(OptionRight.PUT, strike=0.0, volatility=0.30) == 0.0


def test_positive_dividend_yield_reduces_call_value() -> None:
    no_dividend = value(OptionRight.CALL, dividend_yield=0.0)
    positive_dividend = value(OptionRight.CALL, dividend_yield=0.04)

    assert positive_dividend < no_dividend


def test_negative_interest_rate_is_supported_by_closed_form() -> None:
    assert value(OptionRight.PUT, rate=-0.02, volatility=0.25) > 0.0


def test_expiry_before_valuation_is_unsupported_by_method() -> None:
    problem = make_problem(
        OptionRight.CALL,
        valuation_date=date(2027, 1, 2),
        expiry=ONE_YEAR,
    )

    with pytest.raises(UnsupportedPricingProblem, match="does not support"):
        evaluate(problem, BlackScholesClosedForm())


def test_closed_form_rejects_non_european_contract_through_support_boundary() -> None:
    problem = make_problem(OptionRight.CALL)
    incompatible = PricingProblem[date, EquityState, BlackScholesParameters](
        current_state=problem.current_state,
        stochastic_law=problem.stochastic_law,
        parameters=problem.parameters,
        contract=FixedPaymentContract(ONE_YEAR),
        numeraire=problem.numeraire,
        pricing_measure=problem.pricing_measure,
    )

    with pytest.raises(UnsupportedPricingProblem, match="does not support"):
        evaluate(incompatible, BlackScholesClosedForm())
