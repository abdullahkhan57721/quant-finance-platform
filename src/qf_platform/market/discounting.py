"""Narrow maturity-dependent discounting semantics."""

from dataclasses import dataclass
from datetime import date
from math import exp, isfinite
from typing import Protocol, runtime_checkable

from qf_platform._validation import finite_real
from qf_platform.market.time import actual_365_fixed_year_fraction


@runtime_checkable
class DiscountFactorProvider(Protocol):
    """Provide positive finite discount factors from one valuation date."""

    @property
    def valuation_date(self) -> date:
        """Return the valuation date owned by this provider."""
        ...

    def discount_factor(self, maturity: date) -> float:
        """Return the discount factor from valuation date to maturity."""
        ...


@dataclass(frozen=True, slots=True)
class FlatContinuousDiscountCurve:
    """Flat continuously compounded annual-rate discounting.

    For year fraction ``T`` under Actual/365 Fixed, the discount factor is
    ``exp(-r * T)`` where ``r`` is the continuously compounded annual rate.
    Negative rates are supported.
    """

    valuation_date: date
    continuously_compounded_rate: float

    def __post_init__(self) -> None:
        if type(self.valuation_date) is not date:
            raise TypeError("valuation_date must be a datetime.date")
        object.__setattr__(
            self,
            "continuously_compounded_rate",
            finite_real(
                self.continuously_compounded_rate,
                name="continuously_compounded_rate",
            ),
        )

    def discount_factor(self, maturity: date) -> float:
        """Return ``exp(-rT)`` for a maturity on or after valuation date."""
        year_fraction = actual_365_fixed_year_fraction(self.valuation_date, maturity)
        try:
            factor = exp(-self.continuously_compounded_rate * year_fraction)
        except OverflowError as exc:
            raise ValueError("discount factor must be finite") from exc
        if not isfinite(factor) or factor <= 0.0:
            raise ValueError("discount factor must be positive and finite")
        return factor
