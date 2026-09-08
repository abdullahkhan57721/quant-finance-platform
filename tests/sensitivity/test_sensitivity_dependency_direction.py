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


def test_pricing_package_does_not_depend_on_sensitivity() -> None:
    pricing_package = Path(__file__).parents[2] / "src" / "qf_platform" / "pricing"

    for path in pricing_package.glob("*.py"):
        imports = imported_modules(path)
        assert all(
            not module.startswith("qf_platform.sensitivity") for module in imports
        ), path.name
