import ast
from pathlib import Path


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return modules


def test_pricing_and_sensitivity_do_not_depend_on_control() -> None:
    package_root = Path(__file__).parents[2] / "src" / "qf_platform"

    for package_name in ("pricing", "sensitivity"):
        for path in (package_root / package_name).glob("*.py"):
            imports = imported_modules(path)
            assert all(
                not module.startswith("qf_platform.control") for module in imports
            ), path.name
