"""Normalize a synthetic quote and infer model-dependent implied volatility."""

from datetime import UTC, date, datetime

from qf_platform.application import (
    MarketWorkbenchAnalysis,
    MarketWorkbenchConfig,
    run_market_workbench,
)
from qf_platform.market_data import (
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    RawOptionQuote,
    RawUnderlyingObservation,
)
from qf_platform.pricing import OptionRight


def run_example() -> MarketWorkbenchAnalysis:
    provenance = ObservationProvenance(
        provider="synthetic:F1-example",
        source="illustrative fixed bid/ask, not a market download",
        market_date=date(2026, 1, 1),
        retrieved_at=datetime(2026, 1, 2, tzinfo=UTC),
        license_notes="synthetic example; no raw vendor data",
    )
    underlying = RawUnderlyingObservation("SYN", 100.0, provenance)
    quote = RawOptionQuote(
        contract_id="SYN-2027-01-01-call-100",
        underlying_id="SYN",
        expiry=date(2027, 1, 1),
        strike=100.0,
        right=OptionRight.CALL,
        exercise_style=OptionExerciseStyle.EUROPEAN,
        settlement_time=OptionSettlementTime.PM,
        provenance=provenance,
        bid=10.40,
        ask=10.50,
    )
    return run_market_workbench(
        (quote,),
        underlying,
        MarketWorkbenchConfig(
            continuously_compounded_rate=0.05,
            continuous_dividend_yield=0.0,
            price_tolerance=1e-10,
            volatility_tolerance=1e-10,
            max_iterations=200,
        ),
    )


if __name__ == "__main__":
    analysis = run_example()
    for outcome in analysis.outcomes:
        print(outcome.raw_quote.contract_id, outcome.status.value, outcome.diagnostic)
        print("Normalized observation:", outcome.normalized)
        print("Inferred result:", outcome.result)
    print("IV is model-dependent inference, not observed physical volatility.")
    print("Separate committed SPX reference:", analysis.empirical_evidence.quote_date)
    print(analysis.empirical_evidence.license_note)
