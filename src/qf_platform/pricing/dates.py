"""Calendar-date to model-time semantics for the M1 option vertical."""

from datetime import date

from qf_platform._validation import calendar_date


def actual_365_fixed_year_fraction(start: date, end: date, /) -> float:
    """Return the signed Actual/365 Fixed year fraction from ``start`` to ``end``.

    Actual/365 Fixed divides the actual number of calendar days by exactly 365.
    February 29 therefore contributes one full calendar day rather than changing
    the denominator.
    """

    start_date = calendar_date(start, name="start")
    end_date = calendar_date(end, name="end")
    return (end_date - start_date).days / 365.0
