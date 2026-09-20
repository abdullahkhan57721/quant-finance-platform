"""Model-generated replication with explicit volatility, costs, cadence and seeds."""

from qf_platform.application import (
    HedgeWorkbenchAnalysis,
    HedgeWorkbenchConfig,
    HedgeWorkbenchRequest,
    canonical_black_scholes_draft,
    compose_black_scholes_study,
    run_hedge_workbench,
)


def make_request() -> HedgeWorkbenchRequest:
    # The canonical draft is a convenience for this published q=0 benchmark.
    # Numeric custom studies may construct BlackScholesStudyComposition directly.
    composition = compose_black_scholes_study(canonical_black_scholes_draft())
    return HedgeWorkbenchRequest(
        composition=composition,
        config=HedgeWorkbenchConfig(
            generating_volatility=0.25,
            hedging_volatility=0.20,
            rebalance_day_interval=7,
            seed=1729,
            replicate_count=8,
            transaction_cost_rate=0.001,
        ),
    )


def run_example() -> HedgeWorkbenchAnalysis:
    return run_hedge_workbench(make_request())


if __name__ == "__main__":
    analysis = run_example()
    print("Pricing-measure GBM replication; not a historical trading backtest.")
    print("Selected volatility/cost configuration:", analysis.selected_summary)
    print(
        "Matched generating/hedging volatility:", analysis.correctly_specified_summary
    )
    print("Same paths without costs:", analysis.frictionless_summary)
    for point in analysis.frequency_evidence:
        print("Rebalance interval (days):", point.rebalance_day_interval, point.summary)
