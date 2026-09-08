from __future__ import annotations

import json
import time
from typing import cast

import pytest

pytest.importorskip("PySide6")

from PySide6.QtGui import QGuiApplication

from qf_platform.desktop.controller import WorkbenchController

_app_instance: QGuiApplication | None = None


def _app() -> QGuiApplication:
    global _app_instance  # noqa: PLW0603
    existing = QGuiApplication.instance()
    if isinstance(existing, QGuiApplication):
        _app_instance = existing
    elif _app_instance is None:
        _app_instance = QGuiApplication(["ui3-controller-tests"])
    return _app_instance


def _controller() -> WorkbenchController:
    _app()
    return WorkbenchController()


def _finish(controller: WorkbenchController, timeout: float = 20.0) -> None:
    app = _app()
    deadline = time.monotonic() + timeout
    while controller.running and time.monotonic() < deadline:
        app.processEvents()
    assert not controller.running


def test_ui3_hedge_worker_exposes_path_and_aggregate_models() -> None:
    controller = _controller()

    assert controller.runHedgeStudy(
        "100",
        "100",
        "2026-01-01",
        "2027-01-01",
        "0.05",
        "call",
        "0.30",
        "0.20",
        "30",
        "19",
        "2",
        "0.001",
    )
    _finish(controller)

    assert controller.hedgeAnalysisReady
    assert controller.hedgeStepModel.rowCount() > 0
    assert controller.hedgeFrequencyModel.rowCount() >= 4
    controller.selectHedgeStep(0)
    assert controller.hedgeSelectedStepModel.rowCount() >= 7

    underlying = json.loads(cast(str, controller.hedgeUnderlyingPlotJson))
    assert underlying["series"][0]["key"] == "spot"
    frequency = json.loads(cast(str, controller.hedgeFrequencyPlotJson))
    assert {series["key"] for series in frequency["series"]} == {"rmse", "mae"}


def test_ui3_market_worker_exposes_observation_inverse_and_empirical_evidence() -> None:
    controller = _controller()

    assert controller.loadMarketEvidence()
    _finish(controller)

    assert controller.marketAnalysisReady
    assert controller.marketObservationModel.rowCount() == 10
    assert controller.marketDiagnosticModel.rowCount() == 4
    controller.selectMarketObservation(0)
    assert controller.marketProvenanceModel.rowCount() >= 7
    assert controller.marketInverseModel.rowCount() >= 7
    assert controller.marketInspectorModel.rowCount() == 6

    synthetic = json.loads(cast(str, controller.syntheticSmilePlotJson))
    empirical = json.loads(cast(str, controller.empiricalSmilePlotJson))
    assert len(synthetic["series"]) == 2
    assert len(empirical["series"]) == 2
