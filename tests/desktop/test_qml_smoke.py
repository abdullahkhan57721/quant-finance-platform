from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtGui import QGuiApplication

from qf_platform.desktop.main import create_engine


def test_qml_loads_with_curated_controller_boundary() -> None:
    if QGuiApplication.instance() is None:
        QGuiApplication(["ui1-qml-smoke"])
    engine, controller = create_engine()

    assert engine.rootObjects()
    assert controller.defaultSpot == "100"
    assert controller.defaultOptionRight == "call"
