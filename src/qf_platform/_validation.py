"""Private validation helpers shared by concrete finance value objects."""

from math import isfinite


def finite_real(value: object, *, name: str) -> float:
    """Normalize an ordinary real number to a finite float."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")

    normalized = float(value)
    if not isfinite(normalized):
        raise ValueError(f"{name} must be finite")
    return normalized


def nonnegative_finite_real(value: object, *, name: str) -> float:
    """Normalize an ordinary real number to a finite non-negative float."""
    normalized = finite_real(value, name=name)
    if normalized < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return normalized
