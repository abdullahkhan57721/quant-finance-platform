from __future__ import annotations

import json

import pytest

pytest.importorskip("PySide6")

from qf_platform.desktop.ui5_controller import WorkbenchController


def test_ui5_controller_exposes_empty_validation_state_without_fabricating_results() -> None:
    controller = WorkbenchController()

    assert not controller.validationAnalysisReady
    assert "Run the M7 validation study" in controller.validationReportText
    assert json.loads(controller.validationResidualPlotJson) == {}
    assert json.loads(controller.validationHeldOutErrorPlotJson) == {}
    assert json.loads(controller.validationParameterStabilityPlotJson) == {}
    assert controller.validationSummaryModel is not None
    assert controller.validationTrainingMetricModel is not None
    assert controller.validationEvaluationMetricModel is not None
    assert controller.validationResidualModel is not None
    assert controller.validationStabilityModel is not None
    assert controller.validationRiskModel is not None
    assert controller.validationWorkloadModel is not None
    assert controller.validationInspectorModel is not None
