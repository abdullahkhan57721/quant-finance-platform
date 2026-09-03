"""Package-level smoke tests."""

import qf_platform


def test_package_imports() -> None:
    """Verify the source-layout package is importable after installation."""
    assert qf_platform.__name__ == "qf_platform"
