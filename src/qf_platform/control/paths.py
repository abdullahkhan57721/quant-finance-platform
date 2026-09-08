"""Concrete exact-transition Black-Scholes path simulation for M3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import exp, isfinite, sqrt
from random import Random
from typing import cast

from qf_platform._validation import calendar_date, finite_real
from qf_platform.pricing.black_scholes import BlackScholesLaw, BlackScholesParameters
from qf_platform.pricing.dates import actual_365_fixed_year_fraction
from qf_platform.pricing.equity import EquityState, EquityStateSpace, EuropeanOption
from qf_platform.pricing.measures import (
    PricingMeasureSemantics,
    validated_numeraire_value,
)
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState

type BlackScholesPricingProblem = PricingProblem[
    date, EquityState, BlackScholesParameters
]


def _require_integer_seed(seed: object) -> int:
    if type(seed) is not int:
        msg = "seed must be an integer"
        raise TypeError(msg)
    return seed


def _strictly_increasing_dates(
    values: tuple[date, ...], *, name: str
) -> tuple[date, ...]:
    dates = tuple(calendar_date(value, name=name) for value in values)
    if not dates:
        msg = f"{name} must not be empty"
        raise ValueError(msg)
    if any(later <= earlier for earlier, later in zip(dates, dates[1:], strict=False)):
        msg = f"{name} must be strictly increasing"
        raise ValueError(msg)
    return dates


def _require_black_scholes_problem(
    problem: BlackScholesPricingProblem,
    *,
    purpose: str,
) -> tuple[EuropeanOption, FlatMoneyMarketNumeraire]:
    contract = problem.contract
    numeraire = problem.numeraire
    if not (
        isinstance(problem.current_state.state_space, EquityStateSpace)
        and isinstance(problem.stochastic_law, BlackScholesLaw)
        and isinstance(contract, EuropeanOption)
        and isinstance(numeraire, FlatMoneyMarketNumeraire)
    ):
        msg = f"{purpose} requires the concrete M1 Black-Scholes family"
        raise ValueError(msg)
    return contract, numeraire


@dataclass(frozen=True, slots=True)
class EquityPathPoint:
    """One immutable modeled equity state sampled on a simulated path."""

    time: date
    spot: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "time", calendar_date(self.time, name="path-point time")
        )
        spot = finite_real(self.spot, name="path-point spot")
        if spot <= 0.0:
            msg = "path-point spot must be positive"
            raise ValueError(msg)
        object.__setattr__(self, "spot", spot)


@dataclass(frozen=True, slots=True)
class BlackScholesPathSimulation:
    """Exact-transition GBM path configuration under explicit pricing semantics.

    Observation dates are simulation/output times, not Euler timesteps. Each adjacent
    state is sampled from the exact constant-parameter Black-Scholes transition.
    """

    initial_state: ModeledState[date, EquityState]
    stochastic_law: BlackScholesLaw
    parameters: BlackScholesParameters
    numeraire: FlatMoneyMarketNumeraire
    pricing_measure: PricingMeasureSemantics[date]
    observation_dates: tuple[date, ...]
    seed: int

    def __post_init__(self) -> None:
        if not isinstance(self.initial_state.state_space, EquityStateSpace):
            msg = "path simulation requires the concrete equity state space"
            raise ValueError(msg)
        if not self.stochastic_law.state_space.contains(self.initial_state.value):
            msg = "initial state is incompatible with the Black-Scholes law"
            raise ValueError(msg)
        if not self.stochastic_law.accepts_parameters(self.parameters):
            msg = "parameters are incompatible with the Black-Scholes law"
            raise TypeError(msg)
        if self.initial_state.value.spot <= 0.0:
            msg = "path simulation requires positive initial spot"
            raise ValueError(msg)
        if self.pricing_measure.numeraire is not self.numeraire:
            msg = "pricing measure must be associated with the path numeraire"
            raise ValueError(msg)
        validated_numeraire_value(self.numeraire, self.initial_state.time)
        dates = _strictly_increasing_dates(
            tuple(self.observation_dates),
            name="observation date",
        )
        if len(dates) < 2:
            msg = "path simulation requires at least two observation dates"
            raise ValueError(msg)
        if dates[0] != self.initial_state.time:
            msg = "first observation date must equal the initial-state time"
            raise ValueError(msg)
        object.__setattr__(self, "observation_dates", dates)
        object.__setattr__(self, "seed", _require_integer_seed(self.seed))

    @classmethod
    def from_pricing_problem(
        cls,
        problem: BlackScholesPricingProblem,
        *,
        observation_dates: tuple[date, ...],
        seed: int,
    ) -> BlackScholesPathSimulation:
        """Create path semantics from a concrete M1 Black-Scholes pricing problem."""

        _require_black_scholes_problem(problem, purpose="path simulation")
        return cls(
            initial_state=problem.current_state,
            stochastic_law=cast(BlackScholesLaw, problem.stochastic_law),
            parameters=problem.parameters,
            numeraire=cast(FlatMoneyMarketNumeraire, problem.numeraire),
            pricing_measure=problem.pricing_measure,
            observation_dates=observation_dates,
            seed=seed,
        )


@dataclass(frozen=True, slots=True)
class SimulatedEquityPath:
    """Immutable realized path plus the exact simulation semantics that generated it."""

    simulation: BlackScholesPathSimulation
    points: tuple[EquityPathPoint, ...]

    def __post_init__(self) -> None:
        points = tuple(self.points)
        if len(points) != len(self.simulation.observation_dates):
            msg = "path points must match the configured observation dates"
            raise ValueError(msg)
        for point, expected_date in zip(
            points,
            self.simulation.observation_dates,
            strict=True,
        ):
            if point.time != expected_date:
                msg = "path-point times must match configured observation dates"
                raise ValueError(msg)
        if points[0].spot != self.simulation.initial_state.value.spot:
            msg = "first path spot must equal the configured initial spot"
            raise ValueError(msg)
        object.__setattr__(self, "points", points)

    def value_at(self, time: date, /) -> EquityState:
        """Return a modeled equity state at an explicitly simulated date."""

        access_date = calendar_date(time, name="path access time")
        for point in self.points:
            if point.time == access_date:
                return EquityState(point.spot)
        msg = "requested time is not present on the simulated path"
        raise KeyError(msg)

    @property
    def seed(self) -> int:
        return self.simulation.seed


def simulate_black_scholes_path(
    simulation: BlackScholesPathSimulation,
    /,
) -> SimulatedEquityPath:
    """Sample a pricing-measure GBM path using exact adjacent-date transitions."""

    rng = Random(simulation.seed)
    rate = simulation.numeraire.continuously_compounded_rate
    parameters = simulation.parameters
    volatility = parameters.annualized_volatility
    dividend_yield = parameters.continuous_dividend_yield
    dates = simulation.observation_dates
    spot = simulation.initial_state.value.spot
    points = [EquityPathPoint(dates[0], spot)]

    for earlier, later in zip(dates, dates[1:], strict=False):
        year_fraction = actual_365_fixed_year_fraction(earlier, later)
        shock = rng.gauss(0.0, 1.0)
        exponent = (
            (rate - dividend_yield - 0.5 * volatility * volatility) * year_fraction
            + volatility * sqrt(year_fraction) * shock
        )
        try:
            spot *= exp(exponent)
        except OverflowError as exc:
            msg = "simulated spot must remain positive and finite"
            raise ValueError(msg) from exc
        if not isfinite(spot) or spot <= 0.0:
            msg = "simulated spot must remain positive and finite"
            raise ValueError(msg)
        points.append(EquityPathPoint(later, spot))

    return SimulatedEquityPath(simulation=simulation, points=tuple(points))
