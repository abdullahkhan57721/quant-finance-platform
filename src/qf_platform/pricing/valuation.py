"""Valuation-method capability and immutable completed valuation results."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Protocol, TypeVar

from qf_platform.pricing.problem import PricingProblem

ParametersT = TypeVar("ParametersT")
PathT = TypeVar("PathT")
StateT = TypeVar("StateT")
TimeT = TypeVar("TimeT")


@dataclass(frozen=True, slots=True)
class ValuationResult:
    """Smallest completed valuation result: one finite present value."""

    present_value: float

    def __post_init__(self) -> None:
        present_value = float(self.present_value)
        if not isfinite(present_value):
            msg = "present value must be finite"
            raise ValueError(msg)
        object.__setattr__(self, "present_value", present_value)


class UnsupportedPricingProblem(ValueError):
    """Raised when a valuation method does not implement a pricing problem."""


class ValuationMethod(Protocol[TimeT, StateT, ParametersT, PathT]):
    """Algorithmic valuation responsibility, separate from financial-model semantics."""

    def supports(
        self,
        problem: PricingProblem[TimeT, StateT, ParametersT, PathT],
        /,
    ) -> bool:
        """Return whether this implementation supports the supplied problem."""

    def apply(
        self,
        problem: PricingProblem[TimeT, StateT, ParametersT, PathT],
        /,
    ) -> ValuationResult:
        """Evaluate a problem already known to be supported by this method."""


def evaluate(
    problem: PricingProblem[TimeT, StateT, ParametersT, PathT],
    method: ValuationMethod[TimeT, StateT, ParametersT, PathT],
    /,
) -> ValuationResult:
    """Evaluate ``problem`` only after explicit implementation-capability checking."""

    if not method.supports(problem):
        method_name = type(method).__name__
        msg = f"{method_name} does not support the supplied pricing problem"
        raise UnsupportedPricingProblem(msg)
    return method.apply(problem)
