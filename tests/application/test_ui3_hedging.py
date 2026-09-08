from __future__ import annotations

from qf_platform.application.black_scholes_study import (
    BlackScholesStudyDraft,
    compose_black_scholes_study,
)
from qf_platform.application.ui3_hedging import (
    HedgeWorkbenchDraft,
    make_hedge_workbench_request,
    run_hedge_workbench,
)


def _composition(*, carry: str = "0.0"):
    return compose_black_scholes_study(
        BlackScholesStudyDraft(
            spot="100",
            strike="100",
            valuation_date="2026-01-01",
            expiry="2027-01-01",
            annualized_volatility="0.20",
            continuously_compounded_rate="0.05",
            continuous_dividend_yield=carry,
            option_right="call",
        )
    )


def test_hedge_workbench_preserves_path_and_replicate_evidence_distinction() -> None:
    request = make_hedge_workbench_request(
        _composition(),
        HedgeWorkbenchDraft(
            generating_volatility="0.30",
            hedging_volatility="0.20",
            rebalance_day_interval="10",
            seed="50",
            replicate_count="3",
            transaction_cost_rate="0.001",
        ),
    )

    analysis = run_hedge_workbench(request)

    assert analysis.selected_result.seed == 50
    assert len(analysis.selected_result.path.points) == 366
    assert tuple(item.seed for item in analysis.selected_replicates) == (50, 51, 52)
    assert analysis.selected_summary.replicate_count == 3
    assert analysis.selected_summary.seeds == (50, 51, 52)
    assert analysis.selected_summary.generating_annualized_volatility == 0.30
    assert analysis.selected_summary.hedging_annualized_volatility == 0.20
    assert analysis.selected_summary.proportional_transaction_cost_rate == 0.001


def test_hedge_workbench_builds_paired_frequency_misspecification_and_cost_evidence() -> (
    None
):
    request = make_hedge_workbench_request(
        _composition(),
        HedgeWorkbenchDraft(
            generating_volatility="0.30",
            hedging_volatility="0.20",
            rebalance_day_interval="10",
            seed="70",
            replicate_count="3",
            transaction_cost_rate="0.001",
        ),
    )

    analysis = run_hedge_workbench(request)

    assert tuple(
        point.rebalance_day_interval for point in analysis.frequency_evidence
    ) == (30, 14, 7, 1, 10)
    assert all(
        point.summary.seeds == (70, 71, 72) for point in analysis.frequency_evidence
    )
    assert analysis.correctly_specified_summary.seeds == (70, 71, 72)
    assert analysis.correctly_specified_summary.generating_annualized_volatility == 0.30
    assert analysis.correctly_specified_summary.hedging_annualized_volatility == 0.30
    assert analysis.frictionless_summary.proportional_transaction_cost_rate == 0.0
    assert analysis.frictionless_summary.seeds == (70, 71, 72)


def test_hedge_workbench_refuses_ui_exposure_m3_does_not_support() -> None:
    try:
        make_hedge_workbench_request(_composition(carry="0.02"), HedgeWorkbenchDraft())
    except ValueError as exc:
        assert "zero continuous dividend-yield" in str(exc)
    else:
        raise AssertionError("nonzero-dividend hedge request should be rejected")
