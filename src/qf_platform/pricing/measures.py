"""Numeraire and physical/pricing-measure semantics for asset pricing."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Protocol


class Numeraire[TimeT](Protocol):
    """Strictly-positive value process used to denominate financial values."""

    def value_at(self, time: TimeT, /) -> float:
        """Return the numeraire value at a supported time."""


def validated_numeraire_value[TimeT](
    numeraire: Numeraire[TimeT],
    time: TimeT,
    /,
) -> float:
    """Return a positive finite numeraire value or reject invalid semantics."""

    value = float(numeraire.value_at(time))
    if not isfinite(value) or value <= 0.0:
        msg = "numeraire value must be positive and finite"
        raise ValueError(msg)
    return value


@dataclass(frozen=True, slots=True)
class PhysicalMeasureSemantics:
    """Identity/role semantics for a physical probability measure P.

    This is not a measure-theory engine and provides no change-of-measure operation.
    """

    name: str = "P"

    def __post_init__(self) -> None:
        if not self.name.strip():
            msg = "physical-measure name must be non-empty"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class PricingMeasureSemantics[TimeT]:
    """Numeraire-associated pricing-measure semantics Q^N.

    Under these semantics, appropriately modeled traded assets denominated by
    ``numeraire`` are martingales. The object identifies that mathematical context; it
    does not mechanically transform arbitrary physical-measure dynamics into pricing
    dynamics.
    """

    name: str
    numeraire: Numeraire[TimeT]

    def __post_init__(self) -> None:
        if not self.name.strip():
            msg = "pricing-measure name must be non-empty"
            raise ValueError(msg)
