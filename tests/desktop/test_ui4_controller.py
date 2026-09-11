from __future__ import annotations

import json
import time
from typing import cast

import pytest

pytest.importorskip("PySide6")

from PySide6.QtGui import QGuiApplication

from qf_platform.desktop.controller import WorkbenchController
from qf_platform.desktop.models import PresentationRowModel

_app_instance: QGuiApplication | None = None


def _app() -> QGuiApplication:
    global _app_instance  # noqa: PLW0603
    existing = QGuiApplication.instance()
    if isinstance(existing, QGuiApplication):
        _app_instance = existing
    elif _app_instance is None:
        _app_instance = QGuiApplication(["ui4-controller-tests"])
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


def _run_heston(controller: WorkbenchController, *, paths: str = "256") -> bool:
    return controller.runHestonPricing(
        "100",
        "100",
        "2026-01-01",
        "2027-01-01",
        "0.03",
        "0.01",
        "call",
        "0.04",
        "2.0",
        "0.04",
        "0.5",
        "-0.7",
        "1e-8",
        "80",
        "64",
        paths,
        "16",
        "19",
    )


def test_ui4_heston_worker_exposes_model_and_method_specific_evidence() -> None:
    controller = _controller()

    assert _run_heston(controller)
    _finish(controller)

    assert controller.hestonAnalysisReady
    assert cast(PresentationRowModel, controller.hestonModelModel).rowCount() >= 4
    assert cast(PresentationRowModel, controller.hestonParameterModel).rowCount() >= 8
    assert cast(PresentationRowModel, controller.hestonFourierModel).rowCount() >= 4
    assert cast(PresentationRowModel, controller.hestonMonteCarloModel).rowCount() >= 5
    assert cast(PresentationRowModel, controller.hestonInspectorModel).rowCount() >= 8

    comparison = json.loads(cast(str, controller.hestonMethodComparisonPlotJson))
    assert {series["key"] for series in comparison["series"]} == {
        "fourier",
        "monte_carlo",
    }
    assert comparison["series"][1]["points"][0]["lower"] is not None


def test_ui4_calibration_worker_exposes_rank_deficient_thin_evidence() -> None:
    controller = _controller()

    assert controller.runHestonCalibration(
        "thin",
        "0.06",
        "1.2",
        "0.06",
        "0.8",
        "-0.4",
        "250",
        "64",
    )
    _finish(controller)

    assert controller.calibrationAnalysisReady
    assert (
        cast(PresentationRowModel, controller.calibrationProblemModel).rowCount() >= 7
    )
    assert cast(PresentationRowModel, controller.calibrationRunModel).rowCount() == 2
    assert (
        cast(PresentationRowModel, controller.calibrationConditioningModel).rowCount()
        >= 6
    )
    objective = json.loads(cast(str, controller.calibrationObjectivePlotJson))
    assert len(objective["series"][0]["points"]) == 2


def test_ui4_real_market_reference_is_available_without_raw_replay() -> None:
    controller = _controller()

    assert cast(PresentationRowModel, controller.m6MarketSummaryModel).rowCount() >= 5
    assert (
        cast(PresentationRowModel, controller.m6MarketProvenanceModel).rowCount() >= 4
    )
    assert cast(PresentationRowModel, controller.m6MarketStartModel).rowCount() == 3
    residuals = json.loads(cast(str, controller.m6MarketResidualPlotJson))
    assert len(residuals["series"][0]["points"]) == 14


def test_ui4_discards_heston_result_if_inputs_change_during_execution() -> None:
    controller = _controller()

    assert _run_heston(controller, paths="2048")
    controller.invalidateUi4Result("heston")
    _finish(controller)

    assert not controller.hestonAnalysisReady
    assert cast(PresentationRowModel, controller.hestonResultModel).rowCount() == 0
    assert "stale result discarded" in cast(str, controller.status).lower()
