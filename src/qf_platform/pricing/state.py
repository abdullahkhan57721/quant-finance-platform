"""Modeled-state and state-path semantics for asset-pricing problems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class StateSpace[StateT](Protocol):
    """Set-like membership semantics for modeled financial states."""

    def contains(self, value: StateT, /) -> bool:
        """Return whether ``value`` belongs to this modeled state space."""


class StatePath[TimeT, StateT](Protocol):
    """A path of modeled states, without finite-dimensional/Markov assumptions."""

    def value_at(self, time: TimeT, /) -> StateT:
        """Return the modeled state at a supported time on the path."""


@dataclass(frozen=True, slots=True)
class ModeledState[TimeT, StateT]:
    """Current modeled state and the state space whose semantics it uses.

    ``value`` may itself contain path/history information when a non-Markovian model
    needs richer conditioning information. This type does not claim that the current
    value is a finite-dimensional sufficient statistic.
    """

    time: TimeT
    value: StateT
    state_space: StateSpace[StateT]

    def __post_init__(self) -> None:
        if not self.state_space.contains(self.value):
            msg = "modeled state is outside its declared state space"
            raise ValueError(msg)
