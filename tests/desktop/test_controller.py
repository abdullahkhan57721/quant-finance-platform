from __future__ import annotations

import time

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication

from qf_platform.desktop.controller import WorkbenchController


def _controller() -> WorkbenchController:
    if QCoreApplication.instance() is None:
        QCoreApplication([])
    return WorkbenchController()


def test_controller_normalizes_without_exposing_domain_graphs() -> None:
    controller = _controller()

    assert controller.validateDraft(
        "100", "100", "2026-01-01", "2027-01-01", "0.20", "0.05", "0", "call"
    )
    assert controller.compositionReady
    assert controller.methodSupported
    assert not controller.hasResult
    assert "Black-Scholes analytic is supported" in controller.status
    assert "PricingProblem" not in controller.payoffPointsJson


def test_controller_rejects_invalid_transient_input() -> None:
    controller = _controller()

    assert not controller.validateDraft(
        "oops", "100", "2026-01-01", "2027-01-01", "0.20", "0.05", "0", "call"
    )
    assert not controller.compositionReady
    assert controller.status.startswith("Composition invalid:")


def test_pricing_worker_returns_authoritative_m1_result() -> None:
    controller = _controller()
    app = QCoreApplication.instance()
    assert app is not None

    assert controller.priceDraft(
        "100", "100", "2026-01-01", "2027-01-01", "0.20", "0.05", "0", "call"
    )
    deadline = time.monotonic() + 5.0
    while controller.running and time.monotonic() < deadline:
        app.processEvents()

    assert not controller.running
    assert controller.hasResult
    assert float(controller.presentValue) == pytest.approx(
        10.450583572185565,
        abs=2e-11,
    )
