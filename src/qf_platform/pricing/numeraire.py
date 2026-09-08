"""Concrete money-market numeraire specialization required by M1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import exp, isfinite

from qf_platform._validation import calendar_date, finite_real
from qf_platform.pricing.dates import actual_365_fixed_year_fraction


@dataclass(frozen=True, slots=True)
class FlatMoneyMarketNumeraire:
    """Flat continuously compounded money-market account normalized to one.

    ``continuously_compounded_rate`` is an annualized decimal rate. Negative rates
    are admitted. The account is normalized to ``1`` on ``reference_date``:

    ``N(t) = exp(r * ACT365F(reference_date, t))``.
    """

    reference_date: date
    continuously_compounded_rate: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "reference_date",
            calendar_date(self.reference_date, name="reference_date"),
        )
        object.__setattr__(
            self,
            "continuously_compounded_rate",
            finite_real(
                self.continuously_compounded_rate,
                name="continuously_compounded_rate",
            ),
        )

    def value_at(self, time: date, /) -> float:
        """Return the strictly positive finite account value at ``time``."""

        access_date = calendar_date(time, name="time")
        year_fraction = actual_365_fixed_year_fraction(
            self.reference_date,
            access_date,
        )
        exponent = self.continuously_compounded_rate * year_fraction
        try:
            value = exp(exponent)
        except OverflowError as exc:
            msg = "money-market numeraire value must be positive and finite"
            raise ValueError(msg) from exc
        if not isfinite(value) or value <= 0.0:
            msg = "money-market numeraire value must be positive and finite"
            raise ValueError(msg)
        return value
