"""F5 consistency checks across sibling interface adapters."""

from __future__ import annotations

from qf_platform.application import (
    M2WorkbenchDraft,
    canonical_black_scholes_draft,
    compose_black_scholes_study,
    make_m2_workbench_request,
    run_m2_workbench,
)
from qf_platform.presentation import build_m2_workbench_presentation
from qf_platform.reporting import valuation_greeks_report
from qf_platform.web.services import run_valuation_service


def test_canonical_valuation_and_delta_are_consistent_across_surfaces() -> None:
    composition = compose_black_scholes_study(canonical_black_scholes_draft())
    request = make_m2_workbench_request(composition, M2WorkbenchDraft())
    analysis = run_m2_workbench(request)

    selected = analysis.selected_valuation
    assert selected.result is not None
    authoritative_pv = selected.result.present_value

    delta = next(
        run for run in analysis.sensitivities if run.sensitivity.value == "delta"
    )
    assert delta.analytic_result is not None
    authoritative_delta = delta.analytic_result.value

    presentation = build_m2_workbench_presentation(request, analysis)
    present_value_row = next(
        row for row in presentation.result_rows if row.label == "Present value"
    )
    delta_row = next(row for row in presentation.greek_rows if row.greek == "Delta")
    assert present_value_row.value == f"{authoritative_pv:.12g}"
    assert delta_row.analytic == f"{authoritative_delta:.12g}"

    report = valuation_greeks_report(request, analysis)
    valuations = next(table for table in report.tables if table.name == "valuations")
    analytic_row = next(row for row in valuations.rows if row[0] == "analytic")
    assert analytic_row[3] == authoritative_pv

    greeks = next(table for table in report.tables if table.name == "greeks")
    delta_report_row = next(row for row in greeks.rows if row[0] == "delta")
    assert delta_report_row[1] == authoritative_delta

    web = run_valuation_service()
    assert web.error is None
    assert web.value is not None
    web_present_value = next(
        row for row in web.value.result_rows if row.label == "Present value"
    )
    web_delta = next(row for row in web.value.greek_rows if row.greek == "Delta")
    assert web_present_value.value == present_value_row.value
    assert web_delta.analytic == delta_row.analytic
