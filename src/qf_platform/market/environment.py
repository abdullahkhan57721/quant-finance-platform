"""Valuation-ready market state."""

from dataclasses import dataclass
from datetime import date

from qf_platform._validation import nonnegative_finite_real
from qf_platform.market.discounting import DiscountFactorProvider


def _validate_discount_factor_provider(value: object, *, name: str) -> None:
    if not isinstance(value, DiscountFactorProvider):
        raise TypeError(f"{name} must provide maturity discount factors")


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
        _validate_discount_factor_provider(
            self.risk_free_discounting,
            name="risk_free_discounting",
        )
        _validate_discount_factor_provider(
            self.dividend_discounting,
            name="dividend_discounting",
        )
        if self.risk_free_discounting.valuation_date != self.valuation_date:
            raise ValueError(
                "risk-free discounting valuation date must match market environment"
            )
        if self.dividend_discounting.valuation_date != self.valuation_date:
            raise ValueError(
                "dividend discounting valuation date must match market environment"
            )
