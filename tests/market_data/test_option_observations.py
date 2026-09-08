from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from qf_platform.market_data import (
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    QuoteNormalizationError,
    RawOptionQuote,
    RawUnderlyingObservation,
    normalize_european_option_midpoint,
)
from qf_platform.pricing import OptionRight

_MARKET_DATE = date(2026, 1, 2)
_RETRIEVED_AT = datetime(2026, 1, 3, 12, tzinfo=UTC)


def _provenance(*, market_date: date = _MARKET_DATE) -> ObservationProvenance:
    return ObservationProvenance(
        provider="synthetic:test",
        source="unit fixture",
        market_date=market_date,
        retrieved_at=_RETRIEVED_AT,
        raw_artifact_sha256="a" * 64,
        license_notes="synthetic fixture; unrestricted test use",
    )


def _quote(**overrides: object) -> RawOptionQuote:
    values: dict[str, object] = {
        "contract_id": "SYN-C-100",
        "underlying_id": "SYN",
        "expiry": date(2026, 7, 1),
        "strike": 100.0,
        "right": OptionRight.CALL,
        "exercise_style": OptionExerciseStyle.EUROPEAN,
        "provenance": _provenance(),
        "bid": 4.0,
        "ask": 4.2,
        "last": 4.1,
        "volume": 20,
        "open_interest": 100,
        "settlement_time": OptionSettlementTime.PM,
    }
    values.update(overrides)
    return RawOptionQuote(**values)  # type: ignore[arg-type]


def _underlying(**overrides: object) -> RawUnderlyingObservation:
    values: dict[str, object] = {
        "underlying_id": "SYN",
        "value": 100.0,
        "provenance": _provenance(),
    }
    values.update(overrides)
    return RawUnderlyingObservation(**values)  # type: ignore[arg-type]


def test_raw_quote_preserves_bad_observed_prices_for_later_normalization() -> None:
    quote = _quote(bid=-1.0, ask=-2.0)

    assert quote.bid == -1.0
    assert quote.ask == -2.0


def test_provenance_requires_timezone_aware_retrieval_time() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ObservationProvenance(
            provider="synthetic:test",
            source="unit fixture",
            market_date=_MARKET_DATE,
            retrieved_at=datetime(2026, 1, 3, 12),
        )


def test_provenance_rejects_observation_after_retrieval() -> None:
    with pytest.raises(ValueError, match="later than retrieved_at"):
        ObservationProvenance(
            provider="synthetic:test",
            source="unit fixture",
            market_date=_MARKET_DATE,
            retrieved_at=_RETRIEVED_AT,
            observed_at=_RETRIEVED_AT + timedelta(seconds=1),
        )


def test_midpoint_normalization_retains_raw_lineage() -> None:
    quote = _quote()
    underlying = _underlying()

    normalized = normalize_european_option_midpoint(quote, underlying)

    assert normalized.raw_quote is quote
    assert normalized.raw_underlying is underlying
    assert normalized.target_price == pytest.approx(4.1)
    assert normalized.spot == 100.0
    assert normalized.valuation_date == _MARKET_DATE
    assert normalized.normalization_version == "m4-midpoint-v1"


@pytest.mark.parametrize(
    ("quote", "underlying", "message"),
    [
        (_quote(bid=None), _underlying(), "requires both bid and ask"),
        (_quote(bid=0.0), _underlying(), "requires positive bid and ask"),
        (_quote(bid=4.3, ask=4.2), _underlying(), "crossed option quote"),
        (
            _quote(exercise_style=OptionExerciseStyle.AMERICAN),
            _underlying(),
            "supports European exercise only",
        ),
        (
            _quote(settlement_time=OptionSettlementTime.AM),
            _underlying(),
            "AM-settled contracts",
        ),
        (
            _quote(underlying_id="OTHER"),
            _underlying(),
            "same underlying",
        ),
        (
            _quote(),
            _underlying(provenance=_provenance(market_date=date(2026, 1, 3))),
            "share one market date",
        ),
        (_quote(), _underlying(value=0.0), "underlying level must be positive"),
    ],
)
def test_midpoint_normalization_rejects_non_problem_ready_observations(
    quote: RawOptionQuote,
    underlying: RawUnderlyingObservation,
    message: str,
) -> None:
    with pytest.raises(QuoteNormalizationError, match=message):
        normalize_european_option_midpoint(quote, underlying)
