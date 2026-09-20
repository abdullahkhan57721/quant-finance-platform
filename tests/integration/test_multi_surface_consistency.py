"""F5 canonical cross-surface consistency regression."""

from __future__ import annotations

import pytest

from qf_platform.application import (
    M2WorkbenchDraft,
    canonical_black_scholes_draft,
    compose_black_scholes_study,
    make_m2_workbench_request,
    run_m2_workbench,
)
from qf_platform.presentation import build_m2_workbench_presentation
from qf_platform.reporting import valuation_greeks_report
from qf_platform.sensitivity import BlackScholesSensitivity
from qf_platform.web.services import run_valuation_service


def test_canonical_black_scholes_evidence_is_consistent_across_sibling_surfaces() -> (
    None
):
    composition = compose_black_scholes_study(canonical_black_scholes_draft())
    request = make_m2_workbench_request(composition, M2WorkbenchDraft())
    analysis = run_m2_workbench(request)

    analytic = next(
        run for run in analysis.valuations if run.method.value == "analytic"
    )
    assert analytic.result is not None
    authoritative_pv = analytic.result.present_value

    delta = next(
        run
        for run in analysis.sensitivities
        if run.sensitivity is BlackScholesSensitivity.DELTA
    )
    assert delta.analytic_result is not None
    authoritative_delta = delta.analytic_result.value

    presentation = build_m2_workbench_presentation(request, analysis)
    report = valuation_greeks_report(request, analysis)
    web_result = run_valuation_service()
    assert web_result.error is None
    assert web_result.value is not None
    web = web_result.value

    valuation_table = next(
        table for table in report.tables if table.name == "valuations"
    )
    report_analytic = next(row for row in valuation_table.rows if row[0] == "analytic")
    assert report_analytic[3] == authoritative_pv

    greek_table = next(table for table in report.tables if table.name == "greeks")
    report_delta = next(row for row in greek_table.rows if row[0] == "delta")
    assert report_delta[1] == authoritative_delta

    presentation_pv = next(
        row.value for row in presentation.result_rows if row.label == "Present value"
    )
    presentation_delta = next(
        row.analytic for row in presentation.greek_rows if row.greek == "Delta"
    )
    web_pv = next(row.value for row in web.result_rows if row.label == "Present value")
    web_delta = next(row.analytic for row in web.greek_rows if row.greek == "Delta")

    assert float(presentation_pv) == pytest.approx(authoritative_pv, rel=1e-11)
    assert float(presentation_delta) == pytest.approx(authoritative_delta, rel=1e-9)
    assert web_pv == presentation_pv
    assert web_delta == presentation_delta
