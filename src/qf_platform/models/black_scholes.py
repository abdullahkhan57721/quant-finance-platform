"""Black-Scholes model parameters."""

from dataclasses import dataclass

from qf_platform._validation import nonnegative_finite_real


@dataclass(frozen=True, slots=True)
class BlackScholesParameters:
    """Immutable Black-Scholes parameters.

    ``annualized_volatility`` is the annualized standard deviation expressed as
    a decimal. For example, ``0.20`` means 20% annualized volatility.
    """

    annualized_volatility: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "annualized_volatility",
            nonnegative_finite_real(
                self.annualized_volatility,
                name="annualized_volatility",
            ),
        )
