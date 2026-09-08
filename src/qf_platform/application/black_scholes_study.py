"""Concrete frontend-neutral composition for the M1 Black-Scholes study."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from qf_platform.pricing import (
    BlackScholesClosedForm,
    BlackScholesLaw,
    BlackScholesParameters,
    EquityState,
    EquityStateSpace,
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
)


@dataclass(frozen=True, slots=True)
class BlackScholesStudyDraft:
    """Transient text inputs before they become authoritative M1 values.

    Strings are intentional: an interactive frontend must be able to represent a
    temporarily incomplete or invalid edit without making that edit financial state.
    """

    spot: str
    strike: str
    valuation_date: str
    expiry: str
    annualized_volatility: str
    continuously_compounded_rate: str
    continuous_dividend_yield: str
    option_right: str


@dataclass(frozen=True, slots=True)
class BlackScholesStudyComposition:
    """One normalized M1 pricing question plus the selected concrete method."""

    problem: PricingProblem[date, EquityState, BlackScholesParameters]
    method: BlackScholesClosedForm

    @property
    def method_supported(self) -> bool:
        """Report implementation support separately from structural composition."""
        return self.method.supports(self.problem)


def canonical_black_scholes_draft() -> BlackScholesStudyDraft:
    """Return the published M1 benchmark as the first guided-study example."""
    return BlackScholesStudyDraft(
        spot="100",
        strike="100",
        valuation_date="2026-01-01",
        expiry="2027-01-01",
        annualized_volatility="0.20",
        continuously_compounded_rate="0.05",
        continuous_dividend_yield="0.00",
        option_right="call",
    )


def compose_black_scholes_study(
    draft: BlackScholesStudyDraft,
) -> BlackScholesStudyComposition:
    """Normalize transient inputs into the exact merged M1 quantitative semantics."""
    valuation_date = _parse_date(draft.valuation_date, name="valuation date")
    expiry = _parse_date(draft.expiry, name="expiry")
    spot = _parse_float(draft.spot, name="spot")
    strike = _parse_float(draft.strike, name="strike")
    volatility = _parse_float(
        draft.annualized_volatility,
        name="annualized volatility",
    )
    rate = _parse_float(
        draft.continuously_compounded_rate,
        name="continuously compounded rate",
    )
    dividend_yield = _parse_float(
        draft.continuous_dividend_yield,
        name="continuous dividend/carry yield",
    )
    try:
        right = OptionRight(draft.option_right.strip().lower())
    except ValueError as exc:
        msg = "option right must be 'call' or 'put'"
        raise ValueError(msg) from exc

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
    problem = PricingProblem(
        current_state=current_state,
        stochastic_law=law,
        parameters=parameters,
        contract=contract,
        numeraire=numeraire,
        pricing_measure=pricing_measure,
    )
    return BlackScholesStudyComposition(
        problem=problem,
        method=BlackScholesClosedForm(),
    )


def _parse_float(value: str, *, name: str) -> float:
    if type(value) is not str or not value.strip():
        msg = f"{name} is required"
        raise ValueError(msg)
    try:
        return float(value)
    except ValueError as exc:
        msg = f"{name} must be a number"
        raise ValueError(msg) from exc


def _parse_date(value: str, *, name: str) -> date:
    if type(value) is not str or not value.strip():
        msg = f"{name} is required"
        raise ValueError(msg)
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        msg = f"{name} must use YYYY-MM-DD"
        raise ValueError(msg) from exc
