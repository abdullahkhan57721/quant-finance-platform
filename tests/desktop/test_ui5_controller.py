from __future__ import annotations

import json
import time
from typing import cast

import pytest

pytest.importorskip("PySide6")

from PySide6.QtGui import QGuiApplication

from qf_platform.desktop.models import PresentationRowModel
from qf_platform.desktop.ui5_controller import WorkbenchController

_app_instance: QGuiApplication | None = None


def _app() -> QGuiApplication:
    global _app_instance  # noqa: PLW0603
    existing = QGuiApplication.instance()
    if isinstance(existing, QGuiApplication):
        _app_instance = existing
    elif _app_instance is None:
        _app_instance = QGuiApplication(["ui5-controller-tests"])
    return _app_instance


def _controller() -> WorkbenchController:
    _app()
    return WorkbenchController()


def _finish(controller: WorkbenchController, timeout: float = 30.0) -> None:
    app = _app()
    deadline = time.monotonic() + timeout
    while controller.running and time.monotonic() < deadline:
        app.processEvents()
    assert not controller.running
    app.processEvents()


def test_ui5_controller_exposes_empty_validation_and_committed_performance_state() -> (
    None
):
    controller = _controller()

    assert not controller.validationAnalysisReady
    assert "Run the M7 validation study" in cast(str, controller.validationReportText)
    assert json.loads(cast(str, controller.validationResidualPlotJson)) == {}
    assert json.loads(cast(str, controller.validationHeldOutErrorPlotJson)) == {}
    assert json.loads(cast(str, controller.validationParameterStabilityPlotJson)) == {}
    assert cast(PresentationRowModel, controller.validationSummaryModel).rowCount() == 0
    assert (
        cast(PresentationRowModel, controller.validationTrainingMetricModel).rowCount()
        == 0
    )
    assert (
        cast(
            PresentationRowModel, controller.validationEvaluationMetricModel
        ).rowCount()
        == 0
    )
    assert (
        cast(PresentationRowModel, controller.validationResidualModel).rowCount() == 0
    )
    assert (
        cast(PresentationRowModel, controller.validationStabilityModel).rowCount() == 0
    )
    assert cast(PresentationRowModel, controller.validationRiskModel).rowCount() == 0
    assert (
        cast(PresentationRowModel, controller.validationWorkloadModel).rowCount() == 0
    )
    assert (
        cast(PresentationRowModel, controller.validationInspectorModel).rowCount() == 0
    )

    assert (
        cast(PresentationRowModel, controller.performanceWorkloadModel).rowCount() == 6
    )
    assert cast(PresentationRowModel, controller.performanceParityModel).rowCount() == 3
    assert (
        cast(PresentationRowModel, controller.performanceNativeDecisionModel).rowCount()
        == 3
    )
    assert (
        cast(PresentationRowModel, controller.performanceProvenanceModel).rowCount()
        == 4
    )
    performance_plot = json.loads(cast(str, controller.performanceRuntimePlotJson))
    assert len(performance_plot["series"]) == 2
    assert all(len(series["points"]) == 6 for series in performance_plot["series"])

    performance_report = cast(str, controller.performanceReportText)
    combined_report = cast(str, controller.ui5EvidenceReportText)
    assert "M8 PERFORMANCE ENGINEERING EVIDENCE" in performance_report
    assert "C++ kernel added: False" in performance_report
    assert "Run the M7 validation study" in combined_report
    assert "M8 PERFORMANCE ENGINEERING EVIDENCE" in combined_report


def test_ui5_threaded_validation_installs_authoritative_m7_evidence() -> None:
    controller = _controller()

    assert controller.runValidationStudy()
    _finish(controller)

    assert controller.validationAnalysisReady
    assert cast(PresentationRowModel, controller.validationSummaryModel).rowCount() >= 4
    assert (
        cast(PresentationRowModel, controller.validationTrainingMetricModel).rowCount()
        >= 3
    )
    assert (
        cast(
            PresentationRowModel, controller.validationEvaluationMetricModel
        ).rowCount()
        >= 3
    )
    assert (
        cast(PresentationRowModel, controller.validationResidualModel).rowCount() == 14
    )
    assert (
        cast(PresentationRowModel, controller.validationWorkloadModel).rowCount() == 6
    )
    assert (
        cast(PresentationRowModel, controller.validationInspectorModel).rowCount() >= 6
    )

    residual_plot = json.loads(cast(str, controller.validationResidualPlotJson))
    held_out_plot = json.loads(cast(str, controller.validationHeldOutErrorPlotJson))
    stability_plot = json.loads(
        cast(str, controller.validationParameterStabilityPlotJson)
    )
    assert len(residual_plot["series"]) == 4
    assert len(held_out_plot["series"]) == 2
    assert len(stability_plot["series"][0]["points"]) == 5

    report = cast(str, controller.validationReportText)
    combined_report = cast(str, controller.ui5EvidenceReportText)
    assert "10 training / 4 evaluation" in report
    assert "Bounded conclusion" in report
    assert "no authoritative Heston hedge comparison" in report
    assert "10 training / 4 evaluation" in combined_report
    assert "M8 PERFORMANCE ENGINEERING EVIDENCE" in combined_report
