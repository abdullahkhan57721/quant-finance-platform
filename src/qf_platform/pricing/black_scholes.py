"""Black-Scholes stochastic-law identity and immutable parameter values."""

from __future__ import annotations

from dataclasses import dataclass, field

from qf_platform._validation import finite_real, nonnegative_finite_real
from qf_platform.pricing.equity import EquityState, EquityStateSpace


@dataclass(frozen=True, slots=True)
class BlackScholesParameters:
    """Constant Black-Scholes parameters supplied under pricing semantics.

    ``annualized_volatility`` is a decimal annualized standard deviation:
    ``0.20`` means 20% annualized volatility.

    ``continuous_dividend_yield`` is a continuously compounded proportional
    dividend/carry rate. The risk-free accumulation rate is deliberately not
    duplicated here; M1 represents it through the pricing problem's numeraire.
    """

    annualized_volatility: float
    continuous_dividend_yield: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "annualized_volatility",
            nonnegative_finite_real(
                self.annualized_volatility,
                name="annualized_volatility",
            ),
        )
        object.__setattr__(
            self,
            "continuous_dividend_yield",
            finite_real(
                self.continuous_dividend_yield,
                name="continuous_dividend_yield",
            ),
        )


@dataclass(frozen=True, slots=True)
class BlackScholesLaw:
    """GBM/Black-Scholes equity-law identity, separate from its parameters.

    Under the money-market pricing measure used by M1, the concrete dynamics are
    the standard constant-parameter geometric Brownian motion with risk-free
    accumulation supplied by the numeraire and continuous carry supplied by
    ``BlackScholesParameters``. This law intentionally does not extend the
    foundational stochastic-law protocol with a universal drift/diffusion API.
    """

    state_space: EquityStateSpace = field(default_factory=EquityStateSpace)

    def accepts_parameters(self, parameters: BlackScholesParameters, /) -> bool:
        return isinstance(parameters, BlackScholesParameters)
