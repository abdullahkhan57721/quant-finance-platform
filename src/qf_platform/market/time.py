"""Date-to-model-time conventions used by the M1 equity-option vertical."""

from datetime import date


def actual_365_fixed_year_fraction(start: date, end: date) -> float:
    """Return Actual/365 Fixed year fraction between two calendar dates.

    Actual/365 Fixed divides the actual number of calendar days by exactly 365,
    including when the interval contains February 29.
    """
    if type(start) is not date:
        raise TypeError("start must be a datetime.date")
    if type(end) is not date:
        raise TypeError("end must be a datetime.date")
    if end < start:
        raise ValueError("end must not be before start")
    return (end - start).days / 365.0
