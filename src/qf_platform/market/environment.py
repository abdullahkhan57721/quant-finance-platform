"""Valuation-ready market state."""

from dataclasses import dataclass
from datetime import date

from qf_platform._validation import nonnegative_finite_real
from qf_platform.market.discounting import DiscountFactorProvider


@dataclass(frozen=True, slots=True)
class MarketEnvironment:
    """Immutable valuation-ready spot and deterministic discounting inputs."""

    valuation_date: date
    spot: float
    risk_free_discounting: DiscountFactorProvider
    dividend_discounting: DiscountFactorProvider

    def __post_init__(self) -> None:
        if type(self.valuation_date) is not date:
            raise TypeError("valuation_date must be a datetime.date")
        object.__setattr__(
            self,
            "spot",
            nonnegative_finite_real(self.spot, name="spot"),
        )
        risk_free_discounting: object = self.risk_free_discounting
        dividend_discounting: object = self.dividend_discounting
        if not isinstance(risk_free_discounting, DiscountFactorProvider):
            raise TypeError(
                "risk_free_discounting must provide maturity discount factors"
            )
        if not isinstance(dividend_discounting, DiscountFactorProvider):
            raise TypeError(
                "dividend_discounting must provide maturity discount factors"
            )
        if self.risk_free_discounting.valuation_date != self.valuation_date:
            raise ValueError(
                "risk-free discounting valuation date must match market environment"
            )
        if self.dividend_discounting.valuation_date != self.valuation_date:
            raise ValueError(
                "dividend discounting valuation date must match market environment"
            )
