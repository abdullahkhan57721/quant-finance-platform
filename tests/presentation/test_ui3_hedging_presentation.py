from __future__ import annotations

from qf_platform.application.black_scholes_study import (
    canonical_black_scholes_draft,
    compose_black_scholes_study,
)
from qf_platform.application.ui3_hedging import (
    HedgeWorkbenchDraft,
    make_hedge_workbench_request,
    run_hedge_workbench,
)
from qf_platform.presentation.ui3_hedging import (
    build_hedge_workbench_presentation,
    hedge_step_detail_rows,
)


def test_hedge_presentation_keeps_path_aggregate_and_control_roles_explicit() -> None:
    request = make_hedge_workbench_request(
        compose_black_scholes_study(canonical_black_scholes_draft()),
        HedgeWorkbenchDraft(
            rebalance_day_interval="30",
            seed="9",
            replicate_count="2",
            transaction_cost_rate="0.001",
        ),
    )
    analysis = run_hedge_workbench(request)

    presentation = build_hedge_workbench_presentation(request, analysis)

    assert presentation.step_rows
    assert presentation.frequency_rows
    assert {row.label for row in presentation.inspector_rows} >= {
        "State",
        "Generating law",
        "Sensitivity source",
        "Control policy",
        "Rebalance schedule",
        "Financing / cost convention",
        "Objective / error",
    }
    assert presentation.underlying_plot.series[0].key == "spot"
    assert {series.key for series in presentation.hedge_value_plot.series} == {
        "hedge",
        "option",
    }
    assert {series.key for series in presentation.frequency_plot.series} == {
        "rmse",
        "mae",
    }
    details = hedge_step_detail_rows(presentation, 0)
    assert {row.label for row in details} >= {
        "Underlying",
        "Option value",
        "Target / realized stock units",
        "Cash after rebalance",
        "Transaction cost",
    }
