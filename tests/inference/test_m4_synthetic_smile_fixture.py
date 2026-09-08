from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import TypedDict, cast

import pytest

from qf_platform.inference import (
    BisectionImpliedVolatility,
    BlackScholesImpliedVolatilityProblem,
    infer_implied_volatility,
)
from qf_platform.market_data import (
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    RawOptionQuote,
    RawUnderlyingObservation,
    normalize_european_option_midpoint,
)
from qf_platform.pricing import (
    FlatMoneyMarketNumeraire,
    OptionRight,
    PricingMeasureSemantics,
)


class _FixtureRow(TypedDict):
    contract_id: str
    expiry: str
    strike: float
    right: str
    bid: float
    ask: float
    expected_implied_volatility: float


class _Fixture(TypedDict):
    provider: str
    source: str
    market_date: str
    spot: float
    continuously_compounded_rate: float
    continuous_dividend_yield: float
    rows: list[_FixtureRow]


def _load_fixture() -> _Fixture:
    path = Path(__file__).parents[1] / "fixtures" / "m4_synthetic_option_quotes.json"
    return cast(_Fixture, json.loads(path.read_text(encoding="utf-8")))


def test_synthetic_fixture_reproduces_deliberate_strike_and_maturity_structure() -> (
    None
):
    fixture = _load_fixture()
    market_date = date.fromisoformat(fixture["market_date"])
    retrieved_at = datetime(2026, 1, 3, 12, tzinfo=UTC)
    provenance = ObservationProvenance(
        provider=fixture["provider"],
        source=fixture["source"],
        market_date=market_date,
        retrieved_at=retrieved_at,
        raw_artifact_sha256="c" * 64,
        license_notes="synthetic fixture; unrestricted test use",
    )
    underlying = RawUnderlyingObservation(
        underlying_id="SYN",
        value=fixture["spot"],
        provenance=provenance,
    )
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=market_date,
        continuously_compounded_rate=fixture["continuously_compounded_rate"],
    )
    measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
    inferred: dict[tuple[str, float], float] = {}

    for row in fixture["rows"]:
        quote = RawOptionQuote(
            contract_id=row["contract_id"],
            underlying_id="SYN",
            expiry=date.fromisoformat(row["expiry"]),
            strike=row["strike"],
            right=OptionRight(row["right"]),
            exercise_style=OptionExerciseStyle.EUROPEAN,
            provenance=provenance,
            bid=row["bid"],
            ask=row["ask"],
            settlement_time=OptionSettlementTime.PM,
        )
        observation = normalize_european_option_midpoint(quote, underlying)
        problem = BlackScholesImpliedVolatilityProblem(
            observation=observation,
            numeraire=numeraire,
            pricing_measure=measure,
            continuous_dividend_yield=fixture["continuous_dividend_yield"],
        )
        result = infer_implied_volatility(problem, BisectionImpliedVolatility())
        inferred[(row["expiry"], row["strike"])] = result.annualized_volatility
        assert result.annualized_volatility == pytest.approx(
            row["expected_implied_volatility"],
            abs=1.0e-8,
        )

    assert inferred[("2026-04-02", 80.0)] > inferred[("2026-04-02", 120.0)]
    assert inferred[("2026-07-01", 80.0)] > inferred[("2026-07-01", 120.0)]
    assert inferred[("2026-04-02", 100.0)] != pytest.approx(
        inferred[("2026-07-01", 100.0)]
    )
