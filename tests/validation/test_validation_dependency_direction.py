from __future__ import annotations

from pathlib import Path


def test_lower_quantitative_families_do_not_depend_on_validation() -> None:
    src_root = Path(__file__).parents[2] / "src" / "qf_platform"
    lower_families = ("pricing", "sensitivity", "control", "market_data", "inference")
    violations: list[str] = []
    for family in lower_families:
        for path in (src_root / family).rglob("*.py"):
            if "qf_platform.validation" in path.read_text(encoding="utf-8"):
                violations.append(str(path.relative_to(src_root)))

    assert violations == []


def test_validation_does_not_depend_on_application_presentation_or_desktop() -> None:
    src_root = Path(__file__).parents[2] / "src" / "qf_platform"
    forbidden = (
        "qf_platform.application",
        "qf_platform.presentation",
        "qf_platform.desktop",
    )
    violations: list[str] = []
    for path in (src_root / "validation").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(module in text for module in forbidden):
            violations.append(str(path.relative_to(src_root)))

    assert violations == []
