"""Heston stochastic-volatility state, law identity, and parameter values."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import exp, isfinite

from qf_platform._validation import finite_real, nonnegative_finite_real
from qf_platform.pricing.equity import EquityState


@dataclass(frozen=True, slots=True)
class HestonEquityState(EquityState):
    """Modeled equity spot plus instantaneous variance under Heston semantics.

    The state refines ``EquityState`` so existing spot-dependent contracts can be
    reused without introducing Heston-specific contract types. ``instantaneous_variance``
    is an annualized variance quantity, not an annualized volatility.
    """

    instantaneous_variance: float

    def __post_init__(self) -> None:
        EquityState.__post_init__(self)
        object.__setattr__(
            self,
            "instantaneous_variance",
            nonnegative_finite_real(
                self.instantaneous_variance,
                name="instantaneous_variance",
            ),
        )


@dataclass(frozen=True, slots=True)
class HestonStateSpace:
    """Non-negative finite spot/variance state space for the Heston law."""

    def contains(self, value: object, /) -> bool:
        return isinstance(value, HestonEquityState)


@dataclass(frozen=True, slots=True)
class HestonParameters:
    """Immutable Heston parameters supplied under pricing-measure semantics.

    ``mean_reversion_speed`` (kappa) is strictly positive per model year.
    ``long_run_variance`` (theta) and ``volatility_of_variance`` (xi) are
    non-negative annualized variance-model quantities. ``correlation`` (rho) lies in
    ``[-1, 1]``. The risk-free accumulation rate remains owned by the pricing
    problem's numeraire rather than being duplicated here.

    The Feller condition ``2*kappa*theta >= xi^2`` is exposed as diagnostic evidence;
    it is sufficient for strict positivity of the CIR variance process but is not
    treated as a universal structural-validity requirement.
    """

    mean_reversion_speed: float
    long_run_variance: float
    volatility_of_variance: float
    correlation: float
    continuous_dividend_yield: float = 0.0

    def __post_init__(self) -> None:
        mean_reversion_speed = finite_real(
            self.mean_reversion_speed,
            name="mean_reversion_speed",
        )
        if mean_reversion_speed <= 0.0:
            msg = "mean_reversion_speed must be strictly positive"
            raise ValueError(msg)
        object.__setattr__(self, "mean_reversion_speed", mean_reversion_speed)
        object.__setattr__(
            self,
            "long_run_variance",
            nonnegative_finite_real(
                self.long_run_variance,
                name="long_run_variance",
            ),
        )
        object.__setattr__(
            self,
            "volatility_of_variance",
            nonnegative_finite_real(
                self.volatility_of_variance,
                name="volatility_of_variance",
            ),
        )
        correlation = finite_real(self.correlation, name="correlation")
        if correlation < -1.0 or correlation > 1.0:
            msg = "correlation must lie in [-1, 1]"
            raise ValueError(msg)
        object.__setattr__(self, "correlation", correlation)
        object.__setattr__(
            self,
            "continuous_dividend_yield",
            finite_real(
                self.continuous_dividend_yield,
                name="continuous_dividend_yield",
            ),
        )

    @property
    def feller_discriminant(self) -> float:
        """Return ``2*kappa*theta - xi^2`` for explicit positivity diagnostics."""

        return (
            2.0 * self.mean_reversion_speed * self.long_run_variance
            - self.volatility_of_variance * self.volatility_of_variance
        )

    @property
    def feller_condition_satisfied(self) -> bool:
        """Return whether the classical Heston/CIR Feller inequality is satisfied."""

        return self.feller_discriminant >= 0.0


def integrated_deterministic_heston_variance(
    initial_variance: float,
    parameters: HestonParameters,
    year_fraction: float,
    /,
) -> float:
    """Return integrated variance when ``xi == 0`` makes variance deterministic.

    For ``dv = kappa(theta-v) dt`` the deterministic path is
    ``v(t)=theta+(v0-theta)exp(-kappa*t)``. Its integral is the variance entering the
    terminal log-spot distribution and therefore the Black-Scholes-equivalent limit.
    """

    initial = nonnegative_finite_real(initial_variance, name="initial_variance")
    horizon = nonnegative_finite_real(year_fraction, name="year_fraction")
    kappa = parameters.mean_reversion_speed
    theta = parameters.long_run_variance
    value = theta * horizon + (initial - theta) * (1.0 - exp(-kappa * horizon)) / kappa
    if not isfinite(value) or value < 0.0:
        msg = "integrated deterministic Heston variance must be non-negative and finite"
        raise ValueError(msg)
    return value


@dataclass(frozen=True, slots=True)
class HestonLaw:
    """Risk-neutral Heston stochastic-volatility law identity.

    Under the existing money-market pricing semantics, the model is

    ``dS = (r-q) S dt + sqrt(v) S dW_S``

    ``dv = kappa(theta-v) dt + xi sqrt(v) dW_v``

    with instantaneous Brownian correlation ``rho``. The law deliberately does not
    add a universal drift/diffusion interface to the foundational stochastic-law
    protocol.
    """

    state_space: HestonStateSpace = field(default_factory=HestonStateSpace)

    def accepts_parameters(self, parameters: object, /) -> bool:
        return isinstance(parameters, HestonParameters)
