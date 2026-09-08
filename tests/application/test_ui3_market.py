from __future__ import annotations

from dataclasses import replace

import pytest

from qf_platform.application.ui3_market import (
    MarketObservationStatus,
    MarketWorkbenchConfig,
    canonical_m4_market_workbench,
    run_market_workbench,
)


def test_canonical_market_workbench_runs_the_actual_m4_pipeline() -> None:
    analysis = canonical_m4_market_workbench()

    assert analysis.underlying.underlying_id == "SYN"
    assert analysis.underlying.value == 100.0
    assert len(analysis.outcomes) == 10
    assert all(
        outcome.status is MarketObservationStatus.INFERRED
        for outcome in analysis.outcomes
    )
    inferred = {
        (outcome.raw_quote.expiry.isoformat(), outcome.raw_quote.strike): (
            outcome.result.annualized_volatility if outcome.result is not None else None
        )
        for outcome in analysis.outcomes
    }
    assert inferred[("2026-04-02", 80.0)] == pytest.approx(0.30, abs=1.0e-8)
    assert inferred[("2026-04-02", 120.0)] == pytest.approx(0.21, abs=1.0e-8)
    assert inferred[("2026-07-01", 80.0)] == pytest.approx(0.28, abs=1.0e-8)
    assert inferred[("2026-07-01", 120.0)] == pytest.approx(0.21, abs=1.0e-8)
    assert len(analysis.slice_evidence) == 4


def test_market_workbench_preserves_normalization_failure_as_evidence() -> None:
    canonical = canonical_m4_market_workbench()
    original = canonical.outcomes[0].raw_quote
    crossed = replace(original, bid=2.0, ask=1.0)

    analysis = run_market_workbench(
        (crossed,),
        canonical.underlying,
        MarketWorkbenchConfig(),
    )

    outcome = analysis.outcomes[0]
    assert outcome.status is MarketObservationStatus.NORMALIZATION_REJECTED
    assert outcome.normalized is None
    assert outcome.result is None
    assert "crossed" in outcome.diagnostic


def test_market_workbench_preserves_inverse_failure_after_normalization() -> None:
    canonical = canonical_m4_market_workbench()

    analysis = run_market_workbench(
        (canonical.outcomes[0].raw_quote,),
        canonical.underlying,
        MarketWorkbenchConfig(maximum_annualized_volatility=0.05),
    )

    outcome = analysis.outcomes[0]
    assert outcome.status is MarketObservationStatus.INFERENCE_FAILED
    assert outcome.normalized is not None
    assert outcome.result is None
    assert "ImpliedVolatilityNotBracketed" in outcome.diagnostic


def test_empirical_spx_panel_is_explicitly_derived_not_raw_redistribution() -> None:
    evidence = canonical_m4_market_workbench().empirical_evidence

    assert evidence.underlying == "SPX"
    assert evidence.quote_date.isoformat() == "2023-01-04"
    assert len(evidence.points) == 14
    assert "raw rows are not redistributed" in evidence.license_note
    expiries = {point.expiry.isoformat() for point in evidence.points}
    assert expiries == {"2023-02-03", "2023-04-28"}
