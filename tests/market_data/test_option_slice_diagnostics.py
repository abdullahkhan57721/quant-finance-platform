from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from qf_platform.market_data import (
    IncomparableOptionSlice,
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    RawOptionQuote,
    RawUnderlyingObservation,
    diagnose_option_strike_slice,
    normalize_european_option_midpoint,
)
from qf_platform.pricing import OptionRight

_VALUATION_DATE = date(2026, 1, 2)
_EXPIRY = date(2026, 7, 2)
_PROVENANCE = ObservationProvenance(
    provider="synthetic:test",
    source="static diagnostic unit fixture",
    market_date=_VALUATION_DATE,
    retrieved_at=datetime(2026, 1, 3, 12, tzinfo=UTC),
    raw_artifact_sha256="d" * 64,
    license_notes="synthetic fixture; unrestricted test use",
)
_UNDERLYING = RawUnderlyingObservation(
    underlying_id="SYN",
    value=100.0,
    provenance=_PROVENANCE,
)


def _observation(
    strike: float,
    price: float,
    *,
    right: OptionRight = OptionRight.CALL,
    expiry: date = _EXPIRY,
):
    quote = RawOptionQuote(
        contract_id=f"SYN-{expiry.isoformat()}-{right.value}-{strike}",
        underlying_id="SYN",
        expiry=expiry,
        strike=strike,
        right=right,
        exercise_style=OptionExerciseStyle.EUROPEAN,
        provenance=_PROVENANCE,
        bid=price - 0.05,
        ask=price + 0.05,
        settlement_time=OptionSettlementTime.PM,
    )
    return normalize_european_option_midpoint(quote, _UNDERLYING)


def test_call_slice_passes_monotonicity_and_convexity() -> None:
    diagnostics = diagnose_option_strike_slice(
        (_observation(90.0, 12.0), _observation(100.0, 7.0), _observation(110.0, 3.0))
    )

    assert diagnostics.passes
    assert diagnostics.monotonicity_violations == ()
    assert diagnostics.convexity_violations == ()


def test_call_slice_reports_monotonicity_without_repairing_prices() -> None:
    observations = (_observation(90.0, 12.0), _observation(100.0, 13.0))

    diagnostics = diagnose_option_strike_slice(observations)

    assert not diagnostics.passes
    assert diagnostics.monotonicity_violations == ((90.0, 100.0),)
    assert observations[0].target_price == 12.0
    assert observations[1].target_price == 13.0


def test_call_slice_reports_discrete_convexity_violation() -> None:
    diagnostics = diagnose_option_strike_slice(
        (_observation(90.0, 12.0), _observation(100.0, 7.0), _observation(110.0, 1.0))
    )

    assert diagnostics.monotonicity_violations == ()
    assert diagnostics.convexity_violations == ((90.0, 100.0, 110.0),)


def test_put_slice_uses_put_monotonicity_direction() -> None:
    diagnostics = diagnose_option_strike_slice(
        (
            _observation(90.0, 2.0, right=OptionRight.PUT),
            _observation(100.0, 5.0, right=OptionRight.PUT),
            _observation(110.0, 9.0, right=OptionRight.PUT),
        )
    )

    assert diagnostics.passes


def test_diagnostics_reject_mixed_expiries() -> None:
    with pytest.raises(IncomparableOptionSlice, match="one expiry"):
        diagnose_option_strike_slice(
            (
                _observation(90.0, 12.0),
                _observation(100.0, 7.0, expiry=date(2026, 8, 2)),
            )
        )
