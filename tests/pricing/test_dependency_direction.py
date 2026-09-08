import ast
from pathlib import Path

LOW_LEVEL_MODULES = (
    "cashflows.py",
    "contracts.py",
    "measures.py",
    "models.py",
    "state.py",
)


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return modules


def test_foundational_dependency_direction_keeps_valuation_downstream() -> None:
    package = Path(__file__).parents[2] / "src" / "qf_platform" / "pricing"

    for filename in LOW_LEVEL_MODULES:
        imports = imported_modules(package / filename)
        assert "qf_platform.pricing.problem" not in imports
        assert "qf_platform.pricing.valuation" not in imports

    problem_imports = imported_modules(package / "problem.py")
    assert "qf_platform.pricing.valuation" not in problem_imports
