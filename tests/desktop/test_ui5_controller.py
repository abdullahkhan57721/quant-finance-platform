from __future__ import annotations

import json
from typing import cast

import pytest

pytest.importorskip("PySide6")

from qf_platform.desktop.models import PresentationRowModel
from qf_platform.desktop.ui5_controller import WorkbenchController


def test_ui5_controller_exposes_empty_validation_state_without_fabricating_results() -> (
    None
):
    controller = WorkbenchController()

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
        cast(PresentationRowModel, controller.validationEvaluationMetricModel).rowCount()
        == 0
    )
    assert cast(PresentationRowModel, controller.validationResidualModel).rowCount() == 0
    assert cast(PresentationRowModel, controller.validationStabilityModel).rowCount() == 0
    assert cast(PresentationRowModel, controller.validationRiskModel).rowCount() == 0
    assert cast(PresentationRowModel, controller.validationWorkloadModel).rowCount() == 0
    assert cast(PresentationRowModel, controller.validationInspectorModel).rowCount() == 0
