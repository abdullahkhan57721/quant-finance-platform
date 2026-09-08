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
        _app_instance = QGuiApplication(["ui2-controller-tests"])
    return _app_instance


def _controller() -> WorkbenchController:
    _app()
    return WorkbenchController()


def _ui2_args(
    *,
    rate: str = "0.05",
    volatility: str = "0.20",
    method: str = "analytic",
    crr_steps: str = "400",
    paths: str = "2000",
    seed: str = "1729",
    greek: str = "gamma",
) -> tuple[str, ...]:
    return (
        "100",
        "100",
        "2026-01-01",
        "2027-01-01",
        volatility,
        rate,
        "0",
        "call",
        method,
        crr_steps,
        paths,
        seed,
        greek,
        "0.1",
        "0.001",
        "0.0001",
        "1",
    )


def test_ui2_controller_validates_selected_method_configuration() -> None:
    controller = _controller()

    assert controller.validateStudy(*_ui2_args(method="crr", crr_steps="200"))
    assert controller.compositionReady
    assert controller.methodSupported
    assert cast(str, controller.selectedMethodLabel) == "Cox-Ross-Rubinstein"
    assert "supported" in cast(str, controller.status).lower()


def test_ui2_controller_preserves_explicit_crr_support_boundary() -> None:
    controller = _controller()

    assert not controller.validateStudy(
        *_ui2_args(
            rate="0.50",
            volatility="0.01",
            method="crr",
            crr_steps="1",
        )
    )
    assert controller.compositionReady
    assert not controller.methodSupported
    assert "unsupported" in cast(str, controller.status).lower()


def test_ui2_worker_returns_comparison_uncertainty_and_greek_plot() -> None:
    controller = _controller()
    app = _app()

    assert controller.runStudy(
        *_ui2_args(method="monte_carlo", paths="2000", seed="1729", greek="gamma")
    )
    deadline = time.monotonic() + 12.0
    while controller.running and time.monotonic() < deadline:
        app.processEvents()

    assert not controller.running
    assert controller.analysisReady
    assert controller.hasResult
    assert float(cast(str, controller.presentValue)) > 0.0

    monte_carlo_plot = json.loads(cast(str, controller.monteCarloPlotJson))
    assert monte_carlo_plot["series"][0]["key"] == "monte_carlo"
    assert any(
        point["lower"] is not None and point["upper"] is not None
        for point in monte_carlo_plot["series"][0]["points"]
    )

    greek_plot = json.loads(cast(str, controller.greekPlotJson))
    assert greek_plot["title"] == "Gamma vs spot"
    assert {series["key"] for series in greek_plot["series"]} == {
        "analytic",
        "finite_difference",
    }
