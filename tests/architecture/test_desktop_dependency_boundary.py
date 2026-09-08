from __future__ import annotations

from pathlib import Path


def test_lower_layers_do_not_depend_on_optional_desktop_or_pyside() -> None:
    package_root = Path(__file__).resolve().parents[2] / "src" / "qf_platform"
    violations: list[str] = []
    for path in package_root.rglob("*.py"):
        relative = path.relative_to(package_root)
        if relative.parts and relative.parts[0] == "desktop":
            continue
        source = path.read_text(encoding="utf-8")
        if "PySide6" in source or "qf_platform.desktop" in source:
            violations.append(str(relative))

    assert violations == []
