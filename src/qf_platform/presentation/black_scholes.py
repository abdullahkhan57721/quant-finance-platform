"""Renderer-neutral presentation for the concrete M1 Black-Scholes study."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import exp

from qf_platform.application.black_scholes_study import BlackScholesStudyComposition
from qf_platform.pricing import (
    EquityState,
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    OptionRight,
    StatePath,
    ValuationResult,
    actual_365_fixed_year_fraction,
    validated_numeraire_value,
)


@dataclass(frozen=True, slots=True)
class PresentationRow:
    """One deliberately small labeled value for inspector/evidence presentation."""

    label: str
    value: str
    detail: str = ""
    status: str = ""


@dataclass(frozen=True, slots=True)
class PayoffPoint:
    """One renderer-neutral terminal payoff sample."""

    underlying: float
    payoff: float


@dataclass(frozen=True, slots=True)
class BlackScholesPresentation:
    """Concrete UI1 presentation data; not a universal visualization grammar."""

    inspector_rows: tuple[PresentationRow, ...]
    evidence_rows: tuple[PresentationRow, ...]
    payoff_points: tuple[PayoffPoint, ...]


@dataclass(frozen=True, slots=True)
class _StaticEquityPath(StatePath[date, EquityState]):
    state: EquityState

    def value_at(self, time: date, /) -> EquityState:
        del time
        return self.state


def build_black_scholes_presentation(
    composition: BlackScholesStudyComposition,
    result: ValuationResult | None = None,
) -> BlackScholesPresentation:
    """Prepare display-only values from the normalized M1 problem and result."""
    problem = composition.problem
    contract = problem.contract
    numeraire = problem.numeraire
    if not isinstance(contract, EuropeanOption):
        raise TypeError("UI1 presentation requires an M1 EuropeanOption")
    if not isinstance(numeraire, FlatMoneyMarketNumeraire):
        raise TypeError("UI1 presentation requires an M1 money-market numeraire")

    parameters = problem.parameters
    valuation_date = problem.valuation_time
    year_fraction = actual_365_fixed_year_fraction(valuation_date, contract.expiry)
    right_name = "Call" if contract.right is OptionRight.CALL else "Put"
    support = composition.method_supported

    inspector_rows = (
        PresentationRow(
            "State",
            f"Spot = {problem.current_state.value.spot:g}",
            "Valuation-ready modeled equity state; not an observed quote container.",
        ),
        PresentationRow(
            "Stochastic law",
            "Black-Scholes / geometric Brownian motion",
            "Law identity is separate from its parameter values and valuation method.",
        ),
        PresentationRow(
            "Parameters",
            (
                f"vol = {parameters.annualized_volatility:g}; "
                f"carry = {parameters.continuous_dividend_yield:g}"
            ),
            "Annualized decimal volatility and continuous proportional carry.",
        ),
        PresentationRow(
            "Contract / payoff",
            f"European {right_name}; K = {contract.strike:g}; E = {contract.expiry}",
            "The contract owns terminal cash-flow semantics independently of valuation.",
        ),
        PresentationRow(
            "Numeraire",
            f"Money market; r = {numeraire.continuously_compounded_rate:g}",
            "Flat continuously compounded annualized decimal rate; negative rates allowed.",
        ),
        PresentationRow(
            "Pricing measure",
            problem.pricing_measure.name,
            "Numeraire-associated money-market pricing semantics.",
        ),
        PresentationRow(
            "Pricing problem",
            f"Present value at {valuation_date}; T = {year_fraction:.8g}",
            "M1 PricingProblem composes state, law, parameters, contract, numeraire, and Q.",
        ),
        PresentationRow(
            "Valuation method",
            "Black-Scholes analytic",
            "Method capability is checked in Python, not inferred by QML.",
            "Supported" if support else "Unsupported",
        ),
        PresentationRow(
            "Assumptions / conventions",
            "ACT/365F · continuous compounding · continuous carry",
            "Calendar dates; no business-day or time-of-day semantics in M1.",
        ),
        PresentationRow(
            "Validation status",
            "M1 reference evidence available",
            "Benchmark, parity, bounds, limiting cases, and convention-discriminating tests.",
            "Validated reference" if support else "Not runnable",
        ),
    )

    evidence_rows = list(_compatibility_rows(support))
    if result is not None:
        evidence_rows.append(_no_arbitrage_bound_row(composition, result))
        evidence_rows.append(
            PresentationRow(
                "Authoritative valuation result",
                f"PV = {result.present_value:.12g}",
                "Displayed directly from immutable M1 ValuationResult.present_value.",
                "Complete",
            )
        )

    return BlackScholesPresentation(
        inspector_rows=inspector_rows,
        evidence_rows=tuple(evidence_rows),
        payoff_points=_payoff_points(
            contract,
            current_spot=problem.current_state.value.spot,
        ),
    )


def _compatibility_rows(supported: bool) -> tuple[PresentationRow, ...]:
    return (
        PresentationRow(
            "Mathematically meaningful",
            "M1 pricing composition constructed",
            "Structural financial semantics are represented by typed production objects.",
            "Ready",
        ),
        PresentationRow(
            "Implemented",
            "European option + Black-Scholes analytic",
            "UI1 exposes only capabilities already implemented on merged main.",
            "Available",
        ),
        PresentationRow(
            "Selected method support",
            "Black-Scholes analytic",
            "Implementation capability is distinct from structural validity.",
            "Supported" if supported else "Unsupported",
        ),
        PresentationRow(
            "Validated",
            "M1 reference suite",
            "Published benchmark, put-call parity, arbitrage bounds, and limiting cases.",
            "Reference evidence",
        ),
        PresentationRow(
            "Workbench exposed",
            "UI1 Black-Scholes vertical",
            "Exposure is a product decision, not a statement of mathematical universality.",
            "Exposed",
        ),
    )


def _payoff_points(
    contract: EuropeanOption,
    *,
    current_spot: float,
    sample_count: int = 41,
) -> tuple[PayoffPoint, ...]:
    upper = max(2.0 * contract.strike, 2.0 * current_spot, 1.0)
    points: list[PayoffPoint] = []
    for index in range(sample_count):
        underlying = upper * index / (sample_count - 1)
        path = _StaticEquityPath(EquityState(underlying))
        stream = contract.cash_flows(path)
        points.append(PayoffPoint(underlying, stream.cash_flows[0].amount))
    return tuple(points)


def _no_arbitrage_bound_row(
    composition: BlackScholesStudyComposition,
    result: ValuationResult,
) -> PresentationRow:
    problem = composition.problem
    contract = problem.contract
    numeraire = problem.numeraire
    if not isinstance(contract, EuropeanOption):
        raise TypeError("UI1 bound evidence requires an M1 EuropeanOption")
    if not isinstance(numeraire, FlatMoneyMarketNumeraire):
        raise TypeError("UI1 bound evidence requires an M1 money-market numeraire")

    valuation_date = problem.valuation_time
    expiry = contract.expiry
    year_fraction = actual_365_fixed_year_fraction(valuation_date, expiry)
    risk_free_discount = validated_numeraire_value(
        numeraire, valuation_date
    ) / validated_numeraire_value(numeraire, expiry)
    dividend_discount = exp(
        -problem.parameters.continuous_dividend_yield * year_fraction
    )
    discounted_spot = problem.current_state.value.spot * dividend_discount
    discounted_strike = contract.strike * risk_free_discount
    if contract.right is OptionRight.CALL:
        lower = max(discounted_spot - discounted_strike, 0.0)
        upper = discounted_spot
    else:
        lower = max(discounted_strike - discounted_spot, 0.0)
        upper = discounted_strike
    present_value = result.present_value
    passed = lower <= present_value <= upper
    return PresentationRow(
        "Discounted no-arbitrage bounds",
        f"{lower:.8g} ≤ {present_value:.8g} ≤ {upper:.8g}",
        "Bounds are derived in Python from the same normalized M1 numeraire/carry semantics.",
        "Pass" if passed else "Fail",
    )
