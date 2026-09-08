from __future__ import annotations

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
        _app_instance = QGuiApplication(["ui1-controller-tests"])
    return _app_instance


def _controller() -> WorkbenchController:
    _app()
    return WorkbenchController()


def test_controller_normalizes_without_exposing_domain_graphs() -> None:
    controller = _controller()

    assert controller.validateDraft(
        "100", "100", "2026-01-01", "2027-01-01", "0.20", "0.05", "0", "call"
    )
    assert controller.compositionReady
    assert controller.methodSupported
    assert not controller.hasResult
    assert "Black-Scholes analytic is supported" in cast(str, controller.status)
    assert "PricingProblem" not in cast(str, controller.payoffPointsJson)


def test_controller_rejects_invalid_transient_input() -> None:
    controller = _controller()

    assert not controller.validateDraft(
        "oops", "100", "2026-01-01", "2027-01-01", "0.20", "0.05", "0", "call"
    )
    assert not controller.compositionReady
    assert cast(str, controller.status).startswith("Composition invalid:")


def test_pricing_worker_returns_authoritative_m1_result() -> None:
    controller = _controller()
    app = _app()

    assert controller.priceDraft(
        "100", "100", "2026-01-01", "2027-01-01", "0.20", "0.05", "0", "call"
    )
    deadline = time.monotonic() + 5.0
    while controller.running and time.monotonic() < deadline:
        app.processEvents()

    assert not controller.running
    assert controller.hasResult
    assert float(cast(str, controller.presentValue)) == pytest.approx(
        10.450583572185565,
        abs=2e-11,
    )
