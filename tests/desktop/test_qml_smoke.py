from __future__ import annotations

from typing import cast

import pytest

pytest.importorskip("PySide6")

from PySide6.QtGui import QGuiApplication

from qf_platform.desktop.main import create_engine


def test_qml_loads_with_curated_controller_boundary() -> None:
    app = QGuiApplication.instance()
    if not isinstance(app, QGuiApplication):
        app = QGuiApplication(["ui1-qml-smoke"])
    engine, controller = create_engine()

    assert app.applicationName() is not None
    assert engine.rootObjects()
    assert cast(str, controller.defaultSpot) == "100"
    assert cast(str, controller.defaultOptionRight) == "call"
