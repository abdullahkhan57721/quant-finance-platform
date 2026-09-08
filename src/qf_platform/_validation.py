"""Private validation helpers shared by concrete finance value objects."""

from datetime import date
from math import isfinite


def finite_real(value: object, *, name: str) -> float:
    """Normalize an ordinary real number to a finite float."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        msg = f"{name} must be a real number"
        raise TypeError(msg)
    normalized = float(value)
    if not isfinite(normalized):
        msg = f"{name} must be finite"
        raise ValueError(msg)
    return normalized


def nonnegative_finite_real(value: object, *, name: str) -> float:
    """Normalize an ordinary real number to a finite non-negative float."""

    normalized = finite_real(value, name=name)
    if normalized < 0.0:
        msg = f"{name} must be non-negative"
        raise ValueError(msg)
    return normalized


def calendar_date(value: object, *, name: str) -> date:
    """Require a calendar ``datetime.date`` rather than a ``datetime``."""

    if type(value) is not date:
        msg = f"{name} must be a datetime.date"
        raise TypeError(msg)
    return value
