"""Launch the native PySide6 / Qt Quick Quant Research Workbench."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from qf_platform.desktop.controller import WorkbenchController


def create_engine() -> tuple[QQmlApplicationEngine, WorkbenchController]:
    """Create the QML engine with one deliberately curated Python controller."""
    engine = QQmlApplicationEngine()
    controller = WorkbenchController()
    engine.rootContext().setContextProperty("workbenchController", controller)
    qml_path = Path(__file__).resolve().parent / "qml" / "UI4Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        raise RuntimeError(f"Failed to load Quant Workbench QML from {qml_path}.")
    return engine, controller


def main(argv: list[str] | None = None) -> int:
    """Run the native desktop application."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Load the native application and exit automatically after startup.",
    )
    args, qt_args = parser.parse_known_args(argv)
    app = QGuiApplication([sys.argv[0], *qt_args])
    app.setApplicationName("Quant Research Workbench")
    engine, controller = create_engine()
    # Keep Python-owned objects alive for the full QML engine lifetime.
    app.setProperty("ui1Engine", engine)
    app.setProperty("ui1WorkbenchController", controller)
    if args.smoke_test:
        QTimer.singleShot(300, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
