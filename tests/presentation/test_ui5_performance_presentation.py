from __future__ import annotations

from qf_platform.application.ui5_performance import canonical_m8_performance_reference
from qf_platform.presentation.ui5_performance import build_ui5_performance_presentation


def test_ui5_performance_presentation_keeps_runtime_parity_and_native_decision_separate() -> (
    None
):
    presentation = build_ui5_performance_presentation(
        canonical_m8_performance_reference()
    )

    assert len(presentation.workload_rows) == 6
    assert len(presentation.runtime_plot.series) == 2
    assert all(len(series.points) == 6 for series in presentation.runtime_plot.series)
    assert presentation.runtime_plot.series[0].key == "baseline"
    assert presentation.runtime_plot.series[1].key == "optimized"

    assert presentation.workload_rows[0].status == "Scalar reference · no speedup claim"
    assert presentation.workload_rows[1].status == "Scalar reference · no speedup claim"
    assert "27.38× measured speedup" in presentation.workload_rows[2].status

    assert presentation.parity_rows[0].value == "PASS"
    assert "0.853 combined standard errors" in presentation.parity_rows[1].value
    assert presentation.parity_rows[2].value == "No"

    assert presentation.native_decision_rows[0].value == "No"
    assert presentation.native_decision_rows[0].status == "Measured negative native decision"
    assert "4.61×" in presentation.native_decision_rows[1].value
    assert "not justified" in presentation.native_decision_rows[2].value

    assert presentation.provenance_rows[0].value == (
        "docs/evidence/m8_performance_reference.json"
    )
    assert presentation.provenance_rows[-1].status == "Not a CI threshold"

    assert "M8 PERFORMANCE ENGINEERING EVIDENCE" in presentation.report_text
    assert "C++ kernel added: False" in presentation.report_text
