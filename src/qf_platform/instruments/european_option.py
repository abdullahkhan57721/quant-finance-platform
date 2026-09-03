"""European-option contract semantics."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from qf_platform._validation import nonnegative_finite_real


class OptionRight(StrEnum):
    """Exercise right of a European option."""

    CALL = "call"
    PUT = "put"


def _validate_option_right(value: object) -> None:
    if not isinstance(value, OptionRight):
        raise TypeError("right must be an OptionRight")


@dataclass(frozen=True, slots=True)
class EuropeanOption:
    """Immutable European option contract.

    The contract stores a calendar expiry date only. Business-day adjustment and
    time-of-day expiry semantics are deliberately outside M1.
    """

    expiry: date
    strike: float
    right: OptionRight

    def __post_init__(self) -> None:
        if type(self.expiry) is not date:
            raise TypeError("expiry must be a datetime.date")
        object.__setattr__(
            self,
            "strike",
            nonnegative_finite_real(self.strike, name="strike"),
        )
        _validate_option_right(self.right)
